"""Every Python block in README.md runs, so the examples cannot drift."""

import pathlib
import re
import sys
import types
import unittest


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
