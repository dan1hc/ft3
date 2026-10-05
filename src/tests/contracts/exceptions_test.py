"""Contract: ft3 exceptions are catchable and carry stable codes."""

import json
import pickle
import re
import unittest

import ft3

from .. import mocking

from . import cfg


class Constants(cfg.Constants):
	"""Constant values specific to unit tests in this file."""

	EXCEPTION_MODULES = (
		ft3.core.exc,
		ft3.core.strings.exc,
		ft3.objects.exc,
		ft3.loggers.exc,
		ft3.api.events.exc,
	)


def package_exceptions() -> dict[str, type[ft3.core.exc.BasePackageException]]:
	"""Every exported ft3 exception class, keyed by name."""

	found: dict[str, type[ft3.core.exc.BasePackageException]] = {}
	for module in Constants.EXCEPTION_MODULES:
		for name in module.__all__:
			exc = getattr(module, name)
			if isinstance(exc, type) and issubclass(
				exc, ft3.core.exc.BasePackageException
			):
				found[name] = exc
	return found


class TestExceptionHierarchy(unittest.TestCase):
	"""Every ft3 exception is an ordinary Exception."""

	def setUp(self) -> None:
		self.exceptions = package_exceptions()
		return super().setUp()

	def test_01_all_subclass_exception(self):
		"""No ft3 error escapes an `except Exception` handler."""

		self.assertGreater(len(self.exceptions), 10)
		for name, exc in self.exceptions.items():
			with self.subTest(exception=name):
				self.assertTrue(issubclass(exc, Exception))

	def test_02_validation_error_is_caught_by_except_exception(self):
		"""A parse failure is recoverable with a generic handler."""

		caught: Exception | None = None
		try:
			mocking.TripDeriv.non_nullable_field.parse(None)
		except Exception as exception:
			caught = exception
		self.assertIsInstance(caught, ft3.objects.exc.TypeValidationError)


class TestExceptionCodes(unittest.TestCase):
	"""Every ft3 exception carries a stable, machine-readable code."""

	def setUp(self) -> None:
		self.exceptions = package_exceptions()
		return super().setUp()

	def test_01_codes_are_snake_case(self):
		"""Codes are identifiers, safe for logs and error bodies."""

		for name, exc in self.exceptions.items():
			with self.subTest(exception=name):
				self.assertRegex(exc.code, Constants.CODE_PATTERN)

	def test_02_codes_are_unique(self):
		"""No two exception classes share a code."""

		codes = [exc.code for exc in self.exceptions.values()]
		self.assertEqual(len(codes), len(set(codes)))

	def test_03_code_derives_from_class_name(self):
		"""The default code is the snake_case class name."""

		self.assertEqual(
			ft3.objects.exc.TypeValidationError.code,
			'type_validation_error',
		)
		self.assertEqual(
			ft3.objects.exc.ReservedKeywordError.code,
			'reserved_keyword_error',
		)

	def test_04_explicit_code_is_kept(self):
		"""A subclass may pin its own code."""

		class CustomError(ft3.core.exc.BasePackageException[str]):
			code = 'custom_error_code'

		class DerivedError(CustomError):
			"""Derived without an explicit code."""

		self.assertEqual(CustomError.code, 'custom_error_code')
		self.assertEqual(DerivedError.code, 'derived_error')

	def test_05_code_for_keeps_acronyms_whole(self):
		"""Non-ft3 exceptions get a readable snake_case code too."""

		self.assertEqual(
			ft3.core.exc.code_for(json.JSONDecodeError), 'json_decode_error'
		)
		self.assertEqual(
			ft3.core.exc.code_for(ft3.api.events.exc.HTTPError), 'http_error'
		)
		self.assertEqual(ft3.core.exc.code_for(KeyError), 'key_error')
		self.assertEqual(
			ft3.core.exc.code_for(ft3.objects.exc.TypeValidationError),
			'type_validation_error',
		)

	def test_06_code_survives_pickling(self):
		"""Code and args round-trip through pickle."""

		error_ref = list(ft3.core.codecs.enm.ParseErrorRef)[0]
		exc = ft3.objects.exc.TypeValidationError('field', int, error_ref)
		reloaded = pickle.loads(pickle.dumps(exc))
		self.assertEqual(reloaded.code, exc.code)
		self.assertTupleEqual(reloaded.args, exc.args)
		self.assertTrue(re.match(Constants.CODE_PATTERN, reloaded.code))
