import unittest

import ft3

from ... import mocking


class TestQuery(unittest.TestCase):
    """Fixture for testing the object."""

    def setUp(self) -> None:
        self.cls = mocking.Derivative
        return super().setUp()

    def test_01_eq(self):
        """Test __eq__."""

        self.assertIsInstance(
            self.cls.str_field == 'abc',
            ft3.objects.queries.EqQueryCondition
            )

    def test_02_ne(self):
        """Test __ne__."""

        self.assertIsInstance(
            self.cls.bool_field != True,  # noqa: E712
            ft3.objects.queries.NeQueryCondition
            )

    def test_03_le(self):
        """Test __le__."""

        self.assertIsInstance(
            self.cls.int_field <= 1,
            ft3.objects.queries.LeQueryCondition
            )

    def test_04_lt(self):
        """Test __lt__."""

        self.assertIsInstance(
            self.cls.int_field < 1,
            ft3.objects.queries.LtQueryCondition
            )

    def test_05_ge(self):
        """Test __ge__."""

        self.assertIsInstance(
            self.cls.int_field >= 1,
            ft3.objects.queries.GeQueryCondition
            )

    def test_06_gt(self):
        """Test __gt__."""

        self.assertIsInstance(
            self.cls.int_field > 1,
            ft3.objects.queries.GtQueryCondition
            )

    def test_07_contains(self):
        """Test __lshift__."""

        self.assertIsInstance(
            self.cls.str_field << 't',
            ft3.objects.queries.ContainsQueryCondition
            )

    def test_08_contains_error(self):
        """Test __lshift__ error."""

        self.assertRaises(
            ft3.objects.exc.InvalidContainerComparisonTypeError,
            lambda: self.cls.int_field << 't',
            )

    def test_09_similar(self):
        """Test __mod__."""

        self.assertIsInstance(
            self.cls.str_field % 't',
            ft3.objects.queries.SimilarQueryCondition
            )

    def test_10_similar_with_threshold(self):
        """Test __mod__ with threshold."""

        self.assertEqual(
            self.cls.str_field % ('t', 0.75),
            ft3.objects.queries.SimilarQueryCondition(
                field=self.cls.str_field.name,
                like='t',
                threshold=0.75
                )
            )

    def test_11_and_query(self):
        """Test __and__."""

        self.assertEqual(
            (
                (self.cls.int_field >= 1)
                & (self.cls.int_field < 10)
                ),
            ft3.objects.queries.AndQuery(
                and_=[
                    self.cls.int_field >= 1,
                    self.cls.int_field < 10
                    ]
                )
            )

    def test_12_or_query(self):
        """Test __or__."""

        self.assertEqual(
            (
                (self.cls.int_field >= 1)
                | (self.cls.int_field < 10)
                ),
            ft3.objects.queries.OrQuery(
                or_=[
                    self.cls.int_field >= 1,
                    self.cls.int_field < 10
                    ]
                )
            )

    def test_13_invert_query(self):
        """Test __invert__."""

        self.assertEqual(
            ~(_q := self.cls.int_field >= 1),
            ft3.objects.queries.InvertQuery(invert=_q)
            )

    def test_14_sort_asc_query(self):
        """Test __iadd__."""

        q = self.cls.int_field >= 1
        q += self.cls.int_field.name
        self.assertEqual(
            q.sorting[0],
            ft3.objects.queries.QuerySortBy(
                field=self.cls.int_field.name,
                direction='asc'
                )
            )

    def test_15_sort_desc_query(self):
        """Test __isub__."""

        q = self.cls.int_field >= 1
        q -= self.cls.int_field.name
        self.assertEqual(
            q.sorting[0],
            ft3.objects.queries.QuerySortBy(
                field=self.cls.int_field.name,
                direction='desc'
                )
            )

    def test_16_similar_without_threshold(self):
        """Test __mod__ without threshold."""

        self.assertEqual(
            self.cls.str_field % ('t', 'test'),
            ft3.objects.queries.SimilarQueryCondition(
                field=self.cls.str_field.name,
                like='t',
                threshold=ft3.objects.enm.MatchThreshold.default.value
                )
            )
