import unittest

import ft3

from ... import mocking


class TestSchema(unittest.TestCase):
    """Fixture for testing the object."""

    def setUp(self) -> None:
        self.cls = mocking.ApiDeriv
        return super().setUp()

    def test_01_from_obj(self):
        """Test from_obj."""

        schema = ft3.api.obj.Schema.from_obj(self.cls)
        self.assertIsInstance(schema, ft3.api.obj.Schema)
