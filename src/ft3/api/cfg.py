"""Api constants."""

__all__ = ('Constants',)

from .. import core


class Constants(core.cfg.Constants):
	"""Constant values specific to Api modules."""

	DEFAULT_VERSION = 'v1'
	VERSION = '3.1.0'
	API_PATH = '/'
	SWAGGER_PATH = '/swagger'
	DEFAULT_PORT = 80
	METHODS = (
		'delete',
		'get',
		'options',
		'patch',
		'post',
		'put',
	)
	SKIP_FIELDS = (
		'_object',
		'default',
		'name',
		'required',
		'camel_case_keys',
		'drop_null_items',
	)
	"""Field keys that never appear in an OpenAPI schema."""
