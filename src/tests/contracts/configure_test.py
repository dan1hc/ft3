"""Contract: every environment setting can be set from code instead."""

import unittest

import ft3


class TestConfigure(unittest.TestCase):
	"""`ft3.configure` overrides the environment-derived settings."""

	def tearDown(self) -> None:
		ft3.configure(
			legacy_wire=False,
			redact_allow=(),
			log_format='json',
			log_level='DEBUG',
			log_traceback=True,
		)
		return super().tearDown()

	def test_01_each_setting(self):
		ft3.configure(
			legacy_wire=True,
			redact_allow=['arena_tokens'],
			log_format='PRETTY',
			log_level='warning',
			log_traceback=False,
		)
		self.assertTrue(ft3.core.cfg.Constants.LEGACY_WIRE)
		self.assertEqual(
			ft3.core.strings.cfg.Constants.REDACT_ALLOW, ('arena_tokens',)
		)
		self.assertEqual(ft3.loggers.cfg.Constants.LOG_FORMAT, 'pretty')
		self.assertEqual(ft3.log.level, 30)
		self.assertFalse(ft3.loggers.cfg.Constants.LOG_TRACEBACK)

	def test_02_none_keeps_current_values(self):
		ft3.configure(legacy_wire=True)
		ft3.configure()
		self.assertTrue(ft3.core.cfg.Constants.LEGACY_WIRE)
		self.assertEqual(ft3.loggers.cfg.Constants.LOG_FORMAT, 'json')

	def test_03_legacy_wire_takes_effect_at_call_time(self):
		class Costs(ft3.Object):
			costs: ft3.Field[dict] = {'crystal_shards': 1}

		self.assertEqual(Costs().as_response['costs'], {'crystal_shards': 1})
		ft3.configure(legacy_wire=True)
		self.assertEqual(Costs().as_response['costs'], {'crystalShards': 1})
