"""Static files for api."""

__all__ = (
    'favicon',
    'swagger_template'
    )

from .. import lib

ROOT = lib.os.path.dirname(__file__)

with open(lib.os.path.join(ROOT, 'favicon.ico'), 'rb') as f:
    favicon = f.read()

with open(lib.os.path.join(ROOT, 'swagger.html'), 'r') as f:
    swagger_template = f.read()
