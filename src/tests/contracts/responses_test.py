"""Contract: responses document their bodies and carry their own headers."""

import unittest

import ft3

from . import cfg


class Constants(cfg.Constants):
	"""Constant values specific to unit tests in this file."""

	TEMPLATE = f'{cfg.Constants.PACKAGE}.template'
	VERSION = ft3.api.cfg.Constants.DEFAULT_VERSION
	ACCENTED = 'héllo wörld'


class Greeting(ft3.Object):
	"""A resource whose handler answers in plain text."""

	greeting_id: ft3.Field[str] = 'g'


@Greeting.GET
def greetings(request: ft3.api.Request) -> list[Greeting]:
	"""Answer with a non-ASCII text body."""

	return ft3.api.Response(  # type: ignore[return-value]
		status_code=200, headers={}, body=Constants.ACCENTED
	)


class Built(unittest.TestCase):
	"""Builds an API from the template package."""

	lazy_docs = True

	@classmethod
	def setUpClass(cls) -> None:
		cls.api = ft3.api.api_from_package(
			Constants.TEMPLATE,
			Constants.VERSION,
			'/',
			include_version_prefix=True,
			lazy_docs=cls.lazy_docs,
		)
		cls.handler = ft3.api.Handler(api=cls.api)
		return super().setUpClass()

	def call(
		self, method: str, path: str, headers: dict[str, str] | None = None
	) -> ft3.api.Response:
		return self.handler(
			ft3.api.Request(
				url=path, path=path, method=method, headers=headers or {}
			)
		)


class TestByIdResponsesAreDocumented(Built):
	"""A handler keyed by id documents the body it returns."""

	lazy_docs = False

	def assert_documented(self, uri: str, method: str, code: str) -> None:
		response = self.api.paths[uri][method].responses[code]
		self.assertEqual(response.description, 'Success response.')
		self.assertIn(
			ft3.api.enm.ContentType.json.value, response.content or {}
		)

	def test_01_put_and_patch_by_id(self):
		for method in ('put', 'patch'):
			self.assert_documented(
				'/petWithPets/{petWithPetId}', method, '200'
			)

	def test_02_nested_by_id(self):
		uri = '/petWithPets/{petWithPetId}/pets/{petId}'
		for method in ('get', 'put', 'patch'):
			self.assert_documented(uri, method, '200')

	def test_03_nested_post(self):
		self.assert_documented(
			'/petWithPets/{petWithPetId}/pets', 'post', '201'
		)

	def test_04_list_get_is_unchanged(self):
		self.assert_documented('/petWithPets', 'get', '200')

	def test_05_delete_stays_empty(self):
		response = self.api.paths['/petWithPets/{petWithPetId}'][
			'delete'
		].responses['204']
		self.assertEqual(response.description, 'Empty response.')


class TestComputedHeadersAreNotEchoed(Built):
	"""Request headers never overwrite the headers ft3 computes."""

	def test_01_content_length_is_the_bodys_own(self):
		response = self.call(
			'get',
			'/v1/healthz',
			{'Content-Length': '2', 'Content-Type': 'text/plain'},
		)
		size = len(response.serialize().encode())
		self.assertEqual(int(response.headers['Content-Length']), size)
		self.assertEqual(
			response.headers['Content-Type'],
			ft3.api.enm.ContentType.json.value,
		)

	def test_02_date_is_the_responses_own(self):
		response = self.call('get', '/v1/healthz', {'Date': 'yesterday'})
		self.assertNotEqual(response.headers['Date'], 'yesterday')


class TestContentLengthCountsBytes(Built):
	"""A text body's length is its UTF-8 byte count."""

	@classmethod
	def setUpClass(cls) -> None:
		ft3.Api.register(Greeting)
		return super().setUpClass()

	@classmethod
	def tearDownClass(cls) -> None:
		ft3.api.OBJECTS.pop('Greeting', None)
		handled = ft3.objects.objs.obj.Constants.HANDLED
		for key in [k for k in handled if k.endswith('.Greeting')]:
			handled.pop(key)
		return super().tearDownClass()

	def test_01_non_ascii_text(self):
		response = self.call('get', '/v1/greetings')
		self.assertEqual(response.body, Constants.ACCENTED)
		self.assertEqual(
			int(response.headers['Content-Length']),
			len(Constants.ACCENTED.encode()),
		)
