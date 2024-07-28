"""Docs objects."""

__all__ = (
    'docs_parser',
    'Pattern',
    )

from .. import cli

from . import cfg
from . import enm
from . import lib
from . import utl

__all__ = (
    'docs_parser',
    'Pattern',
    )


class Constants(cfg.Constants):
    """Constant values specific to Docs objs."""


class Pattern:
    """Compiled regex patterns."""

    ModulePattern = lib.re.compile(r'^(\.\. automodule:: )')
    """Matches automodule:: directive text to be stripped from rst files."""

    MinOneWordPattern = lib.re.compile(r'\w+')
    """Matches at least one valid word."""

    PathPattern   = lib.re.compile(r'(\/|\\)')
    """Matches Windows and Unix paths."""

    PrefixPattern = lib.re.compile(r'^(\.)?(\/|\\)?((src)(\/|\\))?')
    """Matches packages that use the /src prefix."""


docs_parser = cli.obj.parsers.add_parser(  # type: ignore[has-type]
    'docs',
    formatter_class=lib.argparse.ArgumentDefaultsHelpFormatter,
    )

docs_parser.add_argument(
    'package',
    help='the name or path to the package to be documented',
    )
docs_parser.add_argument(
    '--version',
    '-v',
    default=Constants.BASE_VERSION,
    help='the version of the package',
    dest='version',
    )
docs_parser.add_argument(
    '--author',
    '-a',
    help='specify package author',
    dest='author',
    default=Constants.DEFAULT_USER,
    )
docs_parser.add_argument(
    '--output',
    '-o',
    help='specify directory in which to create docs/',
    dest='output_dir',
    default='.',
    )
docs_parser.add_argument(
    '--favicon',
    help='specify location of a favicon (.ico) file',
    dest='favicon_path',
    default=lib.os.path.join(Constants.DOCS_STATIC_DIR, 'favicon.ico'),
    )
docs_parser.add_argument(
    '--logo',
    help='specify location of a logo file',
    dest='logo_path',
    default=lib.os.path.join(Constants.DOCS_STATIC_DIR, 'logo.png'),
    )
docs_parser.add_argument(
    '--theme',
    choices=enm.SupportedTheme._member_names_,
    help='specify sphinx theme',
    dest='sphinx_theme',
    default=enm.SupportedTheme.alabaster.value,
    )
docs_parser.add_argument(
    '--namespace-package',
    action='store_true',
    dest='is_namespace_package',
    help='include to specify that package is a namespace package',
    )
docs_parser.add_argument(
    '--add-module-names',
    action='store_true',
    dest='add_module_names',
    help='include to prepend module names to object names',
    )
docs_parser.add_argument(
    '--no-inherit-docstrings',
    action='store_false',
    dest='autodoc_inherit_docstrings',
    help='include to disable docstring inheritance',
    )
docs_parser.add_argument(
    '--no-cleanup',
    action='store_true',
    dest='no_cleanup',
    help='include to disable /docs/source/ dir removal',
    )
docs_parser.add_argument(
    '--include-private-modules',
    action='store_true',
    dest='include_private_modules',
    help='include to also document _private modules',
    )
docs_parser.add_argument(
    '--make-index',
    action='store_true',
    dest='make_index',
    help='include to make root file called index instead of {package}',
    )
docs_parser.add_argument(
    '--index-from-readme',
    nargs='?',
    dest='readme_path',
    help=(
        'specify path to README.md file to use'
        ' for index instead of {package}'
        ),
    const=lib.os.path.join('.', 'README.md'),
    default=None,
    )
docs_parser.add_argument(
    '--no-include-meta-tags',
    action='store_true',
    dest='no_include_meta_tags',
    help='include to disable auto-generation of meta tags for documentation',
    )
docs_parser.add_argument(
    '--no-robots-txt',
    action='store_true',
    dest='no_include_robots',
    help='include to disable auto-generation of robots.txt file',
    )
docs_parser.add_argument(
    '--site-map-url',
    help='\n'.join(
        (
            (
                'specify full url path to the documentation version to be'
                'included in an auto-generated xml sitemap'
                ),
            '',
            'ex. https://example.readthedocs.io/en/stable',
            '',
            'can be repeated to include multiple versions'
            )
        ),
    action='append',
    dest='site_map_urls',
    )
docs_parser.add_argument(
    '--site-map-change-freq',
    choices=enm.SiteMapChangeFreq._member_names_,
    help='specify how often site-map expected to change',
    dest='site_map_change_freq',
    default=enm.SiteMapChangeFreq.weekly.value,
    )
docs_parser.set_defaults(func=utl.document)
