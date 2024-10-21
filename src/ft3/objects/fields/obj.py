"""Field module."""

__all__ = (
    'Field',
    )

from ... import core

from .. import cfg
from .. import enm
from .. import exc
from .. import lib
from .. import objs
from .. import typ

if lib.t.TYPE_CHECKING:  # pragma: no cover
    from .. import queries


class Constants(cfg.Constants):
    """Constant values specific to this file."""

    FACTORY_CACHE: dict[str, lib.t.Callable[[], lib.t.Any]] = {}


class Field(objs.Object, lib.t.Generic[typ.AnyType]):
    """
    Simple field object.

    ---

    ## Querying

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

    ---

    ## Parameters

    Specify parameters to constrain values allowed for the field \
    and control its behavior.


    ```python
    name: str = None

    ```

    Field Name.
    Sourced from / overwritten by attribute name.


    ```python
    type: type[lib.t.Any] = None

    ```

    Type of value.
    Sourced from / overwritten by type annotation.


    ```python
    default: lib.t.Any = None

    ```

    Default value for field.
    Sourced from / overwritten by attribute value.
    MUST be an instance of field `type` or `None`.


    ```python
    required: bool = False

    ```

    Whether or not the field SHOULD be required.
    Default behavior changes to assume `True` if \
    no attribute value is specified for the field.


    ```python
    enum: deque | frozenset | list | tuple | set | Enum = None

    ```

    Sequence of which field value SHOULD be a member, unless \
    `"*"` is included in the sequence, in which case ANY value \
    MAY be allowed, in addition to those explicitly specified.
    `None` is always allowed.


    ```python
    min_length: int = None

    ```

    Specify `len(value)` SHOULD be `>=` minimum.
    Field type MUST be `str` if specified.


    ```python
    max_length: int = None

    ```

    Specify `len(value)` SHOULD be `<=` maximum.
    Field type MUST be `str` if specified.


    ```python
    minimum: float = None

    ```

    Specify value SHOULD be `>=` minimum.
    Field type MUST be numeric if specified.


    ```python
    exclusive_minimum: bool = False

    ```

    Set `True` to specify value SHOULD be `>` minimum.
    Field minimum MUST also be specified.


    ```python
    maximum: float = None

    ```

    Specify value SHOULD be `<=` maximum.
    Field type MUST be numeric if specified.


    ```python
    exclusive_maximum: bool = False

    ```

    Set `True` to specify value SHOULD be `<` maximum.
    Field maximum MUST also be specified.


    ```python
    multiple_of: float = None

    ```

    Specify `value % multiple_of` SHOULD be `0`.
    Field type MUST be numeric if specified.


    ```python
    pattern: str = None

    ```

    Specify a Regex pattern for which the value SHOULD match.
    Field type MUST be `str` if specified.


    ```python
    min_items: int = None

    ```

    Specify `len(value)` SHOULD be `>=` min_items.
    Field type MUST be `deque | frozenset | list | tuple | set` if specified.


    ```python
    max_items: int = None

    ```

    Specify `len(value)` SHOULD be `<=` max_items.
    Field type MUST be `deque | frozenset | list | tuple | set` if specified.


    ```python
    unique_items: bool = False

    ```

    Specify all elements of value SHOULD be unique.
    Field type MUST be `deque | frozenset | list | tuple | set` if specified.


    ```python
    read_only: bool = False

    ```

    Specify this field SHOULD only be available to read \
    operations (like `GET` http calls).


    ```python
    write_only: bool = False

    ```

    Specify this field SHOULD only be available to write \
    operations (like `PATCH`, `POST`, or `PUT` http calls).

    """


    name: 'Field[str]' = None
    type_: 'Field[type[typ.AnyType]]' = None
    description: 'Field[str]' = None
    default: 'Field[typ.AnyType]' = None
    required: 'Field[bool]' = False
    enum: 'Field[typ.Enum]' = None
    min_length: 'Field[int]' = None
    max_length: 'Field[int]' = None
    minimum: 'Field[float]' = None
    exclusive_minimum: 'Field[bool]' = None
    maximum: 'Field[float]' = None
    exclusive_maximum: 'Field[bool]' = None
    multiple_of: 'Field[float]' = None
    pattern: 'Field[str]' = None
    min_items: 'Field[int]' = None
    max_items: 'Field[int]' = None
    unique_items: 'Field[bool]' = None
    read_only: 'Field[bool]' = None
    write_only: 'Field[bool]' = None

    @lib.t.overload
    def __get__(
        self,
        object_: None,
        dtype: type['objs.Object']
        ) -> 'Field[typ.AnyType]': ...
    @lib.t.overload
    def __get__(
        self,
        object_: 'objs.Object',
        dtype: type['objs.Object']
        ) -> typ.AnyType: ...
    def __get__(
        self,
        object_: lib.t.Optional['objs.Object'],
        dtype: type['objs.Object']
        ) -> 'Field[typ.AnyType]' | typ.AnyType:  # pragma: no cover
        return self

    def __set__(
        self,
        __object: lib.t.Any,
        __value: typ.AnyType
        ) -> lib.t.Optional[lib.Never]:
        object.__setattr__(
            __object,
            self.name,
            self.parse(__value, not self.required)
            )
        return None

    @lib.t.overload
    def __init__(
        self,
        class_as_dict: lib.t.Optional[dict[typ.AnyString, lib.t.Any]] = None,
        /,
        *,
        type_: type[typ.Type] = None,
        description: str = None,
        default: typ.Type | lib.t.Callable[[], typ.Type] = None,
        required: bool = False,
        enum: typ.Enum = None,
        min_length: int = None,
        max_length: int = None,
        minimum: float = None,
        exclusive_minimum: bool = None,
        maximum: float = None,
        exclusive_maximum: bool = None,
        multiple_of: float = None,
        pattern: str = None,
        min_items: int = None,
        max_items: int = None,
        unique_items: bool = None,
        read_only: bool = None,
        write_only: bool = None,
        **kwargs: lib.t.Any
        ): ...
    @lib.t.overload
    def __init__(
        self,
        class_as_dict: lib.t.Optional[dict[typ.AnyString, lib.t.Any]] = None,
        /,
        *,
        type_: type[typ.AnyType] = None,
        description: str = None,
        default: typ.AnyType | lib.t.Callable[[], typ.AnyType] = None,
        required: bool = False,
        enum: typ.Enum = None,
        min_length: int = None,
        max_length: int = None,
        minimum: float = None,
        exclusive_minimum: bool = None,
        maximum: float = None,
        exclusive_maximum: bool = None,
        multiple_of: float = None,
        pattern: str = None,
        min_items: int = None,
        max_items: int = None,
        unique_items: bool = None,
        read_only: bool = None,
        write_only: bool = None,
        **kwargs: lib.t.Any
        ): ...
    def __init__(
        self,
        class_as_dict: lib.t.Optional[dict[typ.AnyString, lib.t.Any]] = None,
        /,
        *,
        type_: type | type[typ.Type] | type[typ.AnyType] = None,
        description: str = None,
        default: lib.t.Any | lib.t.Callable[[], lib.t.Any] = None,
        required: bool = False,
        enum: typ.Enum = None,
        min_length: int = None,
        max_length: int = None,
        minimum: float = None,
        exclusive_minimum: bool = None,
        maximum: float = None,
        exclusive_maximum: bool = None,
        multiple_of: float = None,
        pattern: str = None,
        min_items: int = None,
        max_items: int = None,
        unique_items: bool = None,
        read_only: bool = None,
        write_only: bool = None,
        **kwargs: lib.t.Any
        ):
        if class_as_dict is not None:
            kwargs |= class_as_dict  # type: ignore[arg-type]
        else:
            kwargs |= dict(
                type_=lib.t.cast(
                    type[typ.AnyType],
                    type_ or kwargs.pop('type_', kwargs.pop('type', type_))
                    ),
                default=default,
                description=description,
                required=required,
                enum=enum,
                min_length=min_length,
                max_length=max_length,
                minimum=minimum,
                exclusive_minimum=exclusive_minimum,
                maximum=maximum,
                exclusive_maximum=exclusive_maximum,
                multiple_of=multiple_of,
                pattern=pattern,
                min_items=min_items,
                max_items=max_items,
                unique_items=unique_items,
                read_only=read_only,
                write_only=write_only,
                )

        ckwargs = {
            cname: value
            for name, value
            in kwargs.items()
            if (cname := core.strings.utl.cname_for(name, self.fields))
            }

        if isinstance(class_as_dict, lib.t.Mapping):
            class_as_cdict = {
                cname: value
                for name, value
                in class_as_dict.items()
                if (cname := core.strings.utl.cname_for(name, self.fields))
                }
            ckwargs |= class_as_cdict

        fname: typ.string[typ.snake_case]
        for fname, field in self.__dataclass_fields__.items():
            if fname not in ckwargs:
                ckwargs[fname] = field['default']

        for cname_, value in ckwargs.items():
            setattr(self, cname_, value)

        self.__post_init__()

    def __field_hash__(self) -> int:
        return hash(
            ''.join(
                (
                    self.__class__.__name__,
                    repr(self.type_) or str(),
                    repr(self.default) or str(),
                    self.name or str()
                    )
                )
            )

    @lib.t.overload
    def __eq__(
        self,
        other: 'typ.AnyField[lib.t.Any]'
        ) -> bool: ...
    @lib.t.overload
    def __eq__(self: object, other: object) -> bool: ...
    @lib.t.overload
    def __eq__(
        self,
        other: lib.t.Any
        ) -> 'bool | queries.EqQueryCondition | lib.Never': ...
    def __eq__(
        self,
        other: 'object | lib.t.Any | typ.AnyField[lib.t.Any]'
        ) -> 'bool | queries.EqQueryCondition | lib.Never':
        if typ.utl.check.is_field(other):
            return self.__field_hash__() == other.__field_hash__()
        self._validate_comparison(other)
        from .. import queries
        q: queries.EqQueryCondition = (
            queries.EqQueryCondition(
                field=self.name.rstrip('_'),
                eq=other
                )
            )
        return q

    @lib.t.overload
    def __ne__(
        self,
        other: 'typ.AnyField[lib.t.Any]'
        ) -> bool: ...
    @lib.t.overload
    def __ne__(self: object, other: object) -> bool: ...
    @lib.t.overload
    def __ne__(
        self,
        other: lib.t.Any
        ) -> 'bool | queries.NeQueryCondition | lib.Never': ...
    def __ne__(
        self,
        other: 'object | lib.t.Any | typ.AnyField[lib.t.Any]'
        ) -> 'bool | queries.NeQueryCondition | lib.Never':
        if typ.utl.check.is_field(other):
            return self.__field_hash__() != other.__field_hash__()
        self._validate_comparison(other)
        from .. import queries
        q: queries.NeQueryCondition = (
            queries.NeQueryCondition(
                field=self.name.rstrip('_'),
                ne=other
                )
            )
        return q

    @lib.t.overload
    def __mod__(
        self,
        params: tuple[typ.AnyType, float]
        ) -> 'queries.SimilarQueryCondition': ...
    @lib.t.overload
    def __mod__(
        self,
        params: typ.AnyType
        ) -> 'queries.SimilarQueryCondition': ...
    @lib.t.overload
    def __mod__(
        self,
        params: tuple[lib.t.Any, ...]
        ) -> 'queries.SimilarQueryCondition | lib.Never': ...
    @lib.t.overload
    def __mod__(
        self,
        params: lib.t.Any
        ) -> 'queries.SimilarQueryCondition | lib.Never': ...
    def __mod__(
        self,
        params: tuple[typ.AnyType, float] | tuple[lib.t.Any, ...] | lib.t.Any
        ) -> 'queries.SimilarQueryCondition | lib.Never':
        if isinstance(params, tuple):
            value, threshold = params
            if not isinstance(threshold, float):
                threshold = enm.MatchThreshold.default.value
        else:
            value = params
            threshold = enm.MatchThreshold.default.value
        self._validate_iterable_comparison(value)
        self._validate_comparison(value)
        from .. import queries
        q: queries.SimilarQueryCondition = (
            queries.SimilarQueryCondition(
                field=self.name.rstrip('_'),
                like=value,
                threshold=threshold
                )
            )
        return q

    @lib.t.overload
    def __lshift__(
        self,
        value: typ.obj.ObjectLike
        ) -> lib.Self | lib.Never: ...
    @lib.t.overload
    def __lshift__(
        self,
        value: lib.t.Any
        ) -> lib.t.Union[
            'queries.ContainsQueryCondition',
            'Field[lib.t.Any]',
            lib.Never
            ]: ...
    def __lshift__(
        self,
        value: 'lib.t.Any | typ.obj.ObjectLike'
        ) -> lib.t.Union[
            'queries.ContainsQueryCondition',
            'Field[lib.t.Any]',
            lib.Never
            ]:
        if typ.utl.check.is_field(value):
            return super().__lshift__(value)
        self._validate_iterable_comparison(value)
        from .. import queries
        q: queries.ContainsQueryCondition = (
            queries.ContainsQueryCondition(
                field=self.name.rstrip('_'),
                contains=value
                )
            )
        return q

    @lib.t.overload
    def __gt__(
        self,
        value: typ.AnyType
        ) -> 'queries.GtQueryCondition': ...
    @lib.t.overload
    def __gt__(
        self,
        value: lib.t.Any
        ) -> 'queries.GtQueryCondition | lib.Never': ...
    def __gt__(
        self,
        value: typ.AnyType | lib.t.Any
        ) -> 'queries.GtQueryCondition | lib.Never':
        self._validate_comparison(value)
        from .. import queries
        q: queries.GtQueryCondition = (
            queries.GtQueryCondition(
                field=self.name.rstrip('_'),
                gt=value
                )
            )
        return q

    @lib.t.overload
    def __ge__(
        self,
        value: typ.AnyType
        ) -> 'queries.GeQueryCondition': ...
    @lib.t.overload
    def __ge__(
        self,
        value: lib.t.Any
        ) -> 'queries.GeQueryCondition | lib.Never': ...
    def __ge__(
        self,
        value: typ.AnyType | lib.t.Any
        ) -> 'queries.GeQueryCondition | lib.Never':
        self._validate_comparison(value)
        from .. import queries
        q: queries.GeQueryCondition = (
            queries.GeQueryCondition(
                field=self.name.rstrip('_'),
                ge=value
                )
            )
        return q

    @lib.t.overload
    def __lt__(
        self,
        value: typ.AnyType
        ) -> 'queries.LtQueryCondition': ...
    @lib.t.overload
    def __lt__(
        self,
        value: lib.t.Any
        ) -> 'queries.LtQueryCondition | lib.Never': ...
    def __lt__(
        self,
        value: typ.AnyType | lib.t.Any
        ) -> 'queries.LtQueryCondition | lib.Never':
        self._validate_comparison(value)
        from .. import queries
        q: queries.LtQueryCondition = (
            queries.LtQueryCondition(
                field=self.name.rstrip('_'),
                lt=value
                )
            )
        return q

    @lib.t.overload
    def __le__(
        self,
        value: typ.AnyType
        ) -> 'queries.LeQueryCondition': ...
    @lib.t.overload
    def __le__(
        self,
        value: lib.t.Any
        ) -> 'queries.LeQueryCondition | lib.Never': ...
    def __le__(
        self,
        value: typ.AnyType | lib.t.Any
        ) -> 'queries.LeQueryCondition | lib.Never':
        self._validate_comparison(value)
        from .. import queries
        q: queries.LeQueryCondition = (
            queries.LeQueryCondition(
                field=self.name.rstrip('_'),
                le=value
                )
            )
        return q

    @lib.t.overload
    def _validate_comparison(
        self,
        value: lib.t.Optional[typ.AnyType]
        ) -> None: ...
    @lib.t.overload
    def _validate_comparison(
        self,
        value: lib.t.Any
        ) -> lib.t.Optional[lib.Never]: ...
    def _validate_comparison(
        self,
        value: lib.t.Any
        ) -> lib.t.Optional[lib.Never]:
        if (
            value is not None
            and not isinstance(
                value,
                typ.utl.check.get_checkable_types(self.type_)
                )
            ):
            raise exc.InvalidComparisonTypeError(
                self.name,
                self.type_,
                value
                )
        else:
            return None

    def _validate_iterable_comparison(
        self,
        value: lib.t.Any
        ) -> lib.t.Optional[lib.Never]:
        if not any(
            issubclass(tp, lib.t.Iterable)
            for tp
            in typ.utl.check.get_checkable_types(self.type_)
            ):
            raise exc.InvalidContainerComparisonTypeError(
                self.name,
                self.type_,
                value
                )
        else:
            return None

    @lib.t.overload
    def parse(
        self,
        value: lib.t.Any,
        raise_validation_error: bool,
        ) -> typ.AnyType | lib.Never: ...
    @lib.t.overload
    def parse(
        self,
        value: lib.t.Any,
        raise_validation_error: bool = True,
        ) -> typ.AnyType | lib.Never: ...
    def parse(
        self,
        value: lib.t.Any,
        raise_validation_error: bool = True,
        ) -> lib.t.Optional[typ.AnyType] | lib.Never:
        """
        Return correctly typed value if possible, `None` otherwise, or \
        [optionally] raise an error if an invalid value is passed, the \
        method's default behavior.

        """

        self.type_ = typ.utl.hint.finalize_type(self.type_)  # type: ignore[arg-type]

        parsed = core.codecs.utl.parse(value, self.type_)
        if isinstance(parsed, core.codecs.enm.ParseErrorRef):
            if raise_validation_error:
                raise exc.TypeValidationError(self.name, self.type_, parsed)
            else:
                return None
        else:
            return parsed

    @property
    def factory(self) -> lib.t.Callable[[], typ.AnyType]:
        """Return callable returning default value for field."""

        if (
            (
                key := Constants.DELIM.join(
                    (
                        str(self.name).lower(),
                        getattr(
                            self.type_,
                            '__name__',
                            self.type_.__class__.__name__
                            ),
                        str(self.default),
                        'factory'
                        )
                    )
                )
            not in Constants.FACTORY_CACHE
            ):
            if callable(self.default):
                Constants.FACTORY_CACHE[key] = lambda: self.default()  # type: ignore[operator]
            elif (
                typ.utl.check.is_immutable_type(
                    self.type_ or type(self.default)
                    )
                ):
                Constants.FACTORY_CACHE[key] = lambda: self.default
            else:
                Constants.FACTORY_CACHE[key] = lambda: lib.copy.deepcopy(self.default)

        value: lib.t.Callable[[], typ.AnyType] = Constants.FACTORY_CACHE[key]
        return value
