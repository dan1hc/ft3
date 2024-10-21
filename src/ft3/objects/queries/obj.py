"""Query module."""

__all__ = (
    'AndQuery',
    'ContainsQueryCondition',
    'EqQueryCondition',
    'GeQueryCondition',
    'GtQueryCondition',
    'InvertQuery',
    'LeQueryCondition',
    'LtQueryCondition',
    'NeQueryCondition',
    'OrQuery',
    'Query',
    'QuerySortBy',
    'SimilarQueryCondition',
    )

from .. import cfg
from .. import enm
from .. import fields
from .. import lib
from .. import objs
from .. import typ


class Constants(cfg.Constants):
    """Constant values specific to this file."""


class QuerySortBy(objs.Object):
    """Simple specification for sorting Query results by field."""

    field: fields.Field[str]
    direction: fields.Field[str] = fields.Field(
        default=enm.SortDirection.asc.value,
        enum=enm.SortDirection,
        )


class Query(objs.Object):
    """
    Database agnostic query object.

    ---

    ### Usage

    Queries for `Objects` can be generated from their fields \
    using the following comparison operators:

    * `field_1_eq_filter = Object.field_1 == 'test_value_123'`
    * `field_1_ne_filter = Object.field_1 != 'test_value_123'`
    * `field_1_ge_filter = Object.field_1 >= 'test_value_123'`
    * `field_1_gt_filter = Object.field_1 > 'test_value_123'`
    * `field_1_le_filter = Object.field_1 <= 'test_value_123'`
    * `field_1_lt_filter = Object.field_1 < 'test_value_123'`

    And the following special operators:

    * `field_1_contains_filter = Object.field_1 << 'test_value_123'`
    * `field_1_similarity_filter = Object.field_1 % 'test_value_123'`
    * `field_1_similarity_filter_with_threshold = Object.field_1 % ('test_value_123', 0.8)`

    Queries may be chained together using the `&` and `|` bitwise \
    operators, corresponding to `and` and `or` clauses respectively.

    Additionally, the invert (`~`) operator may be prefixed to any \
    Query to match the opposite of any conditions specified \
    instead.

    Queries also support optional result limiting and sorting:

    * Result limits can be specified by setting the `limit` field.
    * Results can be sorted any number of times using the `+=` and `-=` \
    operators.

    ---

    ### Example

    ```python
    query: Query = (
        (
            (Object.integer_field >= 1)
            | (Object.string_field % ('test', 0.75))
            )
        & ~(Object.list_field << 'test')
        ) += 'string_field' -= 'integer_field'

    ```

    In the example above, the query would match any `Object` for which \
    the string `'test'` is `not` a member of `list_field` and for which \
    either the value for `integer_field` is greater than or equal to `1` \
    or the value for `string_field` is at least `75%` similar to `'test'`. \
    Results would then be sorted first in `ascending` order on `string_field`, \
    then in `descending` order on `integer_field`.

    """

    sorting: fields.Field[list[QuerySortBy]] = []
    limit: fields.Field[lib.t.Optional[int]] = None

    def __iadd__(self, field: str) -> lib.Self:
        """Add an ascending sort to the selected `Query`."""

        self._sort_by(field)
        return self

    def __isub__(self, field: str) -> lib.Self:  # type: ignore[misc, override]
        """Add a descending sort to the selected `Query`."""

        self._sort_by(field, direction=enm.SortDirection.desc.value)
        return self

    def __and__(self, other: 'Query') -> 'AndQuery':
        return AndQuery(and_=[self, other])

    def __or__(self, other: 'Query') -> 'OrQuery':
        return OrQuery(or_=[self, other])

    def __invert__(self) -> 'InvertQuery':
        return InvertQuery(invert=self)

    def _sort_by(
        self,
        field: str,
        direction: typ.SortDirection = enm.SortDirection.asc.value
        ) -> None:
        """
        Sort the selected `Query` by `field` and `direction`.

        Direction may be either `'asc'` or `'desc'`.

        The `field` should correspond to an existing field for the `Object`.

        """

        self.sorting.append(QuerySortBy(field=field, direction=direction))


class QueryCondition(Query):
    """Base query filter."""

    field: fields.Field[str]


class SimilarQueryCondition(QueryCondition):
    """Filters where field is similar to value."""

    like: fields.Field[typ.Primitive | lib.t.Any]
    threshold: fields.Field[lib.t.Optional[float]] = None


class ContainsQueryCondition(QueryCondition):
    """Filters where field contains value."""

    contains: fields.Field[typ.Primitive | lib.t.Any]


class EqQueryCondition(QueryCondition):
    """Filters where == value."""

    eq: fields.Field[typ.Primitive | lib.t.Any]


class NeQueryCondition(QueryCondition):
    """Filters where != value."""

    ne: fields.Field[typ.Primitive | lib.t.Any]


class LeQueryCondition(QueryCondition):
    """Filters where <= value."""

    le: fields.Field[typ.Primitive | lib.t.Any]


class LtQueryCondition(QueryCondition):
    """Filters where < value."""

    lt: fields.Field[typ.Primitive | lib.t.Any]


class GeQueryCondition(QueryCondition):
    """Filters where >= value."""

    ge: fields.Field[typ.Primitive | lib.t.Any]


class GtQueryCondition(QueryCondition):
    """Filters where > value."""

    gt: fields.Field[typ.Primitive | lib.t.Any]


class AndQuery(Query):
    """Filters on all conditions."""

    and_: fields.Field[list[Query]]


class OrQuery(Query):
    """Filters on any condition."""

    or_: fields.Field[list[Query]]


class InvertQuery(Query):
    """Inverts the filter."""

    invert: fields.Field[Query]
