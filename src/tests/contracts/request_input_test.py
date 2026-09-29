"""Contract: generated request parsing is strict unless FT3_LEGACY_WIRE."""

import json
import unittest

import ft3

from ft3 import template

from . import cfg


class Constants(cfg.Constants):
	"""Constant values specific to unit tests in this file."""

	API_PATH = ft3.api.cfg.Constants.API_PATH
	DEFAULT_VERSION = ft3.api.cfg.Constants.DEFAULT_VERSION
	PATH_ROOT = API_PATH + DEFAULT_VERSION
	COLLECTION = PATH_ROOT + '/petWithPets'


class Inputs(ft3.Object):
	"""Exercises the private, read_only, and required input rules."""

	_secret: ft3.Field[str] = 'hidden'
	stored: ft3.Field[str] = ft3.Field(default='s', read_only=True)
	name: ft3.Field[str]


def legacy(value: bool) -> None:
	ft3.core.cfg.Constants.LEGACY_WIRE = value


class TestErrorMapping(unittest.TestCase):
	"""HTTP codes follow the exception MRO and carry a stable ref."""

	def test_01_subclass_inherits_parent_status(self):
		error = ft3.api.events.obj.Error.from_exception(
			template.pkg.exc.CustomExampleError
		)
		self.assertEqual(error.error_code, 400)
		self.assertEqual(error.error_ref, 'custom_example_error')

	def test_02_framework_errors_map(self):
		exc = ft3.api.events.exc
		codes = {
			exc.ResourceNotFoundError: 404,
			exc.MethodNotImplementedError: 501,
			ft3.objects.exc.ConstraintViolationError: 400,
			ft3.objects.exc.MissingRequiredFieldError: 400,
			json.JSONDecodeError: 400,
			KeyError: 500,
		}
		for tp, code in codes.items():
			with self.subTest(exception=tp.__name__):
				self.assertEqual(
					ft3.api.events.obj.Error.from_exception(tp).error_code,
					code,
				)

	def test_03_instance_message_and_ft3_code(self):
		exc = ft3.objects.exc.MissingRequiredFieldError('Pet', 'name')
		error = ft3.api.events.obj.Error.from_exception(exc)
		self.assertEqual(error.error_ref, 'missing_required_field_error')
		self.assertIn("'name'", error.error_message)

	def test_04_request_exception_fallback_is_400(self):
		error = ft3.api.events.obj.Error.from_request_exception(
			ValueError('bad value')
		)
		self.assertEqual(
			(error.error_code, error.error_message, error.error_ref),
			(400, 'bad value', 'value_error'),
		)
		empty = ft3.api.events.obj.Error.from_request_exception(ValueError())
		self.assertEqual(empty.error_code, 400)
		self.assertTrue(empty.error_message)


class TestInputPolicy(unittest.TestCase):
	"""`Request.validate_input` applies the private/read_only/required rules."""

	def setUp(self) -> None:
		ft3.loggers.utl.Constants.WARNED.clear()
		legacy(False)
		return super().setUp()

	def tearDown(self) -> None:
		legacy(False)
		return super().tearDown()

	def request(self, method, body=None, query=None):
		return ft3.api.Request(
			url='/inputs',
			path='/inputs',
			method=method,
			body=body,
			query_params=query or {},
		)

	def test_01_private_field_is_rejected(self):
		request = self.request('post', {'secret': 'x', 'name': 'n'})
		with self.assertRaises(ft3.api.events.exc.RequestError) as ctx:
			request.validate_input(Inputs, 'post')
		self.assertIn('private', str(ctx.exception))

	def test_02_private_field_accepted_with_warning_under_legacy(self):
		legacy(True)
		request = self.request('post', {'secret': 'x', 'name': 'n'})
		with self.assertLogs(ft3.log, level='WARNING') as logs:
			request.validate_input(Inputs, 'post')
			request.validate_input(Inputs, 'post')
		self.assertEqual(len(logs.records), 1)
		self.assertEqual(request.body['secret'], 'x')

	def test_03_read_only_is_dropped_with_warning(self):
		request = self.request('put', {'stored': 'x', 'name': 'n'})
		with self.assertLogs(ft3.log, level='WARNING'):
			request.validate_input(Inputs, 'put')
		self.assertNotIn('stored', request.body)
		self.assertEqual(request.body['name'], 'n')

	def test_04_required_missing_is_rejected_on_post_and_put(self):
		for method in ('post', 'put'):
			with self.subTest(method=method):
				request = self.request(method, {'stored': 'x'})
				self.assertRaises(
					ft3.objects.exc.MissingRequiredFieldError,
					lambda: request.validate_input(Inputs, method),
				)
		null = self.request('post', {'name': None})
		self.assertRaises(
			ft3.objects.exc.MissingRequiredFieldError,
			lambda: null.validate_input(Inputs, 'post'),
		)

	def test_05_required_not_checked_on_patch_or_query(self):
		self.request('patch', {'stored': 'x'}).validate_input(Inputs, 'patch')
		self.request('get', query={'name': 'n'}).validate_input(Inputs, 'get')

	def test_06_required_missing_warns_under_legacy(self):
		legacy(True)
		request = self.request('post', {})
		with self.assertLogs(ft3.log, level='WARNING') as logs:
			request.validate_input(Inputs, 'post')
		self.assertIn('missing_required', logs.output[0])

	def test_07_list_bodies_and_unknown_keys(self):
		request = self.request('post', [{'name': 'a', 'bogus': 1}, 'skip'])
		request.validate_input(Inputs, 'post')
		self.assertEqual(request.body[0]['bogus'], 1)


class TestStrictRequests(unittest.TestCase):
	"""End to end through the template API."""

	@classmethod
	def setUpClass(cls) -> None:
		cls.api = ft3.api.api_from_package(
			f'{Constants.PACKAGE}.template',
			Constants.DEFAULT_VERSION,
			Constants.API_PATH,
			include_version_prefix=True,
		)
		cls.handler = ft3.api.Handler(api=cls.api)
		return super().setUpClass()

	@classmethod
	def tearDownClass(cls) -> None:
		legacy(False)
		return super().tearDownClass()

	def setUp(self) -> None:
		legacy(False)
		return super().setUp()

	def post(self, body):
		return self.handler(
			ft3.api.Request(
				url=Constants.COLLECTION,
				path=Constants.COLLECTION,
				method='post',
				body=body,
			)
		)

	def test_01_enum_violation_is_400(self):
		response = self.post({'name': 'Rex', 'type': 'turtle'})
		self.assertEqual(response.status_code, 400)
		self.assertEqual(
			response.body['errorRef'], 'constraint_violation_error'
		)
		self.assertIn('enum', response.body['errorMessage'])

	def test_02_missing_required_is_400(self):
		response = self.post({'type': 'dog'})
		self.assertEqual(response.status_code, 400)
		self.assertEqual(
			response.body['errorRef'], 'missing_required_field_error'
		)

	def test_03_malformed_json_is_400_before_dispatch(self):
		response = self.post('{bad')
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.body['errorRef'], 'json_decode_error')

	def test_04_read_only_id_is_dropped(self):
		response = self.post({'name': 'Rex', 'type': 'dog', 'id': 'forced'})
		self.assertEqual(response.status_code, 201)
		self.assertNotEqual(response.body['id'], 'forced')

	def test_05_query_constraint_is_400(self):
		url = Constants.COLLECTION + '?type=turtle'
		response = self.handler(
			ft3.api.Request(url=url, path=Constants.COLLECTION, method='get')
		)
		self.assertEqual(response.status_code, 400)

	def test_06_legacy_keeps_1x_dispatch(self):
		legacy(True)
		accepted = self.post({'name': 'Rex', 'type': 'turtle'})
		self.assertEqual(accepted.status_code, 201)
		self.assertEqual(accepted.body['type'], 'turtle')
		malformed = self.post('{bad')
		self.assertEqual(malformed.status_code, 400)
		self.assertEqual(malformed.body['errorRef'], 'syntax_error')
