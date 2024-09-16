"""Module utils unit tests."""

import unittest

import ft3

from . import cfg


class Constants(cfg.Constants):
    """Constant values specific to unit tests in this file."""

    VALID_CAMEL_STRING_EXAMPLES = (
        'upperSnakeCaseString100SureFift337aGood',
        '_privateValidCamelCaseString'
        )
    VALID_SNAKE_STRING_EXAMPLES = (
        'upper_snake_case_string_100_sure_fift_337a_good',
        '_snake_case_string_'
        )
    BIG_STR_DICT = {
        'api-key': VALID_CAMEL_STRING_EXAMPLES[0] * 30,
        'regular': VALID_SNAKE_STRING_EXAMPLES[0] * 30,
        }


class TestUtils(unittest.TestCase):
    """Fixture for testing."""

    def test_01_camel_case_check(self):
        """Test camelCase validation."""

        self.assertFalse(
            ft3.core.strings.utl.isCamelCaseString(
                Constants.VALID_CAMEL_STRING_EXAMPLES[-1]
                )
            )

    def test_02_case_conversion(self):
        """Test case conversion."""

        self.assertTrue(
            ft3.core.strings.utl.is_snake_case_iterable(
                [
                    ft3.core.strings.utl.camel_case_to_snake_case(string)
                    for string
                    in Constants.VALID_CAMEL_STRING_EXAMPLES
                    ]
                )
            )

    def test_03_str_validation(self):
        """Test case validation asserts `type[str]`."""

        self.assertRaises(
            TypeError,
            lambda: ft3.core.strings.utl.validate_casing(
                123,
                ft3.core.strings.enm.SupportedCasing.snake_case.value
                )
            )

    def test_04_case_validation(self):
        """Test case validation asserts snake casing."""

        self.assertRaises(
            ft3.core.strings.exc.StringCasingError,
            lambda: ft3.core.strings.utl.validate_casing(
                Constants.INVALID_STRING_CASING_EXAMPLE,
                ft3.core.strings.enm.SupportedCasing.snake_case.value
                )
            )

    def test_05_case_validation(self):
        """Test case validation asserts camel casing."""

        self.assertRaises(
            ft3.core.strings.exc.StringCasingError,
            lambda: ft3.core.strings.utl.validate_casing(
                Constants.INVALID_STRING_CASING_EXAMPLE,
                ft3.core.strings.enm.SupportedCasing.camelCase.value
                )
            )

    def test_06_snake_iterable_check(self):
        """Test snake_case validation."""

        self.assertTrue(
            ft3.core.strings.utl.is_snake_case_iterable(
                Constants.VALID_SNAKE_STRING_EXAMPLES
                )
            )

    def test_07_camel_iterable_check(self):
        """Test camelCase validation."""

        self.assertTrue(
            ft3.core.strings.utl.isCamelCaseIterable(
                Constants.VALID_CAMEL_STRING_EXAMPLES
                )
            )

    def test_08_get_cname(self):
        """Test cname retrieval."""

        self.assertEqual(
            ft3.core.strings.utl.cname_for(
                Constants.VALID_CAMEL_STRING_EXAMPLES[-1].strip('_'),
                Constants.VALID_CAMEL_STRING_EXAMPLES
                ),
                Constants.VALID_CAMEL_STRING_EXAMPLES[-1]
            )

    def test_09_get_cname(self):
        """Test cname retrieval for a snake_case string."""

        self.assertEqual(
            ft3.core.strings.utl.cname_for(
                Constants.VALID_SNAKE_STRING_EXAMPLES[0],
                Constants.VALID_CAMEL_STRING_EXAMPLES
                ),
                Constants.VALID_CAMEL_STRING_EXAMPLES[0]
            )

    def test_10_get_cname(self):
        """Test cname retrieval negative case returns None."""

        self.assertIsNone(
            ft3.core.strings.utl.cname_for(
                Constants.INVALID_STRING_CASING_EXAMPLE,
                Constants.VALID_CAMEL_STRING_EXAMPLES
                )
            )

    def test_11_validation_success(self):
        """Test validation succeeds."""

        self.assertIsNone(
            ft3.core.strings.utl.validate_casing(
                Constants.VALID_SNAKE_STRING_EXAMPLES[0],
                ft3.core.strings.enm.SupportedCasing.snake_case.value
                )
            )

    def test_12_field_serialization(self):
        """Test field serialization."""

        field = ft3.Field(name='test', default='testing', type_=str)
        self.assertEqual(
            repr(ft3.objects.typ.Field(field, field.type_)),
            ft3.core.strings.utl.convert_for_repr(field)
            )

    def test_13_fn_serialization(self):
        """Test fn serialization."""

        def fn() -> str:
            return 'str'

        self.assertEqual(
            ft3.core.strings.utl.convert_for_repr(
                fn.__annotations__['return'],
                ),
            ft3.core.strings.utl.convert_for_repr(fn)
            )

    def test_14_big_str_redaction(self):
        """Test big_str redaction."""

        self.assertEqual(
            ft3.core.strings.utl.convert_for_repr(
                Constants.BIG_STR_DICT,
                )['api-key'],
            ft3.core.strings.utl.redact_key_value_pair('api-key', 'anything')
            )

    def test_15_big_str_serialization(self):
        """Test big_str serialization."""

        self.assertEqual(
            ft3.core.strings.utl.convert_for_repr(
                Constants.BIG_STR_DICT['regular']
                ),
            [
                Constants.M_LINE_TOKEN,
                *''.join(
                    ft3.core.strings.obj.StringWrapper.wrap(
                        Constants.BIG_STR_DICT['regular']
                        )[:Constants.CUTOFF_LEN]
                    ).split('\n'),
                '[[...]]'
                ]
            )
