"""Contract: unknown keys are dropped everywhere, with one warning each."""

import unittest

import ft3

from . import cfg
from .validation_test import Constrained


class Constants(cfg.Constants):
	"""Constant values specific to unit tests in this file."""


class Holder(ft3.Object):
	"""Embeds a typed list, which used to reject unknown keys."""

	items_: ft3.Field[list[Constrained]] = []


class TestUnknownKeys(unittest.TestCase):
	"""Direct construction and embedded parsing share one policy."""

	def setUp(self) -> None:
		ft3.loggers.utl.Constants.WARNED.clear()
		return super().setUp()

	def test_01_direct_construction_drops_and_warns_once(self):
		with self.assertLogs(ft3.log, level='WARNING') as logs:
			first = Constrained(required_count=1, bogus=1)
			Constrained({'bogus': 2}, required_count=1)
		self.assertEqual(first.required_count, 1)
		self.assertNotIn('bogus', first.fields)
		self.assertEqual(len(logs.records), 1)
		self.assertIn('dropped', logs.output[0])

	def test_02_embedded_typed_list_drops_and_warns_once(self):
		record = {'items': [{'requiredCount': 1, 'bogus': 1}]}
		with self.assertLogs(ft3.log, level='WARNING') as logs:
			holder = Holder(record)
			Holder(record)
		self.assertEqual(holder.items_[0].required_count, 1)
		self.assertEqual(len(logs.records), 1)

	def test_03_warn_once_reports_whether_it_logged(self):
		key = ('Holder', 'unknown_key', 'x')
		self.assertTrue(ft3.loggers.utl.warn_once(key, {'content': 'x'}))
		self.assertFalse(ft3.loggers.utl.warn_once(key, {'content': 'x'}))


class TestSameNamedClasses(unittest.TestCase):
	"""Two Objects with the same class name never share state."""

	def test_01_annotations_are_cached_per_class(self):
		class Pet(ft3.Object):
			name: ft3.Field[str] = 'a'

		first = Pet

		class Pet(ft3.Object):  # noqa: F811
			other: ft3.Field[int] = 1

		self.assertEqual(
			set(ft3.core.typ.utl.hint.collect_annotations(first)), {'name'}
		)
		self.assertEqual(
			set(ft3.core.typ.utl.hint.collect_annotations(Pet)), {'other'}
		)
		self.assertIn('name', repr(first))
		self.assertIn('other', repr(Pet))
