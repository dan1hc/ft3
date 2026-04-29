"""Objects utility functions."""

__all__ = (
	'ast_find_classdef',
	'get_attribute_docs',
	'get_enumerations_from_fields',
	'get_fields_for_hash',
	'get_obj_from_type',
	'is_public_field',
	'is_valid_keyword',
	'should_extract_attribute_docs',
)

from . import cfg
from . import lib
from . import typ

if lib.t.TYPE_CHECKING:  # pragma: no cover
	from . import metas


class Constants(cfg.Constants):
	"""Constant values specific to this file."""


def ast_find_classdef(tree: lib.ast.AST) -> lib.ast.ClassDef:
	"""Get `ClassDef` from an AST."""

	defs = [e for e in lib.ast.walk(tree) if isinstance(e, lib.ast.ClassDef)]
	return defs[0]


def should_extract_attribute_docs() -> bool:
	"""Return if source-backed attribute docs should be extracted."""

	if (raw := lib.os.getenv(Constants.EXTRACT_ATTRIBUTE_DOCS_ENV)) is None:
		return Constants.EXTRACT_ATTRIBUTE_DOCS
	else:
		return (
			raw.strip().lower()
			not in Constants.EXTRACT_ATTRIBUTE_DOCS_FALSE_VALUES
		)


def _source_file_cache_key(source_file: str) -> tuple[str, int, int]:
	"""Return stable cache inputs for a source file."""

	absolute_source_file = lib.os.path.abspath(source_file)
	try:
		source_stat = lib.os.stat(absolute_source_file)
	except OSError:
		return absolute_source_file, 0, 0
	else:
		return (
			absolute_source_file,
			source_stat.st_mtime_ns,
			source_stat.st_size,
		)


def _string_expr_value(stmt: lib.ast.stmt) -> lib.t.Optional[str]:
	"""Return the string value for an expression statement."""

	if isinstance(stmt, lib.ast.Expr):
		value = getattr(stmt.value, 'value', None)
		if isinstance(value, str):
			return value

	return None


def _class_body_without_docstring(
	class_def: lib.ast.ClassDef,
) -> list[lib.ast.stmt]:
	"""Return class body excluding the class docstring when present."""

	if class_def.body and _string_expr_value(class_def.body[0]) is not None:
		return class_def.body[1:]
	else:
		return class_def.body


def _attribute_docs_from_class_def(
	class_def: lib.ast.ClassDef,
) -> dict[str, str]:
	"""Return attribute docs from one class definition."""

	attribute_docs: dict[str, str] = {}
	body = _class_body_without_docstring(class_def)
	for index, stmt in enumerate(body[:-1]):
		if (
			isinstance(stmt, lib.ast.AnnAssign)
			and (doc_raw := _string_expr_value(body[index + 1])) is not None
		):
			name = lib.ast.unparse(stmt.target)
			attribute_docs[name] = lib.textwrap.dedent(doc_raw)

	return attribute_docs


def _collect_attribute_docs_from_body(
	body: list[lib.ast.stmt],
	qualname_prefix: tuple[str, ...],
	result: dict[str, dict[str, str]],
	short_names: dict[str, lib.t.Optional[dict[str, str]]],
) -> None:
	"""Collect attribute docs for all class definitions in a body."""

	for stmt in body:
		if isinstance(stmt, lib.ast.ClassDef):
			qualname = '.'.join((*qualname_prefix, stmt.name))
			docs = _attribute_docs_from_class_def(stmt)
			result[qualname] = docs
			if stmt.name not in short_names:
				short_names[stmt.name] = docs
			else:
				short_names[stmt.name] = None
			_collect_attribute_docs_from_body(
				stmt.body, (*qualname_prefix, stmt.name), result, short_names
			)
		elif isinstance(stmt, (lib.ast.AsyncFunctionDef, lib.ast.FunctionDef)):
			_collect_attribute_docs_from_body(
				stmt.body,
				(*qualname_prefix, stmt.name, '<locals>'),
				result,
				short_names,
			)

	return None


@lib.functools.cache
def _get_attribute_docs_for_source(
	source_file: str,
	source_mtime_ns: int,
	source_size: int,
) -> dict[str, dict[str, str]]:
	"""Return attribute docs for every class in a source file."""

	try:
		with open(source_file, encoding='utf-8') as source:
			tree = lib.ast.parse(source.read(), filename=source_file)
	except (OSError, SyntaxError, UnicodeDecodeError):
		return {}

	result: dict[str, dict[str, str]] = {}
	short_names: dict[str, lib.t.Optional[dict[str, str]]] = {}
	_collect_attribute_docs_from_body(tree.body, (), result, short_names)
	for name, docs in short_names.items():
		if docs is not None:
			result.setdefault(name, docs)

	return result


def get_attribute_docs(
	cls: 'metas.Meta',
) -> dict[typ.string[typ.snake_case], str]:
	"""Get class attribute docstrings."""

	if not should_extract_attribute_docs():
		return {}

	try:
		source_file = lib.inspect.getsourcefile(cls) or lib.inspect.getfile(
			cls
		)
	except (OSError, TypeError):
		return {}

	if not source_file:
		return {}

	docs_by_class = _get_attribute_docs_for_source(
		*_source_file_cache_key(source_file)
	)
	docs = docs_by_class.get(
		cls.__qualname__, docs_by_class.get(cls.__name__, {})
	)
	return lib.t.cast(dict[typ.string[typ.snake_case], str], dict(docs))


@lib.functools.cache
def is_public_field(f: str) -> bool:
	"""Return if field name is public."""

	return not ((f in Constants.FORBIDDEN_KEYWORDS) or f.startswith('_'))


@lib.functools.cache
def is_valid_keyword(f: str) -> bool:
	"""Return if field name is allowed."""

	return f not in (
		set(Constants.FORBIDDEN_KEYWORDS) | set(Constants.BASE_ATTRS)
	)


def get_enumerations_from_fields(
	fields: typ.DataClassFields,
) -> dict[typ.string[typ.snake_case], tuple[typ.Primitive, ...]]:
	"""
	Return dict containing all enums for object.

	---

	Automatically appends `None` to any enums for an `Optional` type.

	"""

	d: dict[typ.string[typ.snake_case], tuple[typ.Primitive, ...]] = {}
	for k, field in fields.items():
		if isinstance((enum_ := field.get('enum')), lib.enum.EnumMeta):
			d[k] = tuple([e.value for e in enum_._member_map_.values()])
		elif typ.utl.check.is_array(enum_):
			d[k] = tuple(enum_)
		if (
			k in d
			and isinstance(
				None, typ.utl.check.get_checkable_types(field.type_)
			)
			and None not in d[k]
		):
			d[k] = (*d[k], None)

	return d


def get_fields_for_hash(
	__fields: typ.DataClassFields,
) -> tuple[typ.string[typ.snake_case], ...]:
	"""
    Filter to set of minimum fields required to compute a unique hash \
    for their owner object.

    ---

    Fields used must be of primitive types, for these purposes: \
    `bool | float | int | None | str`.

    Fields ending in the following will be used [in the following \
    order of precedence]:

    1. `'*id' | '*key'`
    2. `'*name'`

    For example, for an object with fields `'id_'` and \
    `'_common_name_'`, this function would return `('id_', )`, as \
    `'id_'` takes precedence over `'_common_name_'`.

    If no fields are named in ways that suggest they can be used to \
    determine the uniqueness of the object, no fields will be returned.

    """

	id_fields: list[typ.string[typ.snake_case]] = []
	name_fields: list[typ.string[typ.snake_case]] = []

	for f, field in __fields.items():
		if isinstance(field.type_, (lib.t.ForwardRef, str)) or not all(
			typ.utl.check.is_primitive(sub_tp)
			for sub_tp in typ.utl.check.get_checkable_types(field)
		):  # pragma: no cover
			continue
		elif (s := f.strip('_').lower()).endswith('id'):
			id_fields.append(f)
		elif s.endswith('key'):
			id_fields.append(f)
		elif s.startswith('name') or s.endswith('name'):
			name_fields.append(f)

	if id_fields:
		fields_for_hash = tuple(id_fields)
	elif name_fields:
		fields_for_hash = tuple(name_fields)
	else:
		fields_for_hash = tuple()

	return fields_for_hash


@lib.functools.cache
def get_obj_from_type(type_: lib.t.Any) -> lib.t.Optional[type['typ.Object']]:
	"""
    Return valid `type[Object]` from a generic `type` or `None` \
    otherwise.

    """

	tps: tuple[type['typ.Object'], ...]
	if (
		typ.utl.check.is_union(type_)
		and len(u_tps := typ.utl.check.get_type_args(type_)) == 2
		and any(typ.utl.check.is_none_type(tp) for tp in u_tps)
		and any(
			(
				typ.utl.check.is_object_type(tp)
				or typ.utl.check.is_array_of_obj_type(tp)
			)
			for tp in u_tps
		)
	):
		for tp in u_tps:  # pragma: no cover
			if typ.utl.check.is_object_type(tp):
				return tp
			elif typ.utl.check.is_array_of_obj_type(tp):
				tps = typ.utl.check.get_type_args(tp)
				return tps[0]
		return None  # pragma: no cover
	elif typ.utl.check.is_object_type(type_):
		return type_
	elif typ.utl.check.is_array_of_obj_type(type_):
		tps = typ.utl.check.get_type_args(type_)
		return tps[0]
	else:
		return None
