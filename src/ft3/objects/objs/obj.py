"""Object module."""

__all__ = (
    'Object',
    'ObjectBase',
    )

from ... import core

from .. import cfg
from .. import exc
from .. import lib
from .. import metas
from .. import typ
from .. import utl

if lib.t.TYPE_CHECKING:  # pragma: no cover
    from ... import api
    from .. import queries


class Constants(cfg.Constants):
    """Constant values specific to this file."""


@lib.dataclass_transform(
    field_specifiers=(typ.Field, )
    )
class ObjectBase(metaclass=metas.Meta):
    """Base for Objects, used for typing purposes."""

    __annotations__: typ.SnakeDict
    __dataclass_fields__: lib.t.ClassVar[typ.DataClassFields]
    __heritage__: lib.t.ClassVar[tuple['metas.Meta', ...]]
    __operations__: lib.t.ClassVar[
        dict[
            typ.string[typ.snake_case],
            lib.t.Callable[
                ['api.events.obj.Request', ],
                lib.t.Optional[typ.Object]
                | lib.t.Optional[list[typ.Object]]
                | str
                ]
            ]
        ]

    enumerations: lib.t.ClassVar[dict[str, tuple[typ.Primitive, ...]]]
    fields: lib.t.ClassVar[typ.FieldsTuple]
    hash_fields: lib.t.ClassVar[typ.FieldsTuple]

    @classmethod
    def DELETE(
        cls,
        fn: lib.t.Callable[['api.events.obj.Request'], None]
        ) -> lib.t.Callable[['api.events.obj.Request'], None]:
        cls.__operations__[Constants.DELETE] = fn
        return fn

    @classmethod
    def GET(
        cls,
        fn: lib.t.Callable[
            ['api.events.obj.Request'],
            list[lib.Self] | lib.Self | str
            ]
        ) -> lib.t.Callable[
            ['api.events.obj.Request'],
            list[lib.Self] | lib.Self | str
            ]:
        cls.__operations__[Constants.GET] = fn
        return fn

    @classmethod
    def OPTIONS(
        cls,
        fn: lib.t.Callable[['api.events.obj.Request'], None]
        ) -> lib.t.Callable[['api.events.obj.Request'], None]:  # pragma: no cover
        cls.__operations__[Constants.OPTIONS] = fn
        return fn

    @classmethod
    def PATCH(
        cls,
        fn: 'lib.t.Callable[[api.events.obj.Request], lib.Self]'
        ) -> 'lib.t.Callable[[api.events.obj.Request], lib.Self]':
        cls.__operations__[Constants.PATCH] = fn
        return fn

    @classmethod
    def POST(
        cls,
        fn: 'lib.t.Callable[[api.events.obj.Request], lib.Self]'
        ) -> 'lib.t.Callable[[api.events.obj.Request], lib.Self]':
        cls.__operations__[Constants.POST] = fn
        return fn

    @classmethod
    def PUT(
        cls,
        fn: 'lib.t.Callable[[api.events.obj.Request], lib.Self]'
        ) -> 'lib.t.Callable[[api.events.obj.Request], lib.Self]':
        cls.__operations__[Constants.PUT] = fn
        return fn

    def __repr__(self) -> str:
        """
        Return constructor represented as a neatly formatted JSON string.

        """

        return core.codecs.utl.serialize(self)

    def __init__(
        self,
        class_as_dict: lib.t.Optional[dict[typ.AnyString, lib.t.Any]] = None,
        /,
        **kwargs: lib.t.Any
        ):
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

        for cname, field in self.__dataclass_fields__.items():
            if cname not in ckwargs:
                ckwargs[cname] = field.factory()

        for cname, value in ckwargs.items():
            setattr(self, cname, value)

        self.__post_init__()

    def __post_init__(self) -> None:
        """Method that will always run after instantiation."""

    def __setattr__(self, __name: str, __value: lib.t.Any) -> None:
        """Set attribute with type validation."""

        if typ.utl.check.is_field(self):
            object.__setattr__(self, __name, __value)
        elif core.strings.utl.is_snake_case_string(__name):
            self.__dataclass_fields__[__name].__set__(self, __value)

        return None

    def __delitem__(self, __key: lib.t.Any) -> lib.t.Optional[lib.Never]:
        """Reset current value for key to field default."""

        if (
            isinstance(__key, str)
            and (k := core.strings.utl.cname_for(__key, self.fields))
            ):
            self.pop(k, None)
            return None
        else:
            raise KeyError(__key)

    def __getitem__(self, __key: lib.t.Any, /) -> lib.t.Any:
        """Return field value dict style."""

        if (
            isinstance(__key, str)
            and (k := core.strings.utl.cname_for(__key, self.fields))
            ):
            value = getattr(
                self,
                k,
                (
                    field_.factory()
                    if typ.utl.check.is_field(
                        field_ := self.__dataclass_fields__[k]
                        )
                    else field_['default']
                    )
                )
            if (
                isinstance(value, Object)
                and (
                    callers := lib.t.cast(
                        lib.types.FrameType,
                        lib.t.cast(
                            lib.types.FrameType,
                            lib.inspect.currentframe()
                            ).f_back
                        ).f_code.co_names
                    )
                and 'dict' in callers
                and (
                    callers[0] == 'dict'
                    or (
                        callers[callers.index('dict') - 1]
                        != 'to_dict'
                        )
                    )
                ):
                return value.to_dict()
            elif (
                typ.utl.check.is_array(value)
                and (
                    callers := lib.t.cast(
                        lib.types.FrameType,
                        lib.t.cast(
                            lib.types.FrameType,
                            lib.inspect.currentframe()
                            ).f_back
                        ).f_code.co_names
                    )
                and 'dict' in callers
                and (
                    callers[0] == 'dict'
                    or (
                        callers[callers.index('dict') - 1]
                        != 'to_dict'
                        )
                    )
                ):
                return value.__class__(
                    item.to_dict()
                    if typ.utl.check.is_object(item)
                    else item
                    for item
                    in value
                    )
            elif (
                typ.utl.check.is_mapping(value)
                and (
                    callers := lib.t.cast(
                        lib.types.FrameType,
                        lib.t.cast(
                            lib.types.FrameType,
                            lib.inspect.currentframe()
                            ).f_back
                        ).f_code.co_names
                    )
                and 'dict' in callers
                and (
                    callers[0] == 'dict'
                    or (
                        callers[callers.index('dict') - 1]
                        != 'to_dict'
                        )
                    )
                ):
                return value.__class__(
                    {
                        (
                            k.to_dict()
                            if typ.utl.check.is_object(k)
                            else k
                            ): (
                                v.to_dict()
                                if typ.utl.check.is_object(v)
                                else v
                                )
                        for k, v
                        in value.items()
                        }
                    )
            else:
                return value
        else:
            raise KeyError(__key)

    def __setitem__(
        self,
        __key: str,
        __value: lib.t.Any
        ) -> lib.t.Optional[lib.Never]:
        """Set field value dict style."""

        if (k := core.strings.utl.cname_for(__key, self.fields)):
            setattr(self, k, __value)
            return None
        else:
            raise KeyError(__key)

    def __contains__(self, __key: lib.t.Any, /) -> bool:
        """Return `True` if `__key` is a field for self."""

        return bool(core.strings.utl.cname_for(__key, self.fields))

    def __len__(self) -> int:
        """Return count of fields."""

        return len(self.fields)

    def __hash__(self) -> int:
        return hash(
            Constants.DELIM.join(
                [
                    '.'.join((k, str(v)))
                    for k
                    in self.hash_fields
                    if (v := self.get(k))
                    ]
                )
            )

    def __bool__(self) -> bool:
        """Determine truthiness by diff with default field values."""

        return bool(self - self.__class__())

    @lib.t.overload
    def __eq__(
        self,
        other: 'typ.AnyField[lib.t.Any]'
        ) -> bool: ...
    @lib.t.overload
    def __eq__(
        self: object,
        other: object
        ) -> bool: ...
    @lib.t.overload
    def __eq__(
        self,
        other: lib.t.Any
        ) -> lib.t.Union[bool, 'queries.EqQueryCondition', lib.Never]: ...
    def __eq__(
        self,
        other: lib.t.Union[object, lib.t.Any]
        ) -> lib.t.Union[bool, 'queries.EqQueryCondition', lib.Never]:

        return hash(self) == hash(other)

    @lib.t.overload
    def __ne__(
        self,
        other: 'typ.AnyField[lib.t.Any]'
        ) -> bool: ...
    @lib.t.overload
    def __ne__(
        self: object,
        other: object
        ) -> bool: ...
    @lib.t.overload
    def __ne__(
        self,
        other: lib.t.Any
        ) -> lib.t.Union[bool, 'queries.NeQueryCondition', lib.Never]: ...
    def __ne__(
        self,
        other: lib.t.Union[object, lib.t.Any, 'typ.AnyField[lib.t.Any]']
        ) -> lib.t.Union[bool, 'queries.NeQueryCondition', lib.Never]:

        return hash(self) != hash(other)

    def __sub__(self, other: lib.Self) -> typ.SnakeDict:
        """Calculate diff between same object types."""

        diff: typ.SnakeDict = {}
        for field in self.fields:
            if self[field] != other[field]:
                diff[field] = other[field]

        return diff

    def __iter__(
        self
        ) -> lib.t.Iterator[tuple[typ.string[typ.snake_case], lib.t.Any]]:
        """
        Return an iterator of keys and values like a `dict`.

        ---

        Removes any suffixed underscores from field names (`_`).

        """

        for k, v in self.items():
            yield k, v

    @lib.t.overload
    def __lshift__(
        self,
        other: typ.obj.ObjectLike,
        ) -> lib.Self: ...
    @lib.t.overload
    def __lshift__(
        self,
        other: lib.t.Any,
        ) -> lib.t.Union[
            'queries.ContainsQueryCondition',
            lib.Self,
            lib.Never
            ]: ...
    def __lshift__(
        self,
        other: typ.obj.ObjectLike | lib.t.Any
        ) -> lib.t.Union[
            lib.Self,
            'queries.ContainsQueryCondition',
            lib.Never
            ]:
        """
        Interpolate values from other if populated with non-default \
        and return a new instance without mutating self or other.

        """

        if not all(field in other for field in self.__dataclass_fields__):
            raise exc.InvalidObjectComparisonError(self, other)
        else:
            object_ = self.__class__()
            for field, __field in self.__dataclass_fields__.items():
                if typ.utl.check.is_field(self):
                    default_value = __field['default']
                else:
                    default_value = __field.factory()
                if (
                    self[field] == default_value
                    and other[field] != default_value
                    ):
                    object_[field] = other[field]
                else:
                    object_[field] = self[field]
            return object_

    def __rshift__(
        self,
        other: typ.obj.ObjectLike
        ) -> lib.Self:
        """
        Overwrite values from other if populated with non-default \
        and return a new instance without mutating self or other.

        """

        object_ = self.__class__()
        for field, __field in self.__dataclass_fields__.items():
            if other[field] != __field.factory():
                object_[field] = other[field]
            else:
                object_[field] = self[field]
        return object_

    def __reversed__(self) -> lib.t.Iterator[typ.string[typ.snake_case]]:
        """
        Return a reversed iterator of keys like a `dict`.

        ---

        Removes any suffixed underscores from field names (`_`).
        
        """

        for field in reversed(sorted(self.keys())):
            yield field

    def __copy__(self) -> lib.Self:
        """Return a copy of the instance."""

        return self.__class__(dict(self))

    def __deepcopy__(
        self,
        memo: lib.t.Optional[typ.AnyDict] = None
        ) -> lib.Self:
        """Return a deep copy of the instance."""

        return self.__copy__()

    def __getstate__(self) -> typ.AnyDict:
        return dict(self)

    def __setstate__(self, state: typ.AnyDict) -> None:
        other = self.__class__(state)
        self.update(other)
        return None

    def __ior__(self, other: lib.Self | typ.AnyDict, /) -> lib.Self:
        self.update(other)
        return self

    @property
    def as_response(self) -> typ.CamelDict:
        """
        Return self as a `camelCase` dictionary.

        ---

        Includes `null` values as well as all `read_only` fields.

        """

        return self.to_dict(
            camel_case=True,
            include_null=True,
            include_private=False,
            include_write_only=False,
            include_read_only=True
            )

    def get(
        self,
        __key: typ.AnyString,
        __default: typ.AnyType = None
        ) -> lib.t.Any | typ.AnyType:
        """Return value by key if exists, otherwise default."""

        if (k := core.strings.utl.cname_for(__key, self.fields)):
            return self[k]
        else:
            return __default

    def copy(self) -> lib.Self:
        """Return a copy of the instance."""

        return self.__copy__()

    @classmethod
    def fromkeys(
        cls,
        __keys: lib.t.Iterable[typ.string[typ.snake_case]],
        /
        ) -> lib.Self:
        """
        Return an object instance from keys like a `dict`.

        ---

        Removes any suffixed underscores from field names (`_`).

        """

        return cls()

    @classmethod
    def keys(cls) -> lib.t.KeysView[typ.string[typ.snake_case]]:
        """
        Return an iterator of keys like a `dict`.

        ---

        Removes any suffixed underscores from field names (`_`).

        """

        k_: typ.string[typ.snake_case]
        return lib.t.KeysView(
            {
                k_: v
                for k, v
                in cls.__dataclass_fields__.items()
                if (k_ := k.rstrip('_'))
                }
            )

    def items(self) -> lib.t.ItemsView[typ.string[typ.snake_case], lib.t.Any]:
        """
        Return an iterator of keys and values like a `dict`.

        ---

        Removes any suffixed underscores from field names (`_`).

        """

        return self.to_dict().items()

    def pop(
        self,
        __key: str,
        /,
        __default: typ.AnyType = Constants.UNDEFINED
        ) -> typ.AnyType | lib.t.Any | lib.Never:
        """Return current value for key and reset instance value to field default."""

        if (cname := core.strings.utl.cname_for(__key, self.fields)):
            value = self[cname]
            self[cname] = self.__dataclass_fields__[cname].factory()
            return value
        elif __default == Constants.UNDEFINED:
            raise KeyError
        else:
            return __default

    def setdefault(
        self,
        __key: str,
        __value: lib.t.Any
        ) -> lib.t.Optional[lib.Never]:
        """Set value for key if unset; otherwise do nothing."""

        if (
            (k := core.strings.utl.cname_for(__key, self.fields))
            and (
                (
                    _value := self.get(k, Constants.UNDEFINED)
                    ) == Constants.UNDEFINED
                or _value == self.__dataclass_fields__[k].factory()
                )
            ):
            self[k] = __value
        elif not k:
            raise KeyError

        return None

    def update(self, other: lib.Self | typ.AnyDict, /) -> None:
        """Update values like a `dict`."""

        for k, v in other.items():
            if core.strings.utl.cname_for(k, self.fields):
                self[k] = v

        return None

    def values(self) -> lib.t.ValuesView[lib.t.Any]:
        """Return an iterator of values like a `dict`."""

        return lib.t.ValuesView(dict(self))

    @lib.t.overload
    def to_dict(
        self,
        camel_case: lib.t.Literal[False] = False,
        include_null: bool = True,
        include_private: bool = True,
        include_write_only: bool = True,
        include_read_only: bool = False
        ) -> typ.SnakeDict: ...
    @lib.t.overload
    def to_dict(
        self,
        camel_case: lib.t.Literal[True],
        include_null: bool,
        include_private: bool,
        include_write_only: bool,
        include_read_only: bool
        ) -> typ.CamelDict: ...
    @lib.t.overload
    def to_dict(
        self,
        camel_case: bool,
        include_null: bool,
        include_private: bool,
        include_write_only: bool,
        include_read_only: bool
        ) -> 'typ.SnakeDict | typ.CamelDict': ...
    def to_dict(
        self,
        camel_case: bool = False,
        include_null: bool = True,
        include_private: bool = True,
        include_write_only: bool = True,
        include_read_only: bool = False
        ) -> 'typ.SnakeDict | typ.CamelDict':
        """
        Same as `dict(Object)`, but gives fine-grained control over \
        casing and inclusion of `null` values.

        ---

        If specified, keys may optionally be converted to camelCase.

        `None` values may optionally be discarded as well.

        ---

        Removes any suffixed underscores from field names (`_`) and \
        recursively pops any key, value pairs prefixed with single \
        underscores (`_`).

        """

        d = {
            k: v
            for k, field
            in self.__dataclass_fields__.items()
            if (
                (v := self[k]) is not None
                or (include_null and v is None)
                )
            and (include_private or utl.is_public_field(k))
            and (include_write_only or not field.get('write_only'))
            and (include_read_only or not field.get('read_only'))
            }
        as_dict: typ.SnakeDict = {}
        for key, value in d.items():
            if isinstance(value, ObjectBase):
                as_dict[key] = value.to_dict(
                    camel_case,
                    include_null,
                    include_private,
                    include_write_only,
                    include_read_only
                    )
            elif typ.utl.check.is_array(value):
                as_dict[key] = value.__class__(
                    (
                        v.to_dict(
                            camel_case,
                            include_null,
                            include_private,
                            include_write_only,
                            include_read_only
                            )
                        if isinstance(v, Object)
                        else v
                        for v
                        in value
                        if (v is not None or include_null)
                        )
                    )
            elif typ.utl.check.is_mapping(value):
                as_dict[key] = value.__class__(
                    **{
                        (
                            core.strings.utl.snake_case_to_camel_case(k)
                            if (camel_case and isinstance(k, str))
                            else k
                            ): (
                                v.to_dict(
                                    camel_case,
                                    include_null,
                                    include_private,
                                    include_write_only,
                                    include_read_only
                                    )
                                if isinstance(v, Object)
                                else v
                                )
                        for k, v
                        in value.items()
                        if (include_private or utl.is_public_field(k))
                        and (v is not None or include_null)
                        }
                    )
            else:
                as_dict[key] = value

        if camel_case:
            return {
                core.strings.utl.snake_case_to_camel_case(k): v
                for k, v
                in as_dict.items()
                }
        else:
            k_: typ.string[typ.snake_case]
            snake_dict: typ.SnakeDict = {
                k_: v
                for k, v
                in as_dict.items()
                if (k_ := k.rstrip('_'))
                }
            return snake_dict


@lib.dataclass_transform(
    kw_only_default=True,
    field_specifiers=(typ.Field, )
    )
class Object(ObjectBase):
    """
    Base Object.

    ---

    Usage
    -----

    * Subclass to create objects for your application.

    General Recommendations
    -----------------------

    * Ideally, objects should be 1:1 with their counterparts in the \
    data store from which they are originally sourced (even \
    if that data store is your own database, and even if that \
    data is not ostensibly stored in a 1:1 manner, as is the case \
    with most relational databases).
        \
        * For example, if there is a SQL table called `pets` \
        with the schema below, you would want to create \
        a corresponding `python representation` similar to \
        the following.

    #### pets table

    ```
    | id  | name     | type   |
    | --- | -------- | ------ |
    | a1  | fido     | dog    |
    | a2  | garfield | cat    |
    | a3  | sophie   | dog    |
    | a4  | stripes  | turtle |

    ```

    #### python representation

    ```python
    import ft3


    class Pet(ft3.Object):
        \"""A pet.\"""

        id_: ft3.Field[str] # Trailing underscores are special
                             # in ft3, check the documentation
                             # below for more detail.
        name: ft3.Field[str] = 'Fido'  # Setting = 'Fido' will mean that
                                       # all Pet() instances will be
                                       # named 'Fido' by default.
        type: ft3.Field[str]  # You can make a field 'required' by
                              # not specifying a default value.

    ```

    ---

    Special Rules
    -------------

    #### Default Values
    Subclassed (derivative) objects should include default values for \
    all fields specified. In cases where a default value is not specified, \
    `None` will be used instead and the field will be assumed to be \
    'required' for all downstream purposes (ex. as a query parameter \
    for HTTP requests) unless otherwise specified explicitly.

    #### Type Annotations
    Type annotations are required and must be a generic `Field[type]`. \
    For example: `Field[int]`, `Field[str]`, `Field[str | bool]`.

    * Not only is this best practice, these are leveraged downstream \
    to do things like auto-document and auto-generate API's.

    #### Uniform Casing
    ALL Fields must be either camelCase or snake_case, with the only \
    exception being that fields may begin with an underscore '_', so long \
    as all following characters adhere to camelCase or snake_case conventions.

    #### Underscore Prefix for Private Fields
    Fields that begin with an underscore '_' will be ignored on \
    conversion to / from DBO, REST, and JSON representations, \
    unless the field ends with 'id' or 'id_' (case insensitive), \
    in which case it will still be converted.

    * This follows the broader pattern of flagging methods and \
    attributes as private / internal to a system with a preceding \
    underscore. It should be expected that end users of your \
    system will not need to interact with these fields.

    #### Underscore Suffix for Reserved Keyword Fields
    Fields with a trailing underscore '_' will automatically have \
    the trailing underscore removed on conversion to / from \
    DBO, REST, and JSON representations.

    * This allows for python keywords, such as `in_`, to be used \
    as object fields, where they would otherwise raise errors \
    without the proceeding underscore.

    * On translation to and from dictionaries, keys without \
    underscores will still be checked against these fields -- \
    so, a dictionary with key `in` will correctly map to the `in_` \
    field on the Object. See below for more detail.

    ```python
    import ft3


    class Pet(ft3.Object):
        \"""A pet.\"""

        id_: ft3.Field[str]
        _alternate_id: ft3.Field[str]

        name: ft3.Field[str]
        type: ft3.Field[str]
        in_: ft3.Field[str]
        is_tail_wagging: ft3.Field[bool] = True


    # This means each of the below will work.
    bob_the_dog = Pet(
        id='abc123',
        _alternate_id='dog1',
        name='Bob',
        type='dog',
        in_='timeout',
        is_tail_wagging=False
        )
    bob_the_dog = Pet(
        {
            'id': 'abc123',
            '_alternate_id': 'dog1',
            'name': 'Bob',
            'type': 'dog',
            'in': 'timeout',
            'is_tail_wagging': False
            }
        )

    # And so would this, since translation
    # automatically handles camelCase to
    # snake_case conversions.
    bob_the_dog = Pet(
        {
            'id': 'abc123',
            'alternateId': 'dog1',
            'name': 'Bob',
            'type': 'dog',
            'in': 'timeout',
            'isTailWagging': False
            }
        )

    ```

    ---

    Special Method Usage
    --------------------

    Objects have been designed to be almost interchangable with \
    dictionaries. The primary difference is that values cannot be \
    assigned to keys unless you define them on the Object's class \
    definition itself.
    * This is done to automatically maximize the efficiency of your \
    application's memory footprint. Feel free to read more about \
    python [slots](https://wiki.python.org/moin/UsingSlots) to better \
    understand why this is necessary.

    ```python
    import ft3


    class Pet(ft3.Object):  # noqa

        name: ft3.Field[str]


    dog = Pet(name='Fido')

    # The below would return the string, 'Fido'.
    dog['name']

    # The following would set the dog's name to something else.
    dog.setdefault('name', 'Arnold')
    assert dog.name == 'Arnold'
    dog.setdefault('name', 'Buddy')
    assert dog.name == 'Arnold'
    dog['name'] = 'Buddy'
    assert dog.name == 'Buddy'
    assert dog['name'] == 'Buddy'

    # The following all work exactly the same as with a dictionary.
    # (in the below, key will be 'name' and value 'Fido').
    for key, value in dog.items():
        break

    for key in dog.keys():
        break

    for value in dog.values():
        break

    # But the following will raise a KeyError.
    dog['field_that_does_not_exist'] = 'Buddy'

    # And so would this, since fields can only be added
    # or removed on the class definition of Pet itself.
    dog.setdefault('field_that_does_not_exist', 'Buddy')

    ```

    Object truthiness will evaluate to True if any values for \
    the Object instance are different from default values, \
    otherwise False.

    ```python
    if Object:
    ```

    Objects are designed to display themselves as neatly \
    formatted JSON on calls to `__repr__`.

    ```python
    print(Object)
    ```

    Updates Object1 with values from Object2 if they \
    are a non-default value for the object.

    ```python
    Object1 << Object2
    ```

    Overwrites Object1 values with those from Object2 \
    if they are a non-default value for the object.

    ```python
    Object1 >> Object2
    ```

    Returns a dictionary with {fieldName: fieldValue2} for \
    any fields that differ between the two Objects.

    ```python
    Object1 - Object2
    ```

    Get value for Object field.

    ```python
    value = Object['field']
    ```

    Set value for Object field.

    ```python
    Object['field'] = value
    ```

    Returns True if any one of field, _field, field_, or _field_ \
    is a valid field for the Object, otherwise False.

    ```python
    field in Object
    ```

    Same as `len(Object.fields)`.

    ```python
    len(Object)
    ```

    """

    class_as_dict: lib.t.Final[
        lib.t.Optional[dict[typ.AnyString, lib.t.Any]]
        ] = None
    """
    Instantiate class directly from passed `dict` (assumed to be \
    version of class in `dict` form).

    """
