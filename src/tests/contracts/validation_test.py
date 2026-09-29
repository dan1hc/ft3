"""Contract: declared constraints are enforced in strict mode."""

import enum
import unittest

import ft3

from ft3.core import lib

from . import cfg


class Constants(cfg.Constants):
	"""Constant values specific to unit tests in this file."""


class Kind(enum.Enum):
	"""Enum-class constraint."""

	cat = 'cat'
	dog = 'dog'


class Constrained(ft3.Object):
	"""Lenient by default: exactly 1.x hydrate behavior."""

	kind: ft3.Field[str] = ft3.Field(default='dog', enum=Kind)
	mood: ft3.Field[str] = ft3.Field(default='calm', enum=['calm', 'wild'])
	count: ft3.Field[int] = ft3.Field(default=1, minimum=0, maximum=10)
	step: ft3.Field[int] = ft3.Field(default=5, multiple_of=5)
	code: ft3.Field[str] = ft3.Field(
		default='ab-1', pattern=r'^[a-z]+-\d$', min_length=3, max_length=8
	)
	tags: ft3.Field[list[str]] = ft3.Field(
		default=lambda: ['a'], min_items=1, max_items=3, unique_items=True
	)
	flag: ft3.Field[bool] = True
	anything: ft3.Field[lib.t.Any] = None
	optional_count: ft3.Field[lib.t.Optional[int]] = ft3.Field(
		default=None, maximum=3
	)
	required_count: ft3.Field[int]


class Strict(Constrained, strict=True):
	"""Opts in to strict construction and assignment."""


class Inherited(Strict):
	"""Inherits strictness without restating it."""


class TestStrictParse(unittest.TestCase):
	"""`Field.parse(strict=True)` enforces every declared constraint."""

	def assertViolation(self, field, value, constraint):
		with self.assertRaises(
			ft3.objects.exc.ConstraintViolationError
		) as ctx:
			field.parse(value, strict=True)
		self.assertEqual(ctx.exception.constraint, constraint)
		self.assertEqual(ctx.exception.field, field.name)
		self.assertIn(constraint, ctx.exception.args[0])
		self.assertEqual(ctx.exception.code, 'constraint_violation_error')

	def test_01_enum_class(self):
		self.assertViolation(Constrained.kind, 'turtle', 'enum')
		self.assertEqual(Constrained.kind.parse('cat', strict=True), 'cat')

	def test_02_enum_iterable(self):
		self.assertViolation(Constrained.mood, 'angry', 'enum')

	def test_03_minimum_maximum(self):
		self.assertViolation(Constrained.count, -1, 'minimum')
		self.assertViolation(Constrained.count, 11, 'maximum')
		self.assertEqual(Constrained.count.parse(10, strict=True), 10)

	def test_04_multiple_of(self):
		self.assertViolation(Constrained.step, 7, 'multiple_of')

	def test_05_string_constraints(self):
		self.assertViolation(Constrained.code, 'ab', 'min_length')
		self.assertViolation(Constrained.code, 'abcdefgh-1', 'max_length')
		self.assertViolation(Constrained.code, 'AB-1', 'pattern')

	def test_06_array_constraints(self):
		self.assertViolation(Constrained.tags, [], 'min_items')
		self.assertViolation(Constrained.tags, list('abcd'), 'max_items')
		self.assertViolation(Constrained.tags, ['a', 'a'], 'unique_items')

	def test_07_lossless_coercion(self):
		"""'3' -> 3 is fine; 3.9 -> 3 and True -> 1 are not."""

		self.assertEqual(Constrained.count.parse('3', strict=True), 3)
		self.assertViolation(Constrained.count, 3.9, 'lossless')
		self.assertViolation(Constrained.count, True, 'lossless')
		self.assertIs(Constrained.flag.parse(True, strict=True), True)
		self.assertEqual(Constrained.anything.parse(3.9, strict=True), 3.9)

	def test_08_none_skips_constraints(self):
		self.assertIsNone(Constrained.optional_count.parse(None, strict=True))

	def test_09_type_errors_still_raise(self):
		self.assertRaises(
			ft3.objects.exc.TypeValidationError,
			lambda: Constrained.count.parse('abc', False, strict=True),
		)


class TestLenientParse(unittest.TestCase):
	"""Without strict, parsing keeps 1.x behavior and warns once."""

	def setUp(self) -> None:
		ft3.objects.fields.obj.Constants.WARNED.clear()
		return super().setUp()

	def test_01_violations_are_kept(self):
		self.assertEqual(Constrained.count.parse(99), 99)
		self.assertEqual(Constrained.count.parse(3.9), 3)

	def test_02_warns_once_per_field_and_constraint(self):
		with self.assertLogs(ft3.log, level='WARNING') as logs:
			Constrained.count.parse(99)
			Constrained.count.parse(98)
			Constrained.count.parse(-1)
		self.assertEqual(len(logs.records), 2)
		self.assertIn('was kept', logs.output[0])

	def test_03_required_invalid_value_becomes_none_with_warning(self):
		with self.assertLogs(ft3.log, level='WARNING') as logs:
			obj = Constrained(required_count='abc')
		self.assertIsNone(obj.required_count)
		self.assertIn('became None', logs.output[0])

	def test_04_violations_lists_everything(self):
		self.assertEqual(
			[
				c
				for c, _, _ in Constrained.tags.violations(
					['a', 'a', 'b', 'c']
				)
			],
			['max_items', 'unique_items'],
		)
		self.assertEqual(
			Constrained.count.constraints, {'minimum': 0, 'maximum': 10}
		)


class TestStrictObjects(unittest.TestCase):
	"""`class X(Object, strict=True)` enforces constraints on assignment."""

	def test_01_flag_is_set_and_inherited(self):
		self.assertFalse(Constrained.__strict__)
		self.assertTrue(Strict.__strict__)
		self.assertTrue(Inherited.__strict__)

	def test_02_construction_raises(self):
		self.assertRaises(
			ft3.objects.exc.ConstraintViolationError,
			lambda: Strict(required_count=1, count=99),
		)
		self.assertEqual(Strict(required_count=1, count=9).count, 9)

	def test_03_assignment_raises(self):
		obj = Inherited(required_count=1)
		with self.assertRaises(ft3.objects.exc.ConstraintViolationError):
			obj.kind = 'turtle'

	def test_04_required_invalid_value_raises(self):
		self.assertRaises(
			ft3.objects.exc.TypeValidationError,
			lambda: Strict(required_count='abc'),
		)

	def test_05_lenient_class_accepts_same_values(self):
		obj = Constrained(required_count=1, count=99, kind='turtle')
		self.assertEqual((obj.count, obj.kind), (99, 'turtle'))

	def test_06_strict_is_reserved(self):
		def _define():
			class Bad(ft3.Object):
				__strict__: ft3.Field[bool] = True

		self.assertRaises(ft3.objects.exc.ReservedKeywordError, _define)
