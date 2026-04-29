import importlib.util
import os
import sys
import tempfile
import textwrap
import typing
import types
import unittest
from unittest import mock

import ft3

from ... import mocking

from . import cfg


class Constants(cfg.Constants):
	"""Constant values specific to unit tests in this file."""


class TestMeta(unittest.TestCase):
	"""Fixture for testing Meta."""

	def setUp(self) -> None:
		self.mcs = ft3.objects.metas.Meta
		self.cls = mocking.Derivative
		self.field = ft3.Field(
			name='str_field',
			default='value',
			type_=str,
		)
		return super().setUp()

	def _load_module_from_source(self, source_file: str) -> types.ModuleType:
		module_name = f'_ft3_attribute_docs_test_{id(self)}'
		spec = importlib.util.spec_from_file_location(module_name, source_file)
		if spec is None or spec.loader is None:  # pragma: no cover
			raise RuntimeError('Unable to create module spec.')
		module = importlib.util.module_from_spec(spec)
		sys.modules[module_name] = module
		try:
			spec.loader.exec_module(module)
		except Exception:
			sys.modules.pop(module_name, None)
			raise
		else:
			self.addCleanup(sys.modules.pop, module_name, None)
			return module

	def _load_module_from_text(self, source: str) -> types.ModuleType:
		with tempfile.TemporaryDirectory() as temp_dir:
			source_file = os.path.join(temp_dir, 'attribute_docs_module.py')
			with open(source_file, 'w', encoding='utf-8') as module_file:
				module_file.write(textwrap.dedent(source))
			return self._load_module_from_source(source_file)

	def test_01_dict_functionality(self):
		"""Test Meta __getitem__."""

		self.assertIsInstance(self.cls['str_field'], ft3.Field)

	def test_02_dict_functionality(self):
		"""Test Meta __getitem__ with type input returns Field alias."""

		self.assertIsInstance(ft3.Field[str], ft3.objects.typ.Field)

	def test_03_dict_functionality(self):
		"""Test Meta __getitem__ with type input raises KeyError if not Field."""

		self.assertRaises(KeyError, lambda: self.cls[str])

	def test_04_dict_functionality(self):
		"""Test __setitem__ raises correct exc if value is not FieldType."""

		self.assertRaises(
			ft3.objects.exc.IncorrectTypeError,
			lambda: self.mcs.__setitem__(self.cls, self.field.name, 'value'),
		)

	def test_05_dict_functionality(self):
		"""Test __setitem__ raises correct exc if Field with invalid name."""

		self.assertRaises(
			ft3.objects.exc.InvalidFieldRedefinitionError,
			lambda: self.mcs.__setitem__(
				self.cls,
				self.field.name,
				ft3.Field(
					name='_str_field',
					default='value',
					type_=str,
				),
			),
		)

	def test_06_dict_functionality(self):
		"""Test __setitem__ raises correct exc if Field has invalid type."""

		self.assertRaises(
			ft3.objects.exc.IncorrectTypeError,
			lambda: self.mcs.__setitem__(
				self.cls,
				self.field.name,
				ft3.Field(
					name='str_field',
					default='value',
					type_=int,
				),
			),
		)

	def test_07_dict_functionality(self):
		"""Test __setitem__ raises correct exc if Field does not exist."""

		self.assertRaises(
			ft3.objects.exc.InvalidFieldAdditionError,
			lambda: self.mcs.__setitem__(
				self.cls,
				'field_that_does_not_exist',
				ft3.Field(
					name='str_field',
					default='value',
					type_=str,
				),
			),
		)

	def test_08_repr_functionality(self):
		"""Test __repr__ is nice."""

		self.assertEqual(
			repr(self.cls),
			ft3.core.lib.json.dumps(
				dict(self.cls),
				default=ft3.core.strings.utl.convert_for_repr,
				indent=Constants.INDENT,
				sort_keys=True,
			),
		)

	def test_09_dict_keys(self):
		"""Test keys."""

		self.assertListEqual(
			list(self.cls.keys()), list(self.cls.__dataclass_fields__)
		)

	def test_10_dict_setitem(self):
		"""Test __setitem__ actually works."""

		self.cls[self.field.name] = self.field
		self.assertEqual(self.cls()[self.field.name], self.field.default)

	def test_11_iter(self):
		"""Test __iter__."""

		self.assertTupleEqual(
			tuple(self.mcs.__iter__(self.cls)), self.cls.fields
		)

	def test_12_dict_functionality(self):
		"""Test __setitem__ raises correct exc if invalid default."""

		self.assertRaises(
			ft3.objects.exc.IncorrectDefaultTypeError,
			lambda: self.mcs.__setitem__(
				self.cls,
				self.field.name,
				ft3.Field(
					name='str_field',
					default=4,
					type_=str,
				),
			),
		)

	def test_13_classvar_skip(self):
		"""Test ClassVar annotation skip."""

		self.mcs(
			'ExcTest',
			(ft3.objects.objs.obj.ObjectBase,),
			{
				'__annotations__': {
					self.field.name: typing.ClassVar[str],
				},
				'__module__': self.__module__,
			},
		)
		self.assertTrue(True)

	def test_14_undefined_field_error(self):
		"""Test cannot set undefined field."""

		self.assertRaises(
			ft3.objects.exc.InvalidFieldAdditionError,
			lambda: self.mcs.__setitem__(
				self.cls,
				'field_that_does_not_exist',
				ft3.Field(
					name='field_that_does_not_exist',
					default='value',
					type_=str,
				),
			),
		)

	def test_15_incorrect_type_error(self):
		"""Test cannot `setattr` invalid type for `Field`."""

		self.assertRaises(
			ft3.objects.exc.IncorrectTypeError,
			lambda: self.mcs.__setattr__(self.cls, 'bool_field', 42),
		)

	def test_16_setattr(self):
		"""Test `Meta.__setattr__()`."""

		new_field = ft3.Field(name='bool_field', type_=bool, default=True)
		self.mcs.__setattr__(self.cls, 'bool_field', new_field)
		self.assertEqual(self.cls.bool_field, new_field)

	def test_17_contains(self):
		"""Test `Meta.__contains__()`."""

		self.assertTrue('bool_field' in self.cls)

	def test_18_invalid_definition_from_casing(self):
		"""Test cannot define `Object` with invalid casing."""

		def _fn():
			class _InvalidObj(ft3.Object):
				valid_case_class_var: ft3.core.lib.t.ClassVar[str] = 'test'
				notSnakeCase: ft3.Field[str] = 'test'

		self.assertRaises(ft3.objects.exc.IncorrectCasingError, _fn)

	def test_19_attribute_docs_preserved(self):
		"""Test attribute docs are preserved and fields point to owner."""

		ft3.objects.utl._get_attribute_docs_for_source.cache_clear()
		module = self._load_module_from_text(
			'''
			import ft3


			class Documented(ft3.Object):
			    """Documented test object."""

			    first_field: ft3.Field[str]
			    """First field docs."""
			    second_field: ft3.Field[int] = 1
			    """Second field docs."""
			'''
		)

		self.assertEqual(
			module.Documented.first_field.description, 'First field docs.'
		)
		self.assertEqual(
			module.Documented.second_field.description, 'Second field docs.'
		)
		self.assertIs(
			module.Documented.__dataclass_fields__['first_field']['object'],
			module.Documented,
		)

	def test_20_attribute_docs_parse_source_once(self):
		"""Test multiple classes in one file share one source parse."""

		ft3.objects.utl._get_attribute_docs_for_source.cache_clear()
		calls = 0
		original_parse = ft3.objects.utl.lib.ast.parse

		def counting_parse(*args, **kwargs):
			nonlocal calls

			calls += 1
			return original_parse(*args, **kwargs)

		with mock.patch.object(
			ft3.objects.utl.lib.ast, 'parse', counting_parse
		):
			module = self._load_module_from_text(
				'''
				import ft3


				class FirstObject(ft3.Object):
				    """First test object."""

				    first_field: ft3.Field[str]
				    """First field docs."""


				class SecondObject(ft3.Object):
				    """Second test object."""

				    second_field: ft3.Field[str]
				    """Second field docs."""
				'''
			)

		self.assertEqual(calls, 1)
		self.assertEqual(
			module.FirstObject.first_field.description, 'First field docs.'
		)
		self.assertEqual(
			module.SecondObject.second_field.description, 'Second field docs.'
		)

	def test_21_attribute_docs_source_unavailable(self):
		"""Test source-unavailable classes return empty docs."""

		self.assertDictEqual(ft3.objects.utl.get_attribute_docs(int), {})

	def test_22_attribute_docs_can_be_disabled(self):
		"""Test environment flag disables attribute doc extraction."""

		ft3.objects.utl._get_attribute_docs_for_source.cache_clear()
		with (
			mock.patch.dict(os.environ, {'FT3_EXTRACT_ATTRIBUTE_DOCS': '0'}),
			mock.patch.object(
				ft3.objects.utl, '_get_attribute_docs_for_source'
			) as get_docs,
		):

			class DisabledDocs(ft3.Object):
				disabled_field: ft3.Field[str]
				"""Disabled field docs."""

			self.assertDictEqual(
				ft3.objects.utl.get_attribute_docs(DisabledDocs), {}
			)
			self.assertIsNone(DisabledDocs.disabled_field.description)
			get_docs.assert_not_called()

	def test_23_ast_find_classdef(self):
		"""Test finding a class definition from an AST."""

		tree = ft3.objects.utl.lib.ast.parse('class Sample:\n\tpass')
		self.assertEqual(
			ft3.objects.utl.ast_find_classdef(tree).name, 'Sample'
		)

	def test_24_attribute_docs_missing_source_key(self):
		"""Test missing source files return a stable empty cache key."""

		missing_source = os.path.join('missing', 'source.py')
		self.assertEqual(
			ft3.objects.utl._source_file_cache_key(missing_source),
			(os.path.abspath(missing_source), 0, 0),
		)

	def test_25_attribute_docs_parse_failure(self):
		"""Test source parse failures return empty docs."""

		ft3.objects.utl._get_attribute_docs_for_source.cache_clear()
		with tempfile.TemporaryDirectory() as temp_dir:
			source_file = os.path.join(temp_dir, 'broken.py')
			with open(source_file, 'w', encoding='utf-8') as module_file:
				module_file.write('class Broken(')

			self.assertDictEqual(
				ft3.objects.utl._get_attribute_docs_for_source(
					*ft3.objects.utl._source_file_cache_key(source_file)
				),
				{},
			)

	def test_26_attribute_docs_empty_source_file(self):
		"""Test empty source lookup returns empty docs."""

		with (
			mock.patch.object(
				ft3.objects.utl.lib.inspect, 'getsourcefile', return_value=''
			),
			mock.patch.object(
				ft3.objects.utl.lib.inspect, 'getfile', return_value=''
			),
		):
			self.assertDictEqual(
				ft3.objects.utl.get_attribute_docs(mocking.Derivative), {}
			)

	def test_27_attribute_docs_nested_duplicate_names(self):
		"""Test qualnames disambiguate duplicate short class names."""

		ft3.objects.utl._get_attribute_docs_for_source.cache_clear()
		module = self._load_module_from_text(
			'''
			import ft3


			class Outer:

			    class Duplicate(ft3.Object):
			        nested_field: ft3.Field[str]
			        """Nested docs."""


			class Duplicate(ft3.Object):
			    top_field: ft3.Field[str]
			    """Top-level docs."""
			'''
		)

		self.assertEqual(
			module.Outer.Duplicate.nested_field.description, 'Nested docs.'
		)
		self.assertEqual(
			module.Duplicate.top_field.description, 'Top-level docs.'
		)


class TestExceptions(unittest.TestCase):
	"""Fixture for testing exceptions."""

	def setUp(self) -> None:
		self.mcs = ft3.objects.metas.Meta
		self.field = ft3.Field(
			name='str_field',
			default='value',
			type_=str,
		)
		return super().setUp()

	def test_01_no_reserved_fields(self):
		"""Test cannot create with reserved keyword overwrites."""

		self.assertRaises(
			ft3.objects.exc.ReservedKeywordError,
			lambda: self.mcs(
				'ExcTest',
				(ft3.objects.objs.obj.ObjectBase,),
				{
					'__cache__': {},
					'__module__': self.__module__,
					'__dataclass_fields__': {},
				},
			),
		)

	def test_02_no_annotations(self):
		"""Test cannot create without annotations."""

		self.assertRaises(
			ft3.objects.exc.MissingTypeAnnotation,
			lambda: self.mcs(
				'ExcTest',
				(ft3.objects.objs.obj.ObjectBase,),
				{
					self.field.name: self.field,
					'__annotations__': {},
					'__module__': self.__module__,
				},
			),
		)

	def test_03_non_field_annotations(self):
		"""Test cannot create without FieldType annotations."""

		self.assertRaises(
			ft3.objects.exc.FieldAnnotationError,
			lambda: self.mcs(
				'ExcTest',
				(ft3.objects.objs.obj.ObjectBase,),
				{
					self.field.name: self.field,
					'__annotations__': {
						self.field.name: str,
					},
					'__module__': self.__module__,
				},
			),
		)

	def test_04_no_reserved_annotations(self):
		"""Test cannot create with reserved keyword overwrites."""

		self.assertRaises(
			ft3.objects.exc.ReservedKeywordError,
			lambda: self.mcs(
				'ExcTest',
				(ft3.objects.objs.obj.ObjectBase,),
				{
					'__annotations__': {
						'__dataclass_fields__': {},
					},
					'__module__': self.__module__,
				},
			),
		)

	def test_05_non_field_annotations(self):
		"""Test cannot create without FieldType annotations."""

		self.assertRaises(
			ft3.objects.exc.FieldAnnotationError,
			lambda: self.mcs(
				'ExcTest',
				(ft3.objects.objs.obj.ObjectBase,),
				{
					'__annotations__': {
						self.field.name: str,
					},
					'__module__': self.__module__,
				},
			),
		)

	def test_06_inconsistent_casing(self):
		"""Test cannot create with inconsistent field casing."""

		self.assertRaises(
			ft3.objects.exc.IncorrectCasingError,
			lambda: self.mcs(
				'ExcTest',
				(ft3.objects.objs.obj.ObjectBase,),
				{
					'__annotations__': {
						'string_field': ft3.Field[str],
						'stringField': ft3.Field[str],
					},
					'__module__': self.__module__,
				},
			),
		)
