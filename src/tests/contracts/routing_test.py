"""Contract: routing is exact, api paths work, handlers may shape responses."""

import unittest

import ft3

from . import cfg


class Constants(cfg.Constants):
	"""Constant values specific to unit tests in this file."""

	TEMPLATE = f'{cfg.Constants.PACKAGE}.template'
	VERSION = ft3.api.cfg.Constants.DEFAULT_VERSION


class Ping(ft3.Object):
	"""A resource whose handler shapes its own response."""

	ping_id: ft3.Field[str] = 'p'


@Ping.GET
def pings(request: ft3.api.Request) -> list[Ping]:
	"""Return a handler-shaped response."""

	return ft3.api.Response(  # type: ignore[return-value]
		status_code=304, headers={'ETag': 'abc', 'X-Custom': 'yes'}
	)


class Built(unittest.TestCase):
	"""Builds an API from the template package in a clean route cache."""

	api_path = '/'
	include_version_prefix = True

	@classmethod
	def setUpClass(cls) -> None:
		cls._paths = list(ft3.api.events.utl.PATHS)
		ft3.api.events.utl.PATHS.clear()
		cls.api = ft3.api.api_from_package(
			Constants.TEMPLATE,
			Constants.VERSION,
			cls.api_path,
			include_version_prefix=cls.include_version_prefix,
		)
		cls.handler = ft3.api.Handler(api=cls.api)
		return super().setUpClass()

	@classmethod
	def tearDownClass(cls) -> None:
		ft3.api.events.utl.PATHS.clear()
		ft3.api.events.utl.PATHS.extend(cls._paths)
		return super().tearDownClass()

	def get(self, path: str) -> ft3.api.Response:
		return self.handler(ft3.api.Request(url=path, path=path, method='get'))


class TestExactRouting(Built):
	"""A route never matches by prefix."""

	def test_01_prefix_does_not_match(self):
		self.assertEqual(self.get('/v1/healthzFOO').status_code, 404)
		self.assertEqual(self.get('/v1/healthz/extra').status_code, 404)

	def test_02_exact_and_trailing_slash_match(self):
		self.assertEqual(self.get('/v1/healthz').status_code, 200)
		self.assertEqual(self.get('/v1/healthz/').status_code, 200)

	def test_03_not_found_carries_ref(self):
		body = self.get('/v1/nothing').body
		self.assertEqual(body['errorRef'], 'resource_not_found_error')


class TestApiPathWithPrefix(Built):
	"""`--api-path /api` with a version prefix routes under /api/v1."""

	api_path = '/api'

	def test_01_routes(self):
		self.assertEqual(self.get('/api/v1/healthz').status_code, 200)
		self.assertEqual(self.get('/v1/healthz').status_code, 404)
		self.assertEqual(self.api.servers[0].url, '/api/{version}')


class TestApiPathWithoutPrefix(Built):
	"""`--api-path /api` without a version prefix routes under /api."""

	api_path = '/api'
	include_version_prefix = False

	def test_01_routes(self):
		self.assertEqual(self.get('/api/healthz').status_code, 200)
		self.assertEqual(self.get('/healthz').status_code, 404)
		self.assertEqual(self.api.servers[0].url, '/api')


class TestHandlerResponse(Built):
	"""A handler may return `Response` to set status and headers."""

	@classmethod
	def setUpClass(cls) -> None:
		ft3.Api.register(Ping)
		return super().setUpClass()

	@classmethod
	def tearDownClass(cls) -> None:
		ft3.api.OBJECTS.pop('Ping', None)
		return super().tearDownClass()

	def test_01_status_and_headers_are_honoured(self):
		response = self.get('/v1/pings')
		self.assertEqual(response.status_code, 304)
		self.assertEqual(response.headers['ETag'], 'abc')
		self.assertEqual(response.headers['X-Custom'], 'yes')
		self.assertEqual(response.body, '')


class TestUnregisteredHandlers(unittest.TestCase):
	"""Handlers on an unregistered class are reported at build time."""

	def test_01_warns_with_fix(self):
		class Orphan(ft3.Object):
			orphan_id: ft3.Field[str] = 'o'

		@Orphan.GET
		def orphans(request: ft3.api.Request) -> list[Orphan]:
			return []  # pragma: no cover

		paths = list(ft3.api.events.utl.PATHS)
		with self.assertLogs(ft3.log, level='WARNING') as logs:
			ft3.api.api_from_package(
				Constants.TEMPLATE, Constants.VERSION, '/'
			)
		ft3.api.events.utl.PATHS.clear()
		ft3.api.events.utl.PATHS.extend(paths)
		self.assertTrue(any('Orphan' in line for line in logs.output))
		self.assertTrue(any('Api.register' in line for line in logs.output))
