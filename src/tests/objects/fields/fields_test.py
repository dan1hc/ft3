import json
import unittest

import ft3

from ... import mocking


class TestField(unittest.TestCase):
    """Fixture for testing the object."""

    def setUp(self) -> None:
        self.int_field = ft3.Field(
            name='int_field',
            default=1,
            type_=int,
            )
        self.str_field = ft3.Field(
            name='str_field',
            default='a',
            type_=str,
            )
        self.union_field = ft3.Field(
            name='union_field',
            default='a',
            type_=int | str,
            )
        self.blank_field = ft3.Field(
            name='str_field',
            type_=str,
            )
        return super().setUp()

    def test_01_hash(self):
        """Test __hash__."""

        self.assertTrue(
            (
                self.str_field.__field_hash__()
                == ft3.Field(dict(self.str_field)).__field_hash__()
                == hash(
                    ''.join(
                        (
                            ft3.Field.__name__,
                            repr(self.str_field.type_),
                            repr(self.str_field.default),
                            self.str_field.name
                            )
                        )
                    )
                ) and self.str_field != self.int_field
            )

    def test_02_validate_comparison_exc(self):
        """Test invalid comparison type error raised."""

        self.assertRaises(
            ft3.objects.exc.InvalidComparisonTypeError,
            lambda: self.str_field % 2
            )

    def test_03_validate_comparison_container_exc(self):
        """Test invalid container comparison error raised."""

        self.assertRaises(
            ft3.objects.exc.InvalidContainerComparisonTypeError,
            lambda: self.int_field % 2
            )

    def test_04_validate_comparison_union_exc(self):
        """Test invalid comparison type error raised for Unions."""

        self.assertRaises(
            ft3.objects.exc.InvalidComparisonTypeError,
            lambda: self.union_field != bytes()
            )

    def test_05_lshift_overwrite(self):
        """Test __lshift__ updates when passed type same as self."""

        interpolated = self.blank_field << self.str_field
        self.assertEqual(interpolated.default, self.str_field.default)

    def test_06_repr_overwrite(self):
        """Test __repr__ same as _fields.Field."""

        self.assertEqual(
            repr(mocking.Derivative.bool_field),
            repr(
                ft3.objects.fields.Field(dict(mocking.Derivative.bool_field))
                )
            )

    def test_07_field_set_type_error(self):
        """Test __setitem__ raises correct exc if Field has invalid type."""

        self.assertRaises(
            ft3.objects.exc.IncorrectTypeError,
            lambda: ft3.objects.metas.Meta.__setitem__(
                ft3.Field,
                'name',
                ft3.Field(name='name', type_=int)
                )
            )


class TestFieldValidation(unittest.TestCase):
    """Fixture for testing the object."""

    def setUp(self) -> None:
        self.cls = mocking.TripDeriv
        return super().setUp()

    def test_01_parse(self):
        """Test correct exc raised if not nullable."""

        self.assertRaises(
            ft3.objects.exc.TypeValidationError,
            lambda: self.cls.non_nullable_field.parse(None)
            )

    def test_02_parse(self):
        """Test None."""

        self.assertIsNone(self.cls.null_field.parse(None))

    def test_03_parse(self):
        """Test bool."""

        self.assertIs(self.cls.bool_field.parse('true'), True)

    def test_04_parse(self):
        """Test decimal."""

        self.assertIsInstance(
            self.cls.decimal_field.parse('4.5'),
            self.cls.decimal_field.type_
            )

    def test_05_parse(self):
        """Test str null."""

        self.assertIsNone(self.cls.null_field.parse('null'))

    def test_06_parse(self):
        """Test unknown str exc."""

        self.assertRaises(
            ft3.objects.exc.TypeValidationError,
            lambda: self.cls.null_field.parse('asdf')
            )

    def test_07_parse(self):
        """Test Object from dict."""

        self.assertIsInstance(
            self.cls.new_deriv.parse(dict(self.cls.new_deriv.default)),
            self.cls.new_deriv.type_
            )

    def test_08_parse(self):
        """Test Union."""

        self.assertIsInstance(
            self.cls.forward_ref_union_field.parse('39.8'),
            ft3.core.typ.utl.check.get_checkable_types(
                self.cls.forward_ref_union_field.type_
                )
            )

    def test_09_parse(self):
        """Test Union."""

        self.assertRaises(
            ft3.objects.exc.TypeValidationError,
            lambda: self.cls.forward_ref_union_field.parse(
                ft3.Field(type_=str)
                ),
            )

    def test_10_parse(self):
        """Test Object from json."""

        self.assertIsInstance(
            self.cls.new_deriv.parse(repr(self.cls.new_deriv.default)),
            self.cls.new_deriv.type_
            )

    def test_11_parse(self):
        """Test any dict."""

        self.assertEqual(
            self.cls.dict_field.parse(
                json.dumps(
                    self.cls.generic_dict_field.default
                    )
                ),
            self.cls.generic_dict_field.default
            )

    def test_12_parse(self):
        """Test generic dict."""

        self.assertRaises(
            ft3.objects.exc.TypeValidationError,
            lambda: self.cls.generic_dict_field.parse(
                json.dumps(self.cls.dict_field.default)
                ),
            )

    def test_13_parse(self):
        """Test any array."""

        self.assertEqual(
            self.cls.tuple_field.parse(
                json.dumps(
                    self.cls.generic_tuple_field.default
                    )
                ),
            self.cls.generic_tuple_field.default
            )

    def test_14_parse(self):
        """Test generic array."""

        self.assertRaises(
            ft3.objects.exc.TypeValidationError,
            lambda: self.cls.generic_tuple_field.parse(
                json.dumps(self.cls.tuple_field.default)
                ),
            )

    def test_15_set(self):
        """
        Test `Field__set__`.

        """

        obj = mocking.NewDeriv()

        def _fn():
            mocking.NewDeriv.generic_tuple_deriv_field.__set__(obj, 3)

        self.assertRaises(ft3.objects.exc.IncorrectTypeError, _fn)

    def test_16_set(self):
        """
        Test `Field__set__`.

        """

        obj = mocking.NewDeriv()

        def _fn():
            mocking.NewDeriv.generic_tuple_deriv_field.__set__(obj, '3')

        self.assertRaises(ft3.objects.exc.TypeValidationError, _fn)

    def test_17_set(self):
        """
        Test `Field__set__`.

        """

        obj = mocking.NewDeriv()
        mocking.NewDeriv.anti_field_1.__set__(obj, '3')

        self.assertEqual(obj.anti_field_1, '3')

    def test_18_set(self):
        """
        Test `Field__set__`.

        """

        obj = mocking.NewDeriv()
        mocking.NewDeriv.anti_field_2.__set__(obj, True)

        self.assertEqual(obj.anti_field_2, True)

    def test_19_parse(self):
        """
        Test parse returns `None` instead of error when set `False`.

        """

        self.assertIsNone(
            self.cls.generic_dict_field.parse(
                json.dumps(self.cls.dict_field.default),
                raise_validation_error=False
                )
            )

    def test_20_eq(self):
        """Test `Field.__eq__()`."""

        self.assertTrue(
            self.cls.generic_dict_field == self.cls.generic_dict_field
            )
