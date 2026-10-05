"""Every Python block in README.md runs, so the examples cannot drift."""

import pathlib
import re
import sys
import tomllib
import types
import unittest
import urllib.parse


class TestReadMe(unittest.TestCase):
	"""README.md examples are executable."""

	README = pathlib.Path(__file__).parents[2] / 'README.md'

	def test_01_every_python_block_runs(self):
		blocks = re.findall(
			r'```python\n(.*?)```', self.README.read_text(), re.DOTALL
		)
		self.assertGreaterEqual(len(blocks), 5)
		for index, block in enumerate(blocks):
			with self.subTest(block=index):
				module = types.ModuleType(f'readme_{index}')
				sys.modules[module.__name__] = module
				try:
					exec(
						compile(block, f'README.md#{index}', 'exec'),
						module.__dict__,
					)
				finally:
					sys.modules.pop(module.__name__, None)

	def test_02_python_badge_matches_classifiers(self):
		pyproject = tomllib.loads(
			(self.README.parent / 'pyproject.toml').read_text()
		)
		prefix = 'Programming Language :: Python :: '
		versions = [
			classifier.removeprefix(prefix)
			for classifier in pyproject['project']['classifiers']
			if classifier.startswith(prefix)
		]
		badge = re.search(
			r'img\.shields\.io/badge/python-(.*?)-brightgreen',
			self.README.read_text(),
		)
		assert badge is not None
		self.assertEqual(
			urllib.parse.unquote(badge.group(1)).split(' | '), versions
		)
