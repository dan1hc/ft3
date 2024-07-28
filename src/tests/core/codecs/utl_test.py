"""Module utils unit tests."""

import unittest

import ft3

from ft3 . core import codecs
from ft3 . core import lib

from . import cfg


class SimpleTypedObj(lib.t.TypedDict):
    """Simple `SupportsAnnotation` object."""

    name: str
    id_: int


class SubDecimal(lib.decimal.Decimal):
    """Decimal subclass for testing."""


class UnknownSerializable:
    """Class for testing with no known serialization."""


class Constants(cfg.Constants):
    """Constant values specific to unit tests in this file."""

    SimpleDict: dict[str, tuple[int, ...]] = {
        'a_simple_key': (0, ),
        '_and_another_': (4, 3, 2, ),
        'components': (1, 2, )
        }
    SimpleTuple = (1, 2, 3, )
    BoolTuple = (True, False, True, )
    BoundType = lib.t.TypeVar('BoundType', bound=int)
    ComplexStr = '1.134_12e+2-1.134_12e+2j'
    ConstrainedType = lib.t.TypeVar('ConstrainedType', bool, int)
    AnotherConstrainedType = lib.t.TypeVar(
        'AnotherConstrainedType',
        tuple[int] | tuple[str],
        tuple[bool] | tuple[int],
        tuple[float] | tuple[bool] | tuple[int] | bool
        )
    NestedDict = {'nesting': SimpleDict}
    DateTime = lib.datetime.datetime.now(lib.datetime.timezone.utc)
    Date = DateTime.date()
    SimpleObj = SimpleTypedObj(name='test', id_=1)


class TestUtils(unittest.TestCase):
    """Fixture for testing."""

    def test_01_tuple_parse(self):
        """Test `parse` on `tuple[int, ...]`."""

        self.assertEqual(
            Constants.SimpleTuple,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.SimpleTuple),
                tuple[int, ...]
                )
            )

    def test_02_dict_parse(self):
        """Test `parse` on `dict[str, tuple[int, ...]]`."""

        self.assertEqual(
            Constants.SimpleDict,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.SimpleDict),
                dict[str, tuple[int, ...]]
                )
            )

    def test_03_typevar_parse_bound(self):
        """Test `parse` on `tuple[BoundType, ...]`."""

        self.assertNotEqual(
            Constants.SimpleTuple,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.BoolTuple),
                tuple[Constants.BoundType, ...]
                )
            )

    def test_04_typevar_parse_bound(self):
        """Test `parse` on `tuple[BoundType, ...]`."""

        self.assertEqual(
            Constants.BoolTuple,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.BoolTuple),
                tuple[Constants.BoundType, ...]
                )
            )

    def test_05_typevar_parse_constrained(self):
        """Test `parse` on `tuple[ConstrainedType, ...]`."""

        self.assertEqual(
            Constants.BoolTuple,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.BoolTuple),
                tuple[Constants.ConstrainedType, ...]
                )
            )

    def test_06_nested_dict_parse(self):
        """Test `parse` on `dict[str, dict[str, tuple[int, ...]]]`."""

        self.assertEqual(
            Constants.NestedDict,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.NestedDict),
                dict[str, dict[str, tuple[int, ...]]]
                )
            )

    def test_07_bool_parse(self):
        """Test `parse` on `bool`."""

        self.assertIs(True, codecs.utl.parse('true', bool))

    def test_08_anti_bool_parse(self):
        """Test `parse` on `bool`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.bool_decode,
            codecs.utl.parse('asdf', bool)
            )

    def test_09_float_parse(self):
        """Test `parse` on `float`."""

        self.assertEqual(1.8, codecs.utl.parse('1.8', float))

    def test_10_anti_float_parse(self):
        """Test `parse` on `float`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.number_decode,
            codecs.utl.parse('asdf', float)
            )

    def test_11_complex_parse(self):
        """Test `parse` on `complex`."""

        self.assertEqual(
            complex(Constants.ComplexStr),
            codecs.utl.parse(Constants.ComplexStr, complex)
            )

    def test_12_none_parse(self):
        """Test `parse` on `None`."""

        self.assertIsNone(codecs.utl.parse('null', type(None)))

    def test_13_anti_none_parse(self):
        """Test `parse` on `None`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.null_decode,
            codecs.utl.parse('asdf', type(None))
            )

    def test_14_union_parse(self):
        """Test `parse` on `int | str`."""

        self.assertIsInstance(codecs.utl.parse('42', tuple[int] | int), int)

    def test_15_anti_tuple_parse(self):
        """Test `parse` on `tuple[int, ...]`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.invalid_arr_decode,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.SimpleTuple),
                tuple[frozenset, ...]
                )
            )

    def test_16_known_tuple_parse(self):
        """Test `parse` on `tuple[int, int, int]`."""

        self.assertEqual(
            Constants.SimpleTuple,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.SimpleTuple),
                tuple[int, int, int]
                )
            )

    def test_17_anti_known_tuple_parse(self):
        """Test `parse` on `tuple[int, int, int]`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.invalid_arr_len,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.SimpleTuple),
                tuple[int, int]
                )
            )

    def test_18_anti_known_tuple_parse(self):
        """Test `parse` on `tuple[int, int, int]`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.invalid_arr_decode,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.SimpleTuple),
                tuple[frozenset, list, tuple]
                )
            )

    def test_19_list_parse(self):
        """Test `parse` on `list[int]`."""

        self.assertEqual(
            list(Constants.SimpleTuple),
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.SimpleTuple),
                list[int]
                )
            )

    def test_20_anti_list_parse(self):
        """Test `parse` on `list[int]`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.value_decode,
            codecs.utl.parse('42', list[int])
            )

    def test_21_anti_list_parse(self):
        """Test `parse` on `list[int]`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.invalid_arr_decode,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.SimpleTuple),
                list[frozenset]
                )
            )

    def test_22_anti_list_parse(self):
        """Test `parse` on `list[int]`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.invalid_json,
            codecs.utl.parse('asdf', list[frozenset])
            )

    def test_23_anti_dict_parse(self):
        """Test `parse` on `dict[str, tuple[int, ...]]`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.invalid_json,
            codecs.utl.parse('asdf', dict[str, tuple[int, ...]])
            )

    def test_24_anti_dict_parse(self):
        """Test `parse` on `dict[str, tuple[int, ...]]`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.invalid_keys_decode,
            codecs.utl.parse(
                codecs.lib.json.dumps(
                    {
                        i: v
                        for (i, v)
                        in enumerate(Constants.SimpleDict.values())
                        }
                    ),
                dict[tuple[str], tuple[int, ...]]
                )
            )

    def test_25_anti_dict_parse(self):
        """Test `parse` on `dict[str, tuple[int, ...]]`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.invalid_values_decode,
            codecs.utl.parse(
                codecs.lib.json.dumps(
                    {
                        k: i
                        for (i, k)
                        in enumerate(Constants.SimpleDict.keys())
                        }
                    ),
                dict[str, tuple[int, ...]]
                )
            )

    def test_26_anti_dict_parse(self):
        """Test `parse` on `dict[str, tuple[int, ...]]`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.invalid_map_decode,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.SimpleDict),
                dict[str]
                )
            )

    def test_27_anti_dict_parse(self):
        """Test `parse` on `dict[str, tuple[int, ...]]`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.value_decode,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.SimpleTuple),
                dict[str, tuple[int, ...]]
                )
            )

    def test_28_typevar_parse_unbound(self):
        """Test `parse` on `tuple[BoundType, ...]`."""

        self.assertEqual(
            Constants.BoolTuple,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.BoolTuple),
                tuple[ft3.core.typ.AnyType, ...]
                )
            )

    def test_29_typevar_parse_constrained_again(self):
        """Test `parse` on `tuple[AnotherConstrainedType, ...]`."""

        self.assertEqual(
            Constants.BoolTuple,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.BoolTuple),
                tuple[Constants.AnotherConstrainedType, ...]
                )
            )

    def test_30_datetime_parse(self):
        """Test `parse` on `datetime.datetime`."""

        self.assertEqual(
            Constants.DateTime,
            codecs.utl.parse(
                Constants.DateTime.isoformat(),
                lib.datetime.datetime
                )
            )

    def test_31_date_parse(self):
        """Test `parse` on `datetime.date`."""

        self.assertEqual(
            Constants.Date,
            codecs.utl.parse(
                Constants.Date.isoformat(),
                lib.datetime.date
                )
            )

    def test_32_anti_datetime_parse(self):
        """Test `parse` on `datetime.datetime`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.datetime_decode,
            codecs.utl.parse('123', lib.datetime.datetime)
            )

    def test_33_parse_literal(self):
        """Test `parse` on `tuple[Literal[1], Literal[2], Literal[3]]`."""

        self.assertEqual(
            Constants.SimpleTuple,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.SimpleTuple),
                tuple[
                    lib.t.Literal[1],
                    lib.t.Literal[2],
                    lib.t.Literal[3]
                    ]
                )
            )

    def test_34_anti_parse_literal(self):
        """Test `parse` on `tuple[Literal[1], Literal[2], Literal[3]]`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.invalid_arr_decode,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.SimpleTuple),
                tuple[
                    lib.t.Literal[3],
                    lib.t.Literal[2],
                    lib.t.Literal[1]
                    ]
                )
            )

    def test_35_parse_another_literal(self):
        """Test `parse` on `Literal[1]`."""

        self.assertEqual(
            1,
            codecs.utl.parse('1', lib.t.Literal[1])
            )

    def test_36_anti_parse_another_literal(self):
        """Test `parse` on `Literal[1]`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.literal_decode,
            codecs.utl.parse('2', lib.t.Literal[1])
            )

    def test_37_parse_typed_obj(self):
        """Test `parse` on `TypedDict`."""

        self.assertEqual(
            Constants.SimpleObj,
            codecs.utl.parse(
                codecs.lib.json.dumps(Constants.SimpleObj),
                SimpleTypedObj
                )
            )

    def test_38_anti_parse_typed_obj(self):
        """Test `parse` on `TypedDict`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.invalid_map_decode,
            codecs.utl.parse(
                codecs.lib.json.dumps(SimpleTypedObj(name=1, id_='test')),
                SimpleTypedObj
                )
            )

    def test_39_anti_parse_typed_obj(self):
        """Test `parse` on `TypedDict`."""

        self.assertEqual(
            codecs.enm.ParseErrorRef.invalid_keys_decode,
            codecs.utl.parse(
                codecs.lib.json.dumps(SimpleTypedObj(not_a_key='test')),
                SimpleTypedObj
                )
            )

    def test_40_encode_subclass(self):
        """Test `encode` on `SubDecimal(Decimal)`."""

        value = SubDecimal(0.1)
        self.assertEqual(float(value), codecs.utl.encode(value))

    def test_41_encode_unknown(self):
        """Test `encode` on `UnknownSerializable`."""

        self.assertEqual(
            repr(UnknownSerializable),
            codecs.utl.encode(UnknownSerializable)
            )
