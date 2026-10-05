"""Contract: build-time tooling and the in-process client."""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

import ft3

from ft3.core import lib

from . import cfg


class Constants(cfg.Constants):
	"""Constant values specific to unit tests in this file."""

	TEMPLATE = f'{cfg.Constants.PACKAGE}.template'
	VERSION = ft3.api.cfg.Constants.DEFAULT_VERSION


class Widget(ft3.Object):
	"""Carries every Field shape `ft3 check` reports on."""

	widget_id: ft3.Field[str] = 'w'
	_hidden: ft3.Field[str] = 'h'
	costs: ft3.Field[dict] = {}
	slots: ft3.Field[list[lib.t.Optional[str]]] = []
	kind: ft3.Field[str] = ft3.Field(default='a', enum=['a', 'b'])


def run_cli(*argv: str) -> tuple[int, str]:
	"""Run `ft3 ...` in-process, returning exit code and stdout."""

	out = io.StringIO()
	original = sys.argv
	sys.argv = ['ft3', *argv]
	try:
		with contextlib.redirect_stdout(out):
			ft3.cli.main()
	except SystemExit as exit_:
		code = int(exit_.code or 0)
	else:
		code = 0
	finally:
		sys.argv = original
	return code, out.getvalue()


def drop_handled(suffix: str) -> None:
	handled = ft3.objects.objs.obj.Constants.HANDLED
	for key in [k for k in handled if k.endswith(suffix)]:
		handled.pop(key)


class TestClient(unittest.TestCase):
	"""`ft3.api.Client` drives an API in-process."""

	@classmethod
	def setUpClass(cls) -> None:
		cls.api = ft3.api.api_from_package(
			Constants.TEMPLATE,
			Constants.VERSION,
			'/',
			include_version_prefix=True,
		)
		cls.client = ft3.api.Client(cls.api)
		return super().setUpClass()

	@classmethod
	def tearDownClass(cls) -> None:
		return super().tearDownClass()

	def test_01_get(self):
		self.assertEqual(self.client.get('/v1/healthz').status_code, 200)

	def test_02_query_and_body(self):
		listed = self.client.get('/v1/petWithPets', query={'type': 'dog'})
		self.assertEqual(listed.status_code, 200)
		created = self.client.post(
			'/v1/petWithPets', body={'name': 'Rex', 'type': 'dog'}
		)
		self.assertEqual(created.status_code, 201)
		path = '/v1/petWithPets/' + created.body['id']
		self.assertEqual(
			self.client.patch(path, query={'name': 'Max'}).body['name'], 'Max'
		)
		self.assertEqual(
			self.client.put(
				path, body={'name': 'Rex', 'type': 'dog'}
			).status_code,
			200,
		)
		self.assertEqual(
			self.client.options('/v1/petWithPets').status_code, 204
		)
		self.assertEqual(self.client.delete(path).status_code, 204)

	def test_03_openapi_document(self):
		document = ft3.api.openapi_document(self.api)
		self.assertEqual(document['openapi'], ft3.api.cfg.Constants.VERSION)
		self.assertIn('/petWithPets', document['paths'])


class TestCheck(unittest.TestCase):
	"""`ft3 check` validates a package and reports the migration list."""

	@classmethod
	def setUpClass(cls) -> None:
		ft3.Api.register(Widget)

		@Widget.GET
		def widgets(request: ft3.api.Request) -> list[Widget]:
			return []  # pragma: no cover

		return super().setUpClass()

	@classmethod
	def tearDownClass(cls) -> None:
		ft3.api.OBJECTS.pop('Widget', None)
		drop_handled('.Widget')
		return super().tearDownClass()

	def notices(self, report, object_name):
		return {
			(n['field'], n['notice'])
			for n in report['notices']
			if n['object'] == object_name
		}

	def test_01_report(self):
		report = ft3.api.check_package(
			Constants.TEMPLATE, include_version_prefix=True
		)
		self.assertTrue(report['ok'], report['errors'])
		routes = {r['path']: r for r in report['routes']}
		self.assertIn('post', routes['/v1/petWithPets']['methods'])
		self.assertEqual(routes['/v1/petWithPets']['resource'], 'PetWithPet')
		self.assertIn(
			('pet_with_pet_id', 'required_field'), self.notices(report, 'Pet')
		)
		self.assertIn(
			('type_', 'constraints_enforced'),
			self.notices(report, 'PetWithPet'),
		)
		self.assertEqual(
			self.notices(report, 'Widget'),
			{
				('_hidden', 'private_field'),
				('costs', 'dict_keys_default'),
				('slots', 'list_nulls_default'),
				('kind', 'constraints_enforced'),
			},
		)
		self.assertNotIn(ft3.api.cfg.Constants.SWAGGER_PATH, ft3.api.FILES)

	def test_02_build_failure(self):
		report = ft3.api.check_package(f'{Constants.PACKAGE}.does_not_exist')
		self.assertFalse(report['ok'])
		self.assertEqual(report['errors'][0]['code'], 'build_failed')
		self.assertEqual(report['errors'][0]['ref'], 'module_not_found_error')

	def test_03_unregistered_handlers(self):
		class Orphan(ft3.Object):
			orphan_id: ft3.Field[str] = 'o'

		@Orphan.GET
		def orphans(request: ft3.api.Request) -> list[Orphan]:
			return []  # pragma: no cover

		try:
			report = ft3.api.check_package(Constants.TEMPLATE)
		finally:
			drop_handled('.Orphan')
		self.assertFalse(report['ok'])
		self.assertEqual(report['errors'][0]['code'], 'unregistered_handlers')
		self.assertIn('Orphan', report['errors'][0]['object'])

	def test_04_openapi_from_package(self):
		document = ft3.api.openapi_from_package(Constants.TEMPLATE)
		self.assertIn('/petWithPets', document['paths'])
		self.assertNotIn(ft3.api.cfg.Constants.SWAGGER_PATH, ft3.api.FILES)


class TestCli(unittest.TestCase):
	"""`ft3 check` and `ft3 openapi` from the command line."""

	def test_01_check_json(self):
		code, out = run_cli(
			'check', Constants.TEMPLATE, '--include-version-prefix'
		)
		self.assertEqual(code, 0)
		self.assertTrue(json.loads(out)['ok'])

	def test_02_check_text(self):
		code, out = run_cli('check', Constants.TEMPLATE, '--format', 'text')
		self.assertEqual(code, 0)
		self.assertTrue(out.startswith(f'{Constants.TEMPLATE}: ok'))
		self.assertIn('route /petWithPets', out)
		self.assertIn('notice Pet.pet_with_pet_id required_field', out)

	def test_03_check_failure_exits_1(self):
		code, out = run_cli('check', 'ft3.nope', '--format', 'text')
		self.assertEqual(code, 1)
		self.assertIn('error build_failed', out)
		code, out = run_cli('check', 'ft3.nope')
		self.assertEqual(code, 1)
		self.assertFalse(json.loads(out)['ok'])

	def test_04_openapi_stdout_and_file(self):
		code, out = run_cli('openapi', Constants.TEMPLATE, '-o', '-')
		self.assertEqual(code, 0)
		self.assertEqual(
			json.loads(out)['openapi'], ft3.api.cfg.Constants.VERSION
		)
		with tempfile.TemporaryDirectory() as directory:
			target = os.path.join(directory, 'openapi.json')
			code, out = run_cli(
				'openapi', Constants.TEMPLATE, '--output', target
			)
			self.assertEqual(code, 0)
			self.assertIn('wrote', out)
			with open(target) as file:
				self.assertIn('/petWithPets', json.load(file)['paths'])

	def test_05_parsers(self):
		args = ft3.cli.obj.root_parser.parse_args(['check', 'x'])
		self.assertIs(args.func, ft3.api.utl.check)
		args = ft3.cli.obj.root_parser.parse_args(['openapi', 'x'])
		self.assertIs(args.func, ft3.api.utl.openapi)
