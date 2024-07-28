"""CLI objects."""

__all__ = (
    'parsers',
    'root_parser',
    )

from .. import __version__

from . import cfg
from . import lib


class Constants(cfg.Constants):
    """Constant values specific to CLI objs."""


root_parser = lib.argparse.ArgumentParser(
    description='root_parser',
    formatter_class=lib.argparse.ArgumentDefaultsHelpFormatter,
    prog='ft3',
    )
root_parser.add_argument(
    '--version',
    '-v',
    action='version',
    version=__version__,
    )

parsers = root_parser.add_subparsers(
    title='module',
    required=True,
    help='specify a module to access its commands'
    )
