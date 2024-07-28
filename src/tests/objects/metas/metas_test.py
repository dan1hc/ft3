import typing
import unittest

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

    def test_01_dict_functionality(self):
        """Test Meta __getitem__."""

        self.assertIsInstance(
            self.cls['str_field'],
            ft3.Field
            )

    def test_02_dict_functionality(self):
        """Test Meta __getitem__ with type input returns Field alias."""

        self.assertIsInstance(
            ft3.Field[str],
            ft3.objects.typ.Field
            )

    def test_03_dict_functionality(self):
        """Test Meta __getitem__ with type input raises KeyError if not Field."""

        self.assertRaises(KeyError, lambda: self.cls[str])

    def test_04_dict_functionality(self):
        """Test __setitem__ raises correct exc if value is not FieldType."""

        self.assertRaises(
            ft3.objects.exc.IncorrectTypeError,
            lambda: self.mcs.__setitem__(self.cls, self.field.name, 'value')
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
                    )
                )
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
                    )
                )
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
                    )
                )
            )

    def test_08_repr_functionality(self):
        """Test __repr__ is nice."""

        self.assertEqual(
            repr(self.cls),
            ft3.core.lib.json.dumps(
                dict(self.cls),
                default=ft3.core.strings.utl.convert_for_repr,
                indent=Constants.INDENT,
                sort_keys=True
                )
            )

    def test_09_dict_keys(self):
        """Test keys."""

        self.assertListEqual(
            list(self.cls.keys()),
            list(self.cls.__dataclass_fields__)
            )

    def test_10_dict_setitem(self):
        """Test __setitem__ actually works."""

        self.cls[self.field.name] = self.field
        self.assertEqual(
            self.cls()[self.field.name],
            self.field.default
            )

    def test_11_iter(self):
        """Test __iter__."""

        self.assertTupleEqual(
            tuple(self.mcs.__iter__(self.cls)),
            self.cls.fields
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
                    )
                )
            )

    def test_13_classvar_skip(self):
        """Test ClassVar annotation skip."""

        self.mcs(
            'ExcTest',
            (ft3.objects.objs.obj.ObjectBase, ),
            {
                '__annotations__': {
                    self.field.name: typing.ClassVar[str],
                    },
                '__module__': self.__module__
                }
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
                    )
                )
            )

    def test_15_incorrect_type_error(self):
        """Test cannot `setattr` invalid type for `Field`."""

        self.assertRaises(
            ft3.objects.exc.IncorrectTypeError,
            lambda: self.mcs.__setattr__(self.cls, 'bool_field', 42)
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
                (ft3.objects.objs.obj.ObjectBase, ),
                {
                    '__cache__': {},
                    '__module__': self.__module__,
                    '__dataclass_fields__': {}
                    }
                ),
            )

    def test_02_no_annotations(self):
        """Test cannot create without annotations."""

        self.assertRaises(
            ft3.objects.exc.MissingTypeAnnotation,
            lambda: self.mcs(
                'ExcTest',
                (ft3.objects.objs.obj.ObjectBase, ),
                {
                    self.field.name: self.field,
                    '__annotations__': {},
                    '__module__': self.__module__
                    }
                ),
            )

    def test_03_non_field_annotations(self):
        """Test cannot create without FieldType annotations."""

        self.assertRaises(
            ft3.objects.exc.FieldAnnotationError,
            lambda: self.mcs(
                'ExcTest',
                (ft3.objects.objs.obj.ObjectBase, ),
                {
                    self.field.name: self.field,
                    '__annotations__': {
                        self.field.name: str,
                        },
                    '__module__': self.__module__
                    }
                ),
            )

    def test_04_no_reserved_annotations(self):
        """Test cannot create with reserved keyword overwrites."""

        self.assertRaises(
            ft3.objects.exc.ReservedKeywordError,
            lambda: self.mcs(
                'ExcTest',
                (ft3.objects.objs.obj.ObjectBase, ),
                {
                    '__annotations__': {
                        '__dataclass_fields__': {},
                        },
                    '__module__': self.__module__
                    }
                ),
            )

    def test_05_non_field_annotations(self):
        """Test cannot create without FieldType annotations."""

        self.assertRaises(
            ft3.objects.exc.FieldAnnotationError,
            lambda: self.mcs(
                'ExcTest',
                (ft3.objects.objs.obj.ObjectBase, ),
                {
                    '__annotations__': {
                        self.field.name: str,
                        },
                    '__module__': self.__module__
                    }
                ),
            )

    def test_06_inconsistent_casing(self):
        """Test cannot create with inconsistent field casing."""

        self.assertRaises(
            ft3.objects.exc.IncorrectCasingError,
            lambda: self.mcs(
                'ExcTest',
                (ft3.objects.objs.obj.ObjectBase, ),
                {
                    '__annotations__': {
                        'string_field': ft3.Field[str],
                        'stringField': ft3.Field[str],
                        },
                    '__module__': self.__module__
                    }
                ),
            )
