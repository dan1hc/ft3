"""Objects constants."""

__all__ = (
    'Constants',
    )

from .. import core


class Constants(core.cfg.Constants):
    """Constant values specific to objects modules."""

    BASE_ATTRS = (
        '__heritage__',
        '__dataclass_fields__',
        '__operations__',
        'enumerations',
        'fields',
        'hash_fields',
        )
    FIELD_KEYS = (
        'name',
        'type',
        'default',
        'required',
        'enum',
        'min_length',
        'max_length',
        'minimum',
        'exclusive_minimum',
        'maximum',
        'exclusive_maximum',
        'multiple_of',
        'pattern',
        'min_items',
        'max_items',
        'unique_items',
        'read_only',
        'write_only',
        )
    FIELDS_MODULE = __name__.replace('cfg', 'fields.obj')
    OBJECTS_MODULE = __name__.replace('cfg', 'objs.obj')
    FORBIDDEN_KEYWORDS = (
        '__init__',
        '__init_subclass__',
        '__new__',
        '__getattribute__',
        '__bool__',
        '__contains__',
        '__getitem__',
        '__setitem__',
        '__delitem__',
        '__reversed__',
        '__eq__',
        '__ne__',
        '__iter__',
        '__ior__',
        '__len__',
        '__repr__',
        '__sub__',
        '__lshift__',
        '__rshift__',
        '__getstate__',
        '__setstate__',
        '__instancecheck__',
        '__subclasscheck__',
        'class_as_dict',
        'copy',
        'enumerations',
        'fields',
        'get',
        'hash_fields',
        'items',
        'keys',
        'pop',
        'setdefault',
        'update',
        'values',
        'DELETE',
        'GET',
        'OPTIONS',
        'PATCH',
        'POST',
        'PUT'
        )
