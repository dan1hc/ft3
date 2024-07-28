import pickle
import unittest

import ft3


class TestExceptions(unittest.TestCase):
    """Fixture for testing exceptions."""

    def setUp(self) -> None:
        return super().setUp()

    def test_01_serialization(self):
        """Test exc serializes correctly."""

        exc = ft3.loggers.exc.InvalidLogMessageTypeError(42)
        dump = pickle.dumps(exc)
        reloaded: ft3.core.typ.PackageExceptionType = pickle.loads(dump)
        self.assertTupleEqual(exc.args, reloaded.args)
