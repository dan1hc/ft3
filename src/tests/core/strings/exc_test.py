"""Module exceptions unit tests."""

import pickle
import unittest

import ft3

from . import cfg


class Constants(cfg.Constants):
    """Constant values specific to unit tests in this file."""


class TestExceptions(unittest.TestCase):
    """Fixture for testing."""

    def test_01_serialization(self):
        """Test multi-arg exc serializes correctly."""

        exc = ft3.core.strings.exc.StringCasingError(
            Constants.INVALID_STRING_CASING_EXAMPLE,
            ft3.core.strings.typ.camelCase
            )
        dump = pickle.dumps(exc)
        deserialized_exc: ft3.core.strings.exc.StringCasingError = (
            pickle.loads(dump)
            )
        self.assertTupleEqual(exc.args, deserialized_exc.args)
