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

	HANDLED: dict[str, type] = {}
	"""Every Object class that has had an HTTP handler attached."""


@lib.dataclass_transform(field_specifiers=(typ.Field,))
class ObjectBase(metaclass=metas.Meta):
	"""Base for Objects, used for typing purposes."""

	__annotations__: typ.SnakeDict
	__dataclass_fields__: lib.t.ClassVar[typ.DataClassFields]
	__heritage__: lib.t.ClassVar[tuple['metas.Meta', ...]]
	__operations__: lib.t.ClassVar[
		dict[
			typ.string[typ.snake_case],
			lib.t.Callable[
				[
					'api.events.obj.Request',
				],
				lib.t.Optional[typ.Object]
				| lib.t.Optional[list[typ.Object]]
				| str,
			],
		]
	]

	enumerations: lib.t.ClassVar[dict[str, tuple[typ.Primitive, ...]]]
	fields: lib.t.ClassVar[typ.FieldsTuple]
	hash_fields: lib.t.ClassVar[typ.FieldsTuple]

	@classmethod
	def _add_operation(
		cls,
		k: 'typ.string[typ.snake_case]',
		fn: lib.t.Callable[..., lib.t.Any],
	) -> None:
		"""Attach an HTTP handler and remember that this class has one."""

		cls.__operations__[k] = fn
		Constants.HANDLED['.'.join((cls.__module__, cls.__qualname__))] = cls

	@classmethod
	def DELETE(
		cls, fn: lib.t.Callable[['api.events.obj.Request'], None]
	) -> lib.t.Callable[['api.events.obj.Request'], None]:
		k: typ.string[typ.snake_case] = '_'.join(
			(cls.__name__.lower(), Constants.DELETE)
		)
		cls._add_operation(k, fn)
		return fn

	@classmethod
	def GET(
		cls,
		fn: lib.t.Callable[
			['api.events.obj.Request'], list[lib.Self] | lib.Self | str
		],
	) -> lib.t.Callable[
		['api.events.obj.Request'], list[lib.Self] | lib.Self | str
	]:
		k: typ.string[typ.snake_case]
		tp = typ.utl.hint.finalize_type(fn.__annotations__['return'])
		if any(
			issubclass(tp_, list)
			for tp_ in typ.utl.check.get_checkable_types(tp)
		) or (typ.utl.check.is_object_type(tp) and not tp.hash_fields):
			k = Constants.GET
		else:
			k = '_'.join(  # pragma: no cover
				(cls.__name__.lower(), Constants.GET)
			)
		cls._add_operation(k, fn)
		return fn

	@classmethod
	def OPTIONS(
		cls, fn: lib.t.Callable[['api.events.obj.Request'], None]
	) -> lib.t.Callable[['api.events.obj.Request'], None]:  # pragma: no cover
		k: typ.string[typ.snake_case]
		k = '_'.join((cls.__name__.lower(), Constants.OPTIONS))
		cls._add_operation(k, fn)
		return fn

	@classmethod
	def PATCH(
		cls, fn: 'lib.t.Callable[[api.events.obj.Request], lib.Self]'
	) -> 'lib.t.Callable[[api.events.obj.Request], lib.Self]':
		k: typ.string[typ.snake_case]
		k = '_'.join((cls.__name__.lower(), Constants.PATCH))
		cls._add_operation(k, fn)
		return fn

	@classmethod
	def POST(
		cls, fn: 'lib.t.Callable[[api.events.obj.Request], lib.Self]'
	) -> 'lib.t.Callable[[api.events.obj.Request], lib.Self]':
		cls._add_operation(Constants.POST, fn)
		return fn

	@classmethod
	def PUT(
		cls, fn: 'lib.t.Callable[[api.events.obj.Request], lib.Self]'
	) -> 'lib.t.Callable[[api.events.obj.Request], lib.Self]':
		k: typ.string[typ.snake_case]
		k = '_'.join((cls.__name__.lower(), Constants.PUT))
		cls._add_operation(k, fn)
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
		**kwargs: lib.t.Any,
	):
		ckwargs: dict[str, lib.t.Any] = {}
		unknown: list[str] = []
		supplied: list[tuple[lib.t.Any, lib.t.Any]] = list(kwargs.items())
		if isinstance(class_as_dict, lib.t.Mapping):
			supplied.extend(class_as_dict.items())
		for name, value in supplied:
			if cname := core.strings.utl.cname_for(name, self.fields):
				ckwargs[cname] = value
			else:
				unknown.append(str(name))

		for name in unknown:
			from ... import loggers

			loggers.utl.warn_once(
				(type(self).__name__, 'unknown_key', name),
				{
					'unknown.key': {
						'object': type(self).__name__,
						'key': name,
						'outcome': 'dropped',
						'fix': 'declare a Field for it or stop sending it',
					}
				},
			)

		for cname, field in self.__dataclass_fields__.items():
			if cname not in ckwargs:
				ckwargs[cname] = field.factory()

		if getattr(type(self), Constants.__STRICT__, False):
			for cname, field in self.__dataclass_fields__.items():
				if field.required and ckwargs.get(cname) is None:
					raise exc.MissingRequiredFieldError(
						type(self).__name__, cname
					)

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

		if isinstance(__key, str) and (
			k := core.strings.utl.cname_for(__key, self.fields)
		):
			self.pop(k, None)
			return None
		else:
			raise KeyError(__key)

	def __getitem__(self, __key: lib.t.Any, /) -> lib.t.Any:
		"""
		Return a field value dict style, exactly as stored.

		---

		Nested Objects are returned as Objects. Use `to_dict()` for a \
		plain-data tree.

		"""

		if isinstance(__key, str) and (
			k := core.strings.utl.cname_for(__key, self.fields)
		):
			field_ = self.__dataclass_fields__[k]
			return getattr(
				self,
				k,
				(
					field_.factory()
					if typ.utl.check.is_field(field_)
					else field_['default']
				),
			)
		else:
			raise KeyError(__key)

	def __setitem__(
		self, __key: str, __value: lib.t.Any
	) -> lib.t.Optional[lib.Never]:
		"""Set field value dict style."""

		if k := core.strings.utl.cname_for(__key, self.fields):
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
					for k in self.hash_fields
					if (v := self.get(k))
				]
			)
		)

	def __bool__(self) -> bool:
		"""
		True if any field differs from its default.

		---

		Never constructs a default instance, so it cannot raise for \
		classes with required or constrained fields.

		"""

		for name, field in self.__dataclass_fields__.items():
			factory = getattr(field, 'factory', None)
			default = factory() if callable(factory) else field.get('default')
			if self[name] != default:
				return True
		return False

	@lib.t.overload
	def __eq__(self, other: 'typ.AnyField[lib.t.Any]') -> bool: ...
	@lib.t.overload
	def __eq__(self: object, other: object) -> bool: ...
	@lib.t.overload
	def __eq__(
		self, other: lib.t.Any
	) -> lib.t.Union[bool, 'queries.EqQueryCondition', lib.Never]: ...
	def __eq__(
		self, other: lib.t.Union[object, lib.t.Any]
	) -> lib.t.Union[bool, 'queries.EqQueryCondition', lib.Never]:
		try:
			return hash(self) == hash(other)
		except TypeError:
			return False

	@lib.t.overload
	def __ne__(self, other: 'typ.AnyField[lib.t.Any]') -> bool: ...
	@lib.t.overload
	def __ne__(self: object, other: object) -> bool: ...
	@lib.t.overload
	def __ne__(
		self, other: lib.t.Any
	) -> lib.t.Union[bool, 'queries.NeQueryCondition', lib.Never]: ...
	def __ne__(
		self, other: lib.t.Union[object, lib.t.Any, 'typ.AnyField[lib.t.Any]']
	) -> lib.t.Union[bool, 'queries.NeQueryCondition', lib.Never]:
		return not self.__eq__(other)

	def __sub__(self, other: lib.Self) -> typ.SnakeDict:
		"""Calculate diff between same object types."""

		diff: typ.SnakeDict = {}
		for field in self.fields:
			if self[field] != other[field]:
				diff[field] = other[field]

		return diff

	def __iter__(
		self,
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
		'queries.ContainsQueryCondition', lib.Self, lib.Never
	]: ...
	def __lshift__(
		self, other: typ.obj.ObjectLike | lib.t.Any
	) -> lib.t.Union[lib.Self, 'queries.ContainsQueryCondition', lib.Never]:
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

	def __rshift__(self, other: typ.obj.ObjectLike) -> lib.Self:
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
		self, memo: lib.t.Optional[dict[int, lib.t.Any]] = None
	) -> lib.Self:
		"""
		Return a deep copy of the instance.

		---

		Every field value, including `read_only` and private fields, \
		is deep-copied, so nothing nested is shared with the original.

		"""

		memo = {} if memo is None else memo
		return self.__class__(
			{name: lib.copy.deepcopy(self[name], memo) for name in self.fields}
		)

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

		Omits `null` values, private fields, and `write_only` fields; \
		includes `read_only` fields.

		"""

		return self.to_dict(
			camel_case=True,
			include_null=False,
			include_private=False,
			include_write_only=False,
			include_read_only=True,
		)

	def get(
		self, __key: typ.AnyString, __default: typ.AnyType = None
	) -> lib.t.Any | typ.AnyType:
		"""Return value by key if exists, otherwise default."""

		if k := core.strings.utl.cname_for(__key, self.fields):
			return self[k]
		else:
			return __default

	def copy(self) -> lib.Self:
		"""Return a copy of the instance."""

		return self.__copy__()

	@classmethod
	def fromkeys(
		cls, __keys: lib.t.Iterable[typ.string[typ.snake_case]], /
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
				for k, v in cls.__dataclass_fields__.items()
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
		self, __key: str, /, __default: typ.AnyType = Constants.UNDEFINED
	) -> typ.AnyType | lib.t.Any | lib.Never:
		"""
        Return current value for key and reset instance value to field \
        default.

        """

		if cname := core.strings.utl.cname_for(__key, self.fields):
			value = self[cname]
			self[cname] = self.__dataclass_fields__[cname].factory()
			return value
		elif __default == Constants.UNDEFINED:
			raise KeyError
		else:
			return __default

	def setdefault(
		self, __key: str, __value: lib.t.Any
	) -> lib.t.Optional[lib.Never]:
		"""Set value for key if unset; otherwise do nothing."""

		if (k := core.strings.utl.cname_for(__key, self.fields)) and (
			(_value := self.get(k, Constants.UNDEFINED)) == Constants.UNDEFINED
			or _value == self.__dataclass_fields__[k].factory()
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
		include_read_only: bool = False,
	) -> typ.SnakeDict: ...
	@lib.t.overload
	def to_dict(
		self,
		camel_case: lib.t.Literal[True],
		include_null: bool,
		include_private: bool,
		include_write_only: bool,
		include_read_only: bool,
	) -> typ.CamelDict: ...
	@lib.t.overload
	def to_dict(
		self,
		camel_case: bool,
		include_null: bool,
		include_private: bool,
		include_write_only: bool,
		include_read_only: bool,
	) -> 'typ.SnakeDict | typ.CamelDict': ...
	def to_dict(
		self,
		camel_case: bool = False,
		include_null: bool = True,
		include_private: bool = True,
		include_write_only: bool = True,
		include_read_only: bool = False,
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
			for k, field in self.__dataclass_fields__.items()
			if ((v := self[k]) is not None or (include_null and v is None))
			and (
				include_private
				or utl.is_public_field(k)
				or k in self.hash_fields
			)
			and (include_write_only or not field.get('write_only'))
			and (include_read_only or not field.get('read_only'))
		}
		as_dict: typ.SnakeDict = {}
		for key, value in d.items():
			options = self.__dataclass_fields__[key]
			camel_keys = options.get('camel_case_keys')
			drop_nulls = options.get('drop_null_items')
			if camel_keys is None:
				camel_keys = Constants.LEGACY_WIRE
			if drop_nulls is None:
				drop_nulls = Constants.LEGACY_WIRE
			if isinstance(value, ObjectBase):
				as_dict[key] = value.to_dict(
					camel_case,
					include_null,
					include_private,
					include_write_only,
					include_read_only,
				)
			elif typ.utl.check.is_array(value):
				as_dict[key] = value.__class__(
					(
						v.to_dict(
							camel_case,
							include_null,
							include_private,
							include_write_only,
							include_read_only,
						)
						if isinstance(v, Object)
						else [
							e.to_dict(
								camel_case,
								include_null,
								include_private,
								include_write_only,
								include_read_only,
							)
							for e in v
						]
						if typ.utl.check.is_array_of_object(v)
						else v
						for v in value
						if (v is not None or include_null or not drop_nulls)
					)
				)
			elif typ.utl.check.is_mapping(value):
				as_dict[key] = value.__class__(
					**{
						(
							core.strings.utl.snake_case_to_camel_case(k)
							if (
								camel_case
								and camel_keys
								and isinstance(k, str)
							)
							else k
						): (
							v.to_dict(
								camel_case,
								include_null,
								include_private,
								include_write_only,
								include_read_only,
							)
							if isinstance(v, Object)
							else v
						)
						for k, v in value.items()
						if (
							include_private
							or utl.is_public_field(k)
							or k in self.hash_fields
						)
						and (v is not None or include_null)
					}
				)
			else:
				as_dict[key] = value

		if camel_case:
			return {
				core.strings.utl.snake_case_to_camel_case(k): v
				for k, v in as_dict.items()
			}
		else:
			k_: typ.string[typ.snake_case]
			snake_dict: typ.SnakeDict = {
				k_: v for k, v in as_dict.items() if (k_ := k.rstrip('_'))
			}
			return snake_dict


@lib.dataclass_transform(kw_only_default=True, field_specifiers=(typ.Field,))
class Object(ObjectBase):
	"""
    Base Object: declare it once, get validation, serialization, an API \
    resource, and a log-safe repr from the declaration.

    ---

    ```python
    import ft3


    class Pet(ft3.Object):
        \"""A pet. The docstring is the resource description.\"""

        id_: ft3.Field[str]                # required; serializes as `id`
        name: ft3.Field[str] = 'Fido'      # default
        type_: ft3.Field[str] = ft3.Field(default='dog', enum=['cat', 'dog'])
        _note: ft3.Field[str] = ''         # private: never on the wire

    ```

    Rules enforced at class definition, each with a named error that \
    states the fix:

    * every annotation is `Field[T]`
    * every field name is `snake_case`; trailing underscores are \
    stripped on the wire (`id_` -> `id`) and let reserved names such \
    as `items_` or `in_` be used
    * a field with no default and no `Optional` type is required
    * fields named `*id` or `*key` are hash fields: they define \
    equality, hashing, and path parameters

    Construction accepts a mapping, keyword arguments, or both, with \
    camelCase or snake_case keys. Plain construction is lenient (the \
    hydrate path for stored records); `class Model(Object, strict=True)` \
    enforces every declared constraint on construction and assignment. \
    Unknown keys are dropped with a one-time WARNING.

    `as_response` is the wire shape (camelCase; nulls, private, and \
    write_only fields omitted; read_only included). `to_dict()` is the \
    plain-data tree (snake_case; read_only omitted by default). See \
    `AGENTS.md` for the complete rulebook.
	"""

	class_as_dict: lib.t.Final[
		lib.t.Optional[dict[typ.AnyString, lib.t.Any]]
	] = None
	"""
    Instantiate class directly from passed `dict` (assumed to be \
    version of class in `dict` form).

    """
