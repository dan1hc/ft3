"""Module objs unit tests."""

import pickle
import unittest

import ft3

from ft3 . core import lib

from ... import mocking

from . import cfg


class Constants(cfg.Constants):
    """Constant values specific to unit tests in this file."""


class TestObjectBase(unittest.TestCase):
    """Fixture for testing `Object` base functionality."""

    def setUp(self) -> None:
        self.mcs = ft3.objects.metas.Meta
        self.cls = mocking.Derivative
        self.object_ = self.cls()
        self.trip = mocking.TripDeriv(
            str_field='123',
            )
        self.anti = mocking.AntiTripDeriv(
            str_field='321'
            )
        return super().setUp()

    def test_01_dict_functionality(self):
        """Test `Object.__getitem__()`."""

        self.assertTrue(
            self.object_['int_field']
            == self.object_.int_field
            == self.cls.int_field.default
            )

    def test_02_dict_functionality(self):
        """Test `Object.__getitem__()` raises KeyError if no key."""

        self.assertRaises(
            KeyError,
            lambda: self.object_['field_that_does_not_exist']
            )

    def test_03_iter(self):
        """Test `Object.__iter__()`."""

        self.assertEqual(dict(self.object_.__iter__()), dict(self.object_))

    def test_04_len(self):
        """Test `Object.__len__()`."""

        self.assertEqual(len(self.object_), len(self.cls.fields))

    def test_05_contains(self):
        """Test `Object.__contains__()`."""

        self.assertIn(self.object_.fields[0], self.object_)

    def test_06_ne(self):
        """Test `Object.__ne__()`."""

        self.assertFalse(self.object_ != self.object_)

    def test_07_lshift(self):
        """Test `Object.__lshift__()` correctly interpolates."""

        object_ = self.trip << self.anti
        self.assertNotEqual(object_.str_field, self.anti.str_field)

    def test_08_lshift(self):
        """Test `Object.__lshift__()` correctly interpolates."""

        object_ = self.trip << self.anti
        self.assertNotEqual(object_.other_field, self.trip.other_field)

    def test_09_rshift(self):
        """Test `Object.__rshift__()` correctly overwrites."""

        default = mocking.TripDeriv()
        object_ = self.trip >> default
        self.assertNotEqual(object_.str_field, default.str_field)

    def test_10_rshift(self):
        """Test `Object.__rshift__()` correctly overwrites."""

        object_ = self.trip >> self.anti
        self.assertEqual(object_.str_field, self.anti.str_field)

    def test_11_dict_functionality(self):
        """Test `Object.get()` returns default if no key."""

        self.assertIsNone(self.object_.get('field_that_does_not_exist'))

    def test_12_to_dict(self):
        """Test `Object.to_dict()`."""

        self.assertDictEqual(
            {
                ft3.core.strings.utl.snake_case_to_camel_case(k): self.trip[k]
                for k, v in self.trip.items()
                if type(v) in lib.t.get_args(ft3.core.typ.Primitive)
                },
            {
                k: v
                for k, v
                in self.trip.to_dict(camel_case=True).items()
                if type(v) in lib.t.get_args(ft3.core.typ.Primitive)
                }
            )

    def test_13_to_dict(self):
        """Test `Object.to_dict()`."""

        self.assertDictEqual(
            {k: v for k, v in self.object_ if v is not None},
            self.object_.to_dict(include_null=False)
            )

    def test_14_repr(self):
        """Test `Object.__repr__()`."""

        self.assertEqual(
            repr(self.trip),
            lib.json.dumps(
                dict(self.trip),
                default=ft3.core.strings.utl.convert_for_repr,
                indent=Constants.INDENT,
                sort_keys=True
                )
            )

    def test_15_invalid_obj_comparison_exc(self):
        """
        Test InvalidObjectComparisonError raised when comparing \
        different Objects.

        """

        self.assertRaises(
            ft3.objects.exc.InvalidObjectComparisonError,
            lambda: mocking.NewDeriv() << mocking.TripDeriv()
            )

    def tearDown(self) -> None:
        return super().tearDown()


class TestObject(unittest.TestCase):
    """Fixture for testing `Object`."""

    def setUp(self) -> None:
        self.cls = mocking.Derivative
        self.object_= self.cls(str_field='cba')
        return super().setUp()

    def test_01_dunder_get_cls(self):
        """Test fields.Field __get__."""

        self.assertIsInstance(self.cls.str_field, ft3.Field)

    def test_02_dunder_get_ins(self):
        """Test fields.Field __get__."""

        self.assertIsInstance(
            self.object_.str_field,
            self.cls.str_field.type_
            )

    def test_03_get_enumeration_from_fields(self):
        """Test we get enumerations from Object fields."""

        self.assertIsInstance(
            ft3.objects.utl.get_enumerations_from_fields(
                self.cls.__dataclass_fields__
                ),
            dict
            )

    def test_04_get_enumeration_from_fields(self):
        """Test we get enumerations from Object fields."""

        self.assertIn(None, self.object_.enumerations['from_dict_field'])

    def test_05_get_fields_for_hash(self):
        """Test we get hashable fields from Object fields."""

        self.assertIn('secondary_key', self.object_.hash_fields)

    def test_06_delitem(self):
        """Test `Object.__delitem__()`."""

        del self.object_['str_field']
        self.assertEqual(
            self.cls.str_field.default,
            self.object_.str_field
            )

    def test_07_delitem(self):
        """Test `Object.__delitem__()`."""

        self.assertRaises(
            KeyError,
            lambda: self.object_.__delitem__('field_that_does_not_exist')
            )

    def test_08_setitem(self):
        """Test `Object.__setitem__()`."""

        self.assertRaises(
            KeyError,
            lambda: self.object_.__setitem__(
                'field_that_does_not_exist',
                1
                )
            )

    def test_09_reversed(self):
        """Test `Object.__reversed__()`."""

        self.assertListEqual(
            sorted(self.object_.keys(), reverse=True),
            list(reversed(self.object_))
            )

    def test_10_serialization(self):
        """Test `Object.__getstate__()`."""

        pickled = pickle.dumps(self.object_)
        self.assertEqual(self.object_, pickle.loads(pickled))

    def test_11_ior(self):
        """Test `Object.__ior__()`."""

        new_obj = self.cls()
        new_obj |= self.object_

        other_new_obj = self.cls()
        other_new_obj.update(self.object_)

        self.assertEqual(new_obj, other_new_obj)

    def test_12_copy(self):
        """Test `Object.__ior__()`."""

        new_obj = self.object_.copy()

        self.assertIsNot(new_obj, self.object_)

    def test_13_fromkeys(self):
        """Test `Object.__fromkeys__()`."""

        self.assertEqual(self.cls(), self.cls.fromkeys(()))

    def test_14_pop(self):
        """Test `Object.pop()`."""

        self.assertIsNone(self.object_.pop('not_a_real_field', None))

    def test_15_pop(self):
        """Test `Object.pop()`."""

        self.assertRaises(
            KeyError,
            lambda: self.object_.pop('not_a_real_field')
            )


class TestObjectDocumentationExamples(unittest.TestCase):
    """Test examples provided in Object __doc__."""

    def setUp(self) -> None:
        self.instance_values = {
            'id': 'abc123',
            '_alternate_id': 'dog1',
            'name': 'Bob',
            'type': 'dog',
            'in': 'timeout',
            'is_tail_wagging': False
            }
        self.new_name = 'Buddy'
        self.cls = mocking.examples.Pet
        self.object_= self.cls(
            id='abc123',
            _alternate_id='dog1',
            name='Bob',
            type='dog',
            in_='timeout',
            is_tail_wagging=False
            )
        self.object_from_dict = self.cls(self.instance_values)
        self.object_from_camel_case = self.cls(
            {
                'id': 'abc123',
                'alternateId': 'dog1',
                'name': 'Bob',
                'type': 'dog',
                'in': 'timeout',
                'isTailWagging': False
                }
            )
        return super().setUp()

    def test_01_instantiation(self):
        """Test __init__."""

        self.assertEqual(self.object_, self.object_from_dict)

    def test_02_instantiation_with_case_conversion(self):
        """Test __init__."""

        self.assertEqual(self.object_from_camel_case, self.object_)

    def test_03_dict_functionality(self):
        """Test __getitem__."""

        key = 'type'
        self.assertEqual(self.object_[key], self.instance_values[key])

    def test_04_dict_functionality(self):
        """Test __setitem__."""

        key = 'name'
        self.object_[key] = self.new_name
        self.assertTupleEqual(
            (self.new_name, self.new_name),
            (self.object_.name, self.object_[key])
            )

    def test_05_dict_functionality(self):
        """Test setdefault."""

        key = 'name'
        object_= self.cls()
        object_.setdefault(key, self.new_name)
        object_.setdefault(key, self.instance_values[key])
        self.assertTrue(
            getattr(object_, key)
            == self.new_name
            != self.instance_values[key]
            )

    def test_06_dict_keys(self):
        """Test keys."""

        self.assertListEqual(
            sorted(self.object_.keys()),
            sorted(self.instance_values)
            )

    def test_07_dict_values(self):
        """Test values."""

        self.assertListEqual(
            list(self.object_.values()),
            list(self.instance_values.values())
            )

    def test_08_dict_items(self):
        """Test items."""

        self.assertListEqual(
            sorted(self.object_.items()),
            sorted(self.instance_values.items())
            )

    def test_09_dict_key_error(self):
        """Test cannot set undefined field."""

        self.assertRaises(
            KeyError,
            lambda: self.object_.setdefault(
                'field_that_does_not_exist',
                self.new_name
                )
            )
