"""Contract: wire shape, truthiness, and copying of Objects."""

import copy
import unittest

import ft3

from ft3.core import lib

from . import cfg


class Constants(cfg.Constants):
	"""Constant values specific to unit tests in this file."""


class Gear(ft3.Object):
	"""A required, constrained field with no default."""

	slot: ft3.Field[str] = ft3.Field(enum=['head', 'body'], required=True)
	name: ft3.Field[str] = 'x'


class Costs(ft3.Object):
	"""Every wire-shape option in one place."""

	costs: ft3.Field[dict] = {'crystal_shards': 1}
	camel_costs: ft3.Field[dict] = ft3.Field(
		default={'crystal_shards': 1}, camel_case_keys=True
	)
	snake_costs: ft3.Field[dict] = ft3.Field(
		default={'crystal_shards': 1}, camel_case_keys=False
	)
	slots: ft3.Field[list[lib.t.Optional[str]]] = [None, 'm', None]
	compact: ft3.Field[list[lib.t.Optional[str]]] = ft3.Field(
		default=[None, 'm'], drop_null_items=True
	)
	rows: ft3.Field[list[dict]] = [{'a': None, 'b_c': 1}]
	stored: ft3.Field[str] = ft3.Field(default='s', read_only=True)
	maybe: ft3.Field[lib.t.Optional[str]] = None


def legacy(value: bool) -> None:
	ft3.core.cfg.Constants.LEGACY_WIRE = value


class TestTruthiness(unittest.TestCase):
	"""`bool(obj)` never constructs a default instance."""

	def test_01_does_not_raise_for_required_enum_field(self):
		self.assertFalse(bool(Gear()))
		self.assertTrue(bool(Gear(slot='head')))
		self.assertTrue(any([Gear(slot='body')]))

	def test_02_default_instance_is_falsy(self):
		self.assertFalse(Costs())
		self.assertTrue(Costs(maybe='y'))


class TestDeepCopy(unittest.TestCase):
	"""`deepcopy(obj)` shares nothing with the original."""

	def test_01_nested_dicts_in_lists_are_isolated(self):
		original = Costs()
		copied = copy.deepcopy(original)
		copied.rows[0]['b_c'] = 2
		copied.costs['crystal_shards'] = 2
		self.assertEqual(original.rows[0]['b_c'], 1)
		self.assertEqual(original.costs['crystal_shards'], 1)
		self.assertIsNot(copied.rows, original.rows)

	def test_02_read_only_and_private_survive(self):
		original = Costs(stored='kept')
		copied = copy.deepcopy(original)
		self.assertEqual(copied.stored, 'kept')
		self.assertEqual(copied.copy().stored, 'kept')


class TestWireShape(unittest.TestCase):
	"""Dict keys are never re-keyed and list nulls keep their positions."""

	def setUp(self) -> None:
		legacy(False)
		return super().setUp()

	def tearDown(self) -> None:
		legacy(False)
		return super().tearDown()

	def test_01_defaults(self):
		wire = Costs().as_response
		self.assertEqual(wire['costs'], {'crystal_shards': 1})
		self.assertEqual(wire['camelCosts'], {'crystalShards': 1})
		self.assertEqual(wire['snakeCosts'], {'crystal_shards': 1})
		self.assertEqual(wire['slots'], [None, 'm', None])
		self.assertEqual(wire['compact'], ['m'])
		self.assertEqual(wire['rows'], [{'a': None, 'b_c': 1}])

	def test_02_legacy_switch_restores_1x(self):
		legacy(True)
		wire = Costs().as_response
		self.assertEqual(wire['costs'], {'crystalShards': 1})
		self.assertEqual(wire['snakeCosts'], {'crystal_shards': 1})
		self.assertEqual(wire['slots'], ['m'])
		self.assertEqual(wire['rows'], [{'a': None, 'b_c': 1}])

	def test_03_unchanged_pins(self):
		obj = Costs()
		self.assertNotIn('stored', obj.to_dict())
		self.assertIn('stored', obj.as_response)
		self.assertNotIn('maybe', obj.as_response)
		self.assertIn('maybe', obj.to_dict())
		self.assertEqual(Costs(maybe='a') - Costs(maybe='b'), {'maybe': 'b'})

	def test_04_options_stay_out_of_openapi(self):
		with self.assertNoLogs(ft3.log, level='WARNING'):
			schema = ft3.api.obj.Schema.from_obj(Costs)
		self.assertNotIn(
			'camelCaseKeys', schema.properties['camelCosts'].as_response
		)
		self.assertNotIn(
			'dropNullItems', schema.properties['compact'].as_response
		)
