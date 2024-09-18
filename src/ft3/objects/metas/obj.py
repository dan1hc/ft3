"""Metaclass module."""

__all__ = (
    'Meta',
    )

from ... import core

from .. import cfg
from .. import exc
from .. import lib
from .. import typ

from . import utl

if lib.t.TYPE_CHECKING:  # pragma: no cover
    from ... import api
    from .. import fields as fields_


class Constants(cfg.Constants):
    """Constant values specific to this file."""


class Meta(type):
    """Base class constructor."""

    if lib.t.TYPE_CHECKING:  # pragma: no cover
        __annotations__: typ.SnakeDict
        __dataclass_fields__: lib.t.ClassVar[typ.DataClassFields]
        __heritage__: lib.t.ClassVar[tuple['Meta', ...]]
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

    def __new__(
        mcs: type[typ.MetaType],
        __name: str,
        __bases: tuple[type, ...],
        __namespace: dict[typ.AnyString, lib.t.Any],
        **kwargs: lib.t.Any
        ) -> typ.MetaType:
        fields: typ.DataClassFields = {}
        heritage: tuple[type, ...] = __bases
        slots: list[typ.string[typ.snake_case]]
        _slots: tuple[typ.string[typ.snake_case], ...] | str = (
            __namespace.get(Constants.__SLOTS__, ())
            )
        if (
            isinstance(_slots, str)
            and core.strings.utl.is_snake_case_string(_slots)
            ):  # pragma: no cover
            slots = [_slots] if _slots != Constants.CLASS_AS_DICT else []
        elif core.strings.utl.is_snake_case_iterable(_slots):
            slots = [s for s in _slots if s != Constants.CLASS_AS_DICT]
        else:  # pragma: no cover
            slots = []
        module: str = __namespace.get(Constants.__MODULE__, '')
        annotations: typ.SnakeDict
        annotations = __namespace.pop(Constants.__ANNOTATIONS__, {})
        annotations |= {
            k: typ.utl.hint.resolve_type(
                v,
                lib.sys.modules[module].__dict__
                )
            for k, v
            in annotations.items()
            }
        operations: dict[
            typ.string[typ.snake_case],
            lib.t.Callable[
                ['api.events.obj.Request', ],
                lib.t.Optional[typ.Object]
                | lib.t.Optional[list[typ.Object]]
                | str
                ]
            ] = __namespace.pop(Constants.__OPERATIONS__, {})

        base_count = 0
        for _base in reversed(__bases):
            if isinstance(_base, Meta):
                base_count += 1
                fields |= _base.__dataclass_fields__

        __namespace.pop(Constants.CLASS_AS_DICT, None)
        annotations.pop(Constants.CLASS_AS_DICT, None)

        if base_count > 1:
            from .. import objs
            common_annotations: typ.SnakeDict = {}
            common_base_names: list[str] = []
            common_bases: list[type[objs.Object]] = []
            common_namespace: dict[typ.AnyString, lib.t.Any] = {}
            common_slots: list[typ.string[typ.snake_case]] = []
            for _base in reversed(__bases):
                for __base in reversed(_base.__mro__):
                    if (
                        issubclass(__base, objs.Object)
                        and __base is not objs.Object
                        ):
                        if __base.__name__ not in common_base_names:
                            common_base_names.insert(0, __base.__name__)
                            common_bases.insert(0, __base)
                            for slot in __base.__slots__:
                                if slot not in common_slots:
                                    common_slots.append(slot)
                            common_annotations |= __base.__annotations__
                            common_namespace |= __base.__dict__
            common_namespace = {
                k: v
                for k, v
                in common_namespace.items()
                if (
                    utl.is_valid_keyword(k)
                    and k not in common_slots
                    )
                }
            common_namespace[Constants.__ANNOTATIONS__] = common_annotations
            common_namespace[Constants.__SLOTS__] = tuple(common_slots)
            common_base = Meta(
                Constants.DELIM_REBASE.join(common_base_names[:base_count]),
                (objs.Object, ),
                common_namespace
                )
            __bases = (common_base, )

        if module != Constants.OBJECTS_MODULE:
            base_fields = set(fields.keys())
            
            defaults, slots, fields = (
                utl.parse_new_namespace(
                    __namespace,
                    annotations,
                    module,
                    slots,
                    fields
                    )
                )

            for name in defaults:
                __namespace.pop(name)

            slots, fields = (
                utl.parse_new_annotations(
                    __namespace,
                    annotations,
                    module,
                    slots,
                    fields,
                    base_fields
                    )
                )

        fields_tuple = tuple(sorted(fields))

        namespace = {
            Constants.__SLOTS__: tuple(slots),
            **__namespace,
            }

        namespace[Constants.__ANNOTATIONS__] = annotations
        namespace[Constants.__DATACLASS_FIELDS__] = fields
        namespace[Constants.__HERITAGE__] = heritage
        namespace[Constants.__OPERATIONS__] = operations

        namespace[Constants.FIELDS] = fields_tuple
        namespace[Constants.ENUMERATIONS] = (
            utl.get_enumerations_from_fields(fields)
            )
        if module != Constants.FIELDS_MODULE:
            namespace[Constants.HASH_FIELDS] = utl.get_fields_for_hash(fields)
        else:
            namespace[Constants.HASH_FIELDS] = ('name', )

        cls = super().__new__(
            mcs,
            __name,
            __bases,
            namespace,
            **kwargs
            )

        docs = utl.get_attribute_docs(cls)
        for name, field in cls.__dataclass_fields__.items():
            field['description'] = docs.get(name)

        return cls

    def __repr__(cls) -> str:
        """
        Return constructor represented as a neatly formatted JSON string.

        """

        return core.codecs.utl.serialize(cls)

    def __getattribute__(cls, __name: str) -> lib.t.Any:
        __fields: dict[str, 'typ.AnyField[lib.t.Any]'] = (
            type.__getattribute__(cls, '__dataclass_fields__')
            )
        if (field := __fields.get(__name)):
            return field
        elif __name == 'class_as_dict':  # pragma: no cover
            # This clause exists to address sphinx-doc error
            # where sphinx thinks this attribute is otherwise
            # more available / heritable than it really is.
            return {}
        else:
            return super().__getattribute__(__name)

    def __setattr__(
        cls,
        __name: str,
        __value: lib.t.Any
        ) -> lib.t.Optional[lib.Never]:
        if (
            (cname := core.strings.utl.cname_for(__name, cls.fields))
            and not typ.utl.check.is_field(__value)
            ):
            raise exc.IncorrectTypeError(__name, type(__value), __value)
        elif cname:
            cls[__name] = __value
            return None
        else:
            super().__setattr__(__name, __value)
            return None

    @lib.t.overload
    def __getitem__(
        cls,
        __key: typ.AnyString
        ) -> 'fields_.Field[lib.t.Any]' | lib.Never: ...
    @lib.t.overload
    def __getitem__(
        cls,
        __key: type[typ.AnyType]
        ) -> 'typ.Field[typ.AnyType]' | lib.Never: ...
    def __getitem__(
        cls,
        __key: typ.AnyType | type[typ.AnyType]
        ) -> lib.t.Union[
            'fields_.Field[lib.t.Any]',
            'typ.Field[typ.AnyType]',
            lib.Never
            ]:
        """Return value dict style."""

        if (
            isinstance(__key, str)
            and core.strings.utl.is_snake_case_string(__key)
            and (k := core.strings.utl.cname_for(__key, cls.fields))
            ):
            return cls.__dataclass_fields__[k]
        elif typ.utl.check.is_field_type(cls):
            return typ.Field(cls, __key)
        else:
            raise KeyError(__key)

    def __contains__(cls, __key: lib.t.Any) -> bool:
        """Return `True` if `__key` is a field for class."""

        return bool(core.strings.utl.cname_for(__key, cls.fields))

    def __iter__(cls) -> lib.t.Iterator[typ.string[typ.snake_case]]:
        """Iterate over field names."""

        for fname in cls.fields:
            yield fname

    def __instancecheck__(cls, __instance: lib.t.Any) -> bool:
        """Instance check that considers slotted heritage."""

        return (
            super().__instancecheck__(__instance)
            or cls in getattr(__instance, '__heritage__', ())
            )

    def __subclasscheck__(cls, __subclass: type[lib.t.Any]) -> bool:
        """Subclass check that considers slotted heritage."""

        return (
            super().__subclasscheck__(__subclass)
            or cls in getattr(__subclass, '__heritage__', ())
            )

    def __setitem__(
        cls,
        __key: str,
        __value: lib.t.Any
        ) -> lib.t.Optional[lib.Never]:
        """Set Field for key dict style."""

        if not typ.utl.check.is_field(__value):
            from .. import fields as fields_
            raise exc.IncorrectTypeError(__key, fields_.Field, __value)
        elif (
            (k := core.strings.utl.cname_for(__key, cls.fields))
            and __value['name'] != k
            ):
            raise exc.InvalidFieldRedefinitionError(__value['name'])
        elif k and not issubclass(
            __value['type'],
            typ.utl.check.get_checkable_types(
                (ftype := cls.__dataclass_fields__[k]['type'])
                )
            ):
            raise exc.IncorrectTypeError(k, ftype, __value['type'])
        elif k and not isinstance(
            __value['default'],
            typ.utl.check.get_checkable_types(
                (ftype := cls.__dataclass_fields__[k]['type'])
                )
            ):
            raise exc.IncorrectDefaultTypeError(
                k,
                ftype,
                __value['default']
                )
        elif k is not None:
            value_: 'fields_.Field[lib.t.Any]' = __value
            cls.__dataclass_fields__[k].update(value_)  # type: ignore[arg-type]
            return None
        else:
            raise exc.InvalidFieldAdditionError(__key)
