"""Field module."""

__all__ = ('Field',)

from ... import core

from .. import cfg
from .. import enm
from .. import exc
from .. import lib
from .. import objs
from .. import typ
from .. import utl

if lib.t.TYPE_CHECKING:  # pragma: no cover
	from ... import api
	from .. import queries


class Constants(cfg.Constants):
	"""Constant values specific to this file."""

	FACTORY_CACHE: dict[str, lib.t.Callable[[], lib.t.Any]] = {}
	CONSTRAINT_KEYS = (
		'enum',
		'min_length',
		'max_length',
		'minimum',
		'maximum',
		'multiple_of',
		'pattern',
		'min_items',
		'max_items',
		'unique_items',
	)
	"""Field keys that constrain a value beyond its type."""
	LOSSLESS = 'lossless'
	"""Pseudo-constraint name for a coercion that would lose data."""
	NUMERIC_TYPES = (int, float, lib.decimal.Decimal)
	"""Types checked for lossless coercion and numeric constraints."""


class Field(objs.Object, lib.t.Generic[typ.AnyType]):
	"""
    A typed, constrained, documented field of an `Object`.

    ---

    Declare a field as a bare default, a `Field(...)`, or a dict of \
    Field keys; a callable default is a factory called per instance.

    ```python
    kind: ft3.Field[str] = ft3.Field(default='dog', enum=['cat', 'dog'])
    count: ft3.Field[int] = {'default': 1, 'minimum': 0, 'maximum': 10}
    tags: ft3.Field[list[str]] = lambda: ['new']

    ```

    ## Options

    * `name`, `type_`, `description`: sourced from the attribute name, \
    the annotation, and the attribute docstring.
    * `default`: the default value or a zero-argument factory.
    * `required`: must be present and non-null on `POST` and `PUT` \
    bodies and on strict construction. Defaults to `True` for a field \
    declared with no default and no `Optional` type.
    * `enum`: an `Enum` class or an iterable of allowed values; for an \
    array-typed field every item must be allowed.
    * `minimum`, `maximum`, `exclusive_minimum`, `exclusive_maximum`, \
    `multiple_of`: numeric constraints.
    * `min_length`, `max_length`, `pattern` (unanchored regex): string \
    constraints.
    * `min_items`, `max_items`, `unique_items`: array constraints.
    * `read_only`: never accepted on input (dropped with a WARNING), \
    included in `as_response`, omitted by `to_dict()`.
    * `write_only`: accepted on input, never in `as_response`.
    * `camel_case_keys`, `drop_null_items`: wire options for dict and \
    array values; `None` follows `FT3_LEGACY_WIRE`.

    Constraints are enforced by `parse(value, strict=True)`, on request \
    input, and on strict classes; otherwise a violation is kept and \
    logged once per class and field.

    ## Querying

    Comparing a class-level field builds a database-agnostic query \
    document: `==`, `!=`, `<`, `<=`, `>`, `>=`, `<<` (contains), and \
    `%` (similar, optionally `('text', 0.8)` with a threshold). Combine \
    with `&`, `|`, and `~`; sort with `query += 'field'` (ascending) or \
    `query -= 'field'` (descending); set `query.limit`. \
    `query.to_dict()` is the document.

    ```python
    query = (Pet.type_ == 'dog') & ~(Pet.name % ('fido', 0.75))
    query += 'name'

    ```
	"""

	_object_: 'Field[type[typ.Object]]'

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
	camel_case_keys: 'Field[bool]' = None
	"""
    Whether first-level keys of a dict value are camelCased on the \
    wire. `None` follows `FT3_LEGACY_WIRE` (2.0 default: keys are \
    never re-keyed).

    """
	drop_null_items: 'Field[bool]' = None
	"""
    Whether `None` items of an array value are dropped on the wire. \
    `None` follows `FT3_LEGACY_WIRE` (2.0 default: positions are \
    preserved).

    """

	@lib.t.overload
	def __get__(
		self, object_: None, dtype: type['objs.Object']
	) -> 'Field[typ.AnyType]': ...
	@lib.t.overload
	def __get__(
		self, object_: 'objs.Object', dtype: type['objs.Object']
	) -> typ.AnyType: ...
	def __get__(
		self,
		object_: lib.t.Optional['objs.Object'],
		dtype: type['objs.Object'],
	) -> 'Field[typ.AnyType]' | typ.AnyType:  # pragma: no cover
		return self

	def __set__(
		self, __object: lib.t.Any, __value: typ.AnyType
	) -> lib.t.Optional[lib.Never]:
		strict: bool = getattr(type(__object), Constants.__STRICT__, False)
		parsed = self._parse(__value)
		if isinstance(parsed, core.codecs.enm.ParseErrorRef):
			if strict or not self.required:
				raise exc.TypeValidationError(self.name, self.type_, parsed)
			if parsed is core.codecs.enm.ParseErrorRef.null_decode:
				self._warn_once(
					__object, 'required', True, None, 'stayed None'
				)
			else:
				self._warn_once(
					__object, 'type', parsed.value, __value, 'became None'
				)
			parsed = None
		else:
			self._enforce(parsed, __value, strict, __object)
		object.__setattr__(__object, self.name, parsed)
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
		camel_case_keys: bool = None,
		drop_null_items: bool = None,
		**kwargs: lib.t.Any,
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
		camel_case_keys: bool = None,
		drop_null_items: bool = None,
		**kwargs: lib.t.Any,
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
		camel_case_keys: bool = None,
		drop_null_items: bool = None,
		**kwargs: lib.t.Any,
	):
		if class_as_dict is not None:
			kwargs |= class_as_dict  # type: ignore[arg-type]
		else:
			kwargs |= dict(
				type_=lib.t.cast(
					type[typ.AnyType],
					type_ or kwargs.pop('type_', kwargs.pop('type', type_)),
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
				camel_case_keys=camel_case_keys,
				drop_null_items=drop_null_items,
			)

		ckwargs = {
			cname: value
			for name, value in kwargs.items()
			if (cname := core.strings.utl.cname_for(name, self.fields))
		}

		if isinstance(class_as_dict, lib.t.Mapping):
			class_as_cdict = {
				cname: value
				for name, value in class_as_dict.items()
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
					self.name or str(),
				)
			)
		)

	def __hash__(self) -> int:
		return self.__field_hash__()

	@lib.t.overload
	def __eq__(self, other: 'typ.AnyField[lib.t.Any]') -> bool: ...
	@lib.t.overload
	def __eq__(self: object, other: object) -> bool: ...
	@lib.t.overload
	def __eq__(
		self, other: lib.t.Any
	) -> 'bool | queries.EqQueryCondition | lib.Never': ...
	def __eq__(
		self, other: 'object | lib.t.Any | typ.AnyField[lib.t.Any]'
	) -> 'bool | queries.EqQueryCondition | lib.Never':
		if typ.utl.check.is_field(other):
			return self.__field_hash__() == other.__field_hash__()
		self._validate_comparison(other)
		from .. import queries

		q: queries.EqQueryCondition = queries.EqQueryCondition(
			field=self.name.rstrip('_'), eq=other
		)
		return q

	@lib.t.overload
	def __ne__(self, other: 'typ.AnyField[lib.t.Any]') -> bool: ...
	@lib.t.overload
	def __ne__(self: object, other: object) -> bool: ...
	@lib.t.overload
	def __ne__(
		self, other: lib.t.Any
	) -> 'bool | queries.NeQueryCondition | lib.Never': ...
	def __ne__(
		self, other: 'object | lib.t.Any | typ.AnyField[lib.t.Any]'
	) -> 'bool | queries.NeQueryCondition | lib.Never':
		if typ.utl.check.is_field(other):
			return self.__field_hash__() != other.__field_hash__()
		self._validate_comparison(other)
		from .. import queries

		q: queries.NeQueryCondition = queries.NeQueryCondition(
			field=self.name.rstrip('_'), ne=other
		)
		return q

	@lib.t.overload
	def __mod__(
		self, params: tuple[typ.AnyType, float]
	) -> 'queries.SimilarQueryCondition': ...
	@lib.t.overload
	def __mod__(
		self, params: typ.AnyType
	) -> 'queries.SimilarQueryCondition': ...
	@lib.t.overload
	def __mod__(
		self, params: tuple[lib.t.Any, ...]
	) -> 'queries.SimilarQueryCondition | lib.Never': ...
	@lib.t.overload
	def __mod__(
		self, params: lib.t.Any
	) -> 'queries.SimilarQueryCondition | lib.Never': ...
	def __mod__(
		self,
		params: tuple[typ.AnyType, float] | tuple[lib.t.Any, ...] | lib.t.Any,
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

		q: queries.SimilarQueryCondition = queries.SimilarQueryCondition(
			field=self.name.rstrip('_'), like=value, threshold=threshold
		)
		return q

	@lib.t.overload
	def __lshift__(
		self, value: typ.obj.ObjectLike
	) -> lib.Self | lib.Never: ...
	@lib.t.overload
	def __lshift__(
		self, value: lib.t.Any
	) -> lib.t.Union[
		'queries.ContainsQueryCondition', 'Field[lib.t.Any]', lib.Never
	]: ...
	def __lshift__(
		self, value: 'lib.t.Any | typ.obj.ObjectLike'
	) -> lib.t.Union[
		'queries.ContainsQueryCondition', 'Field[lib.t.Any]', lib.Never
	]:
		if typ.utl.check.is_field(value):
			return super().__lshift__(value)
		self._validate_iterable_comparison(value)
		from .. import queries

		q: queries.ContainsQueryCondition = queries.ContainsQueryCondition(
			field=self.name.rstrip('_'), contains=value
		)
		return q

	@lib.t.overload
	def __gt__(self, value: typ.AnyType) -> 'queries.GtQueryCondition': ...
	@lib.t.overload
	def __gt__(
		self, value: lib.t.Any
	) -> 'queries.GtQueryCondition | lib.Never': ...
	def __gt__(
		self, value: typ.AnyType | lib.t.Any
	) -> 'queries.GtQueryCondition | lib.Never':
		self._validate_comparison(value)
		from .. import queries

		q: queries.GtQueryCondition = queries.GtQueryCondition(
			field=self.name.rstrip('_'), gt=value
		)
		return q

	@lib.t.overload
	def __ge__(self, value: typ.AnyType) -> 'queries.GeQueryCondition': ...
	@lib.t.overload
	def __ge__(
		self, value: lib.t.Any
	) -> 'queries.GeQueryCondition | lib.Never': ...
	def __ge__(
		self, value: typ.AnyType | lib.t.Any
	) -> 'queries.GeQueryCondition | lib.Never':
		self._validate_comparison(value)
		from .. import queries

		q: queries.GeQueryCondition = queries.GeQueryCondition(
			field=self.name.rstrip('_'), ge=value
		)
		return q

	@lib.t.overload
	def __lt__(self, value: typ.AnyType) -> 'queries.LtQueryCondition': ...
	@lib.t.overload
	def __lt__(
		self, value: lib.t.Any
	) -> 'queries.LtQueryCondition | lib.Never': ...
	def __lt__(
		self, value: typ.AnyType | lib.t.Any
	) -> 'queries.LtQueryCondition | lib.Never':
		self._validate_comparison(value)
		from .. import queries

		q: queries.LtQueryCondition = queries.LtQueryCondition(
			field=self.name.rstrip('_'), lt=value
		)
		return q

	@lib.t.overload
	def __le__(self, value: typ.AnyType) -> 'queries.LeQueryCondition': ...
	@lib.t.overload
	def __le__(
		self, value: lib.t.Any
	) -> 'queries.LeQueryCondition | lib.Never': ...
	def __le__(
		self, value: typ.AnyType | lib.t.Any
	) -> 'queries.LeQueryCondition | lib.Never':
		self._validate_comparison(value)
		from .. import queries

		q: queries.LeQueryCondition = queries.LeQueryCondition(
			field=self.name.rstrip('_'), le=value
		)
		return q

	@lib.t.overload
	def _validate_comparison(
		self, value: lib.t.Optional[typ.AnyType]
	) -> None: ...
	@lib.t.overload
	def _validate_comparison(
		self, value: lib.t.Any
	) -> lib.t.Optional[lib.Never]: ...
	def _validate_comparison(
		self, value: lib.t.Any
	) -> lib.t.Optional[lib.Never]:
		if value is not None and not isinstance(
			value, typ.utl.check.get_checkable_types(self.type_)
		):
			raise exc.InvalidComparisonTypeError(self.name, self.type_, value)
		else:
			return None

	def _validate_iterable_comparison(
		self, value: lib.t.Any
	) -> lib.t.Optional[lib.Never]:
		if not any(
			issubclass(tp, lib.t.Iterable)
			for tp in typ.utl.check.get_checkable_types(self.type_)
		):
			raise exc.InvalidContainerComparisonTypeError(
				self.name, self.type_, value
			)
		else:
			return None

	def _parse(
		self, value: lib.t.Any
	) -> typ.AnyType | core.codecs.enm.ParseErrorRef:
		self.type_ = typ.utl.hint.finalize_type(self.type_)  # type: ignore[arg-type]
		parsed: typ.AnyType | core.codecs.enm.ParseErrorRef = (
			core.codecs.utl.parse(value, self.type_)
		)
		return parsed

	@lib.t.overload
	def parse(
		self,
		value: lib.t.Any,
		raise_validation_error: bool,
		*,
		strict: bool = False,
	) -> typ.AnyType | lib.Never: ...
	@lib.t.overload
	def parse(
		self,
		value: lib.t.Any,
		raise_validation_error: bool = True,
		*,
		strict: bool = False,
	) -> typ.AnyType | lib.Never: ...
	def parse(
		self,
		value: lib.t.Any,
		raise_validation_error: bool = True,
		*,
		strict: bool = False,
	) -> lib.t.Optional[typ.AnyType] | lib.Never:
		"""
        Return correctly typed value if possible, `None` otherwise, or \
        [optionally] raise an error if an invalid value is passed, the \
        method's default behavior.

        ---

        With `strict=True`, every declared constraint (`enum`, \
        `minimum`, `pattern`, ...) is enforced and only lossless \
        coercion is allowed, raising `ConstraintViolationError` \
        otherwise. Without it, constraint violations are logged once \
        per field and the value is returned as parsed.

        """

		parsed = self._parse(value)
		if isinstance(parsed, core.codecs.enm.ParseErrorRef):
			if raise_validation_error or strict:
				raise exc.TypeValidationError(self.name, self.type_, parsed)
			else:
				return None
		else:
			self._enforce(parsed, value, strict)
			return parsed

	@property
	def constraints(self) -> dict[str, lib.t.Any]:
		"""Declared constraints beyond type, keyed by field key."""

		return {
			key: limit
			for key in Constants.CONSTRAINT_KEYS
			if (limit := self.get(key)) is not None
		}

	def _enforce(
		self,
		parsed: lib.t.Any,
		original: lib.t.Any,
		strict: bool,
		object_: lib.t.Any = None,
	) -> lib.t.Optional[lib.Never]:
		"""Raise (strict) or warn once (lenient) per violated constraint."""

		for constraint, limit, value in self.violations(parsed, original):
			if strict:
				raise exc.ConstraintViolationError(
					self.name, constraint, limit, value
				)
			self._warn_once(object_, constraint, limit, value, 'was kept')
		return None

	def _warn_once(
		self,
		object_: lib.t.Any,
		constraint: str,
		limit: lib.t.Any,
		value: lib.t.Any,
		outcome: str,
	) -> None:
		from ... import loggers

		owner = getattr(self._object_, '__name__', type(object_).__name__)
		loggers.utl.warn_once(
			(owner, str(self.name), constraint),
			{
				'lenient.violation': {
					'object': owner,
					'field': self.name,
					'constraint': constraint,
					'limit': core.codecs.utl.encode(limit),
					'value': core.codecs.utl.encode(value),
					'outcome': outcome,
					'fix': 'declare the class with strict=True to raise',
				}
			},
		)
		return None

	def violations(
		self, parsed: lib.t.Any, original: lib.t.Any = Constants.UNDEFINED
	) -> list[tuple[str, lib.t.Any, lib.t.Any]]:
		"""
        Return `(constraint, limit, value)` for every declared \
        constraint the already type-parsed value violates, including \
        `lossless` when `original` was coerced with loss.

        """

		found: list[tuple[str, lib.t.Any, lib.t.Any]] = []
		if parsed is None:
			return found
		checkable = typ.utl.check.get_checkable_types(self.type_)
		if (
			original is not Constants.UNDEFINED
			and checkable
			and isinstance(original, Constants.NUMERIC_TYPES)
		):
			is_bool = isinstance(original, bool)
			numeric_target = bool not in checkable and any(
				isinstance(tp, type)
				and issubclass(tp, Constants.NUMERIC_TYPES)
				for tp in checkable
			)
			lossy = (is_bool and numeric_target) or (
				not is_bool and parsed != original
			)
			if lossy:
				found.append((Constants.LOSSLESS, self.type_, original))
		for constraint, limit in self.constraints.items():
			if self._violates(constraint, limit, parsed):
				found.append((constraint, limit, parsed))
		return found

	@staticmethod
	def _violates(constraint: str, limit: lib.t.Any, value: lib.t.Any) -> bool:
		is_number = isinstance(
			value, Constants.NUMERIC_TYPES
		) and not isinstance(value, bool)
		is_array = typ.utl.check.is_array(value)
		if constraint == 'enum':
			if isinstance(limit, lib.enum.EnumMeta):
				members = lib.t.cast(lib.t.Iterable[lib.enum.Enum], limit)
				allowed = tuple(member.value for member in members)
			else:
				allowed = tuple(limit)
			if is_array:
				return any(
					getattr(v, 'value', v) not in allowed for v in value
				)
			return getattr(value, 'value', value) not in allowed
		elif constraint == 'min_length':
			return isinstance(value, str) and len(value) < limit
		elif constraint == 'max_length':
			return isinstance(value, str) and len(value) > limit
		elif constraint == 'minimum':
			return is_number and value < limit
		elif constraint == 'maximum':
			return is_number and value > limit
		elif constraint == 'multiple_of':
			return is_number and value % limit != 0
		elif constraint == 'pattern':
			return (
				isinstance(value, str) and lib.re.search(limit, value) is None
			)
		elif constraint == 'min_items':
			return is_array and len(value) < limit
		elif constraint == 'max_items':
			return is_array and len(value) > limit
		else:
			return is_array and len({repr(v) for v in value}) < len(value)

	@property
	def factory(self) -> lib.t.Callable[[], typ.AnyType]:
		"""Return callable returning default value for field."""

		if (
			key := Constants.DELIM.join(
				(
					str(self.name).lower(),
					getattr(
						self.type_, '__name__', self.type_.__class__.__name__
					),
					str(self.default),
					'factory',
				)
			)
		) not in Constants.FACTORY_CACHE:
			if callable(self.default):
				Constants.FACTORY_CACHE[key] = lambda: self.default()  # type: ignore[operator]
			elif typ.utl.check.is_immutable_type(
				self.type_ or type(self.default)
			):
				Constants.FACTORY_CACHE[key] = lambda: self.default
			else:
				Constants.FACTORY_CACHE[key] = lambda: lib.copy.deepcopy(
					self.default
				)

		value: lib.t.Callable[[], typ.AnyType] = Constants.FACTORY_CACHE[key]
		return value

	def DELETE(  # type: ignore[override]
		self, fn: lib.t.Callable[['api.events.obj.Request'], None]
	) -> lib.t.Callable[['api.events.obj.Request'], None]:
		k: typ.string[typ.snake_case]
		obj_or_none = utl.get_obj_from_type(self.type_)  # type: ignore[arg-type]
		if obj_or_none is not None:
			k = '_'.join(
				(
					self._object_.__name__.lower(),
					obj_or_none.__name__.lower(),
					Constants.DELETE,
				)
			)
			obj_or_none._add_operation(k, fn)
		return fn

	def GET(  # type: ignore[override]
		self,
		fn: lib.t.Callable[
			['api.events.obj.Request'], 'list[typ.Object] | typ.Object | str'
		],
	) -> lib.t.Callable[
		['api.events.obj.Request'], 'list[typ.Object] | typ.Object | str'
	]:
		k: typ.string[typ.snake_case]
		tp = typ.utl.hint.finalize_type(fn.__annotations__['return'])
		obj_or_none = utl.get_obj_from_type(self.type_)  # type: ignore[arg-type]
		if obj_or_none is not None:
			if any(
				issubclass(tp_, list)
				for tp_ in typ.utl.check.get_checkable_types(tp)
			) or (typ.utl.check.is_object_type(tp) and not tp.hash_fields):
				k = '_'.join(  # pragma: no cover
					(self._object_.__name__.lower(), Constants.GET)
				)
			else:
				k = '_'.join(
					(
						self._object_.__name__.lower(),
						obj_or_none.__name__.lower(),
						Constants.GET,
					)
				)
			obj_or_none._add_operation(k, fn)
		return fn

	def OPTIONS(  # type: ignore[override]
		self, fn: lib.t.Callable[['api.events.obj.Request'], None]
	) -> lib.t.Callable[['api.events.obj.Request'], None]:  # pragma: no cover
		k: typ.string[typ.snake_case]
		obj_or_none = utl.get_obj_from_type(self.type_)  # type: ignore[arg-type]
		if obj_or_none is not None:
			k = '_'.join(
				(
					self._object_.__name__.lower(),
					obj_or_none.__name__.lower(),
					Constants.OPTIONS,
				)
			)
			obj_or_none._add_operation(k, fn)
		return fn

	def PATCH(  # type: ignore[override]
		self, fn: 'lib.t.Callable[[api.events.obj.Request], typ.Object]'
	) -> 'lib.t.Callable[[api.events.obj.Request], typ.Object]':
		k: typ.string[typ.snake_case]
		obj_or_none = utl.get_obj_from_type(self.type_)  # type: ignore[arg-type]
		if obj_or_none is not None:
			k = '_'.join(
				(
					self._object_.__name__.lower(),
					obj_or_none.__name__.lower(),
					Constants.PATCH,
				)
			)
			obj_or_none._add_operation(k, fn)
		return fn

	def POST(  # type: ignore[override]
		self, fn: 'lib.t.Callable[[api.events.obj.Request], typ.Object]'
	) -> 'lib.t.Callable[[api.events.obj.Request], typ.Object]':
		k: typ.string[typ.snake_case]
		obj_or_none = utl.get_obj_from_type(self.type_)  # type: ignore[arg-type]
		if obj_or_none is not None:
			k = '_'.join((self._object_.__name__.lower(), Constants.POST))
			obj_or_none._add_operation(k, fn)
		return fn

	def PUT(  # type: ignore[override]
		self, fn: 'lib.t.Callable[[api.events.obj.Request], typ.Object]'
	) -> 'lib.t.Callable[[api.events.obj.Request], typ.Object]':
		k: typ.string[typ.snake_case]
		obj_or_none = utl.get_obj_from_type(self.type_)  # type: ignore[arg-type]
		if obj_or_none is not None:
			k = '_'.join(
				(
					self._object_.__name__.lower(),
					obj_or_none.__name__.lower(),
					Constants.PUT,
				)
			)
			obj_or_none._add_operation(k, fn)
		return fn
