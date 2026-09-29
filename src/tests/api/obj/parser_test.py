import unittest

import ft3


class TestApiParser(unittest.TestCase):
	"""Fixture for testing the api argument parser."""

	def setUp(self) -> None:
		self.parser = ft3.cli.obj.root_parser
		return super().setUp()

	def test_01_port_default_is_int(self):
		"""Test default port is parsed as int."""

		args = self.parser.parse_args(['api', 'ft3'])
		self.assertIsInstance(args.port, int)
		self.assertEqual(args.port, ft3.api.cfg.Constants.DEFAULT_PORT)

	def test_02_port_long_flag_is_int(self):
		"""Test --port N is parsed as int."""

		args = self.parser.parse_args(['api', 'ft3', '--port', '8080'])
		self.assertIsInstance(args.port, int)
		self.assertEqual(args.port, 8080)

	def test_03_port_short_flag_is_int(self):
		"""Test -p N is parsed as int."""

		args = self.parser.parse_args(['api', 'ft3', '-p', '9000'])
		self.assertIsInstance(args.port, int)
		self.assertEqual(args.port, 9000)

	def test_04_port_non_int_rejected(self):
		"""Test non-integer port is rejected."""

		with self.assertRaises(SystemExit):
			self.parser.parse_args(['api', 'ft3', '--port', 'abc'])
