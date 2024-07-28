"""Docs utility functions."""

__all__ = (
    'document',
    )

from .. import cli

from . import cfg
from . import enm
from . import lib
from . import obj
from . import static


class Constants(cfg.Constants):
    """Documentation utils specific constants."""


def _do_api_doc(
    package_name: str,
    output_dir: str,
    is_namespace_package: bool,
    include_private_modules: bool,
    make_index: bool,
    ) -> None:

    if lib.os.path.exists(lib.os.path.join(output_dir, 'docs')):
        lib.shutil.rmtree(lib.os.path.join(output_dir, 'docs'))
    lib.os.makedirs(lib.os.path.join(output_dir, 'docs', 'source', '_static'))

    flags = [
        '-d', '4',  # noqa
        '-e',
        '-f',
        '-M',
        ]
    if make_index:
        flags.append('--tocfile')
        flags.append('index')
    else:
        flags.append('-T')
    if is_namespace_package:
        flags.append('--implicit-namespaces')
    if include_private_modules:
        flags.append('-P')

    import sphinx.ext.apidoc

    sphinx.ext.apidoc.main(
        (
            *flags,
            '-o',
            lib.os.path.join(output_dir, 'docs', 'source'),
            package_name,
            )
        )

    return None


def _export_conf(
    package_name: str,
    package_version: str,
    author: str,
    sphinx_theme: str,
    add_module_names: bool,
    autodoc_inherit_docstrings: bool,
    output_dir: str,
    ) -> None:

    template = lib.string.Template(static.config_template)
    rendered = template.safe_substitute(
        {
            'add_module_names': add_module_names,
            'author_name': author,
            'autodoc_inherit_docstrings': autodoc_inherit_docstrings,
            'package_name': package_name,
            'package_version': package_version,
            'sphinx_theme': sphinx_theme,
            }
        )

    out_file = lib.os.path.join(output_dir, 'docs', 'source', 'conf.py')
    with open(out_file, 'w') as f:
        f.write(rendered)

    return None


def _do_build(
    output_dir: str,
    ) -> None:

    import sphinx.cmd.build

    sphinx.cmd.build.main(
        (
            '-a',
            '-E',
            lib.os.path.join(output_dir, 'docs', 'source'),
            lib.os.path.join(output_dir, 'docs', 'html')
            )
        )

    return None


def document(
    package: str,
    version: str,
    author: str,
    output_dir: str,
    favicon_path: str,
    logo_path: str,
    sphinx_theme: str,
    is_namespace_package: bool,
    add_module_names: bool,
    autodoc_inherit_docstrings: bool,
    no_cleanup: bool,
    include_private_modules: bool,
    make_index: bool,
    readme_path: lib.t.Optional[str],
    no_include_meta_tags: bool,
    no_include_robots: bool,
    site_map_urls: list[str],
    site_map_change_freq: str,
    ) -> None:
    """
    CLI entrypoint for documenting a python package in wiki style.

    ---

    Requirements
    ------------

    Leverages and requires the sphinx library (and an extension to
    handle markdown), which is technically a third-party dependency, \
    even if sphinx is used to [document python itself](https://devguide.python.org/documentation/start-documenting/#building-doc).

    They can be installed using the following command.

    `$ pip install ft3[docs]`

    ---

    Usage
    -----

    Specify the name of the package (or [relative] path to the package) \
    as the first positional argument.

    For example, if we are in the root level directory of a standard \
    python repo called `package`, then the following command will...

    `$ ft3 docs .`

    ...create a `/docs` sub-directory in the directory from which the \
    script is executed, with all documentation for `package` fully \
    generated within.

    For additional command options and argument flags, please use:

    `$ ft3 docs --help`

    """

    try:
        import commonmark  # type: ignore
        import sphinx  # type: ignore
    except (ImportError, ModuleNotFoundError):
        cli.obj.root_parser.exit(
            1,
            '\n'.join(
                (
                    'Missing a required third-party dependency.',
                    'Install with `$ pip install ft3[docs]`.',
                    'Exiting...'
                    )
                )
            )

    match = obj.Pattern.PrefixPattern.match(package)
    is_local_package = bool(match)

    package_name = obj.Pattern.PrefixPattern.sub('', package)

    if is_local_package:

        for _, dirnames, filenames in lib.os.walk('.'):
            is_pyproject_cfg = 'pyproject.toml' in filenames
            is_src_package = 'src' in dirnames
            break

        if is_pyproject_cfg and not package_name:
            parser = lib.configparser.ConfigParser()
            parser.read('pyproject.toml')
            package_name = parser['project']['name'][1:-1]
        elif not package_name:
            with open('setup.py', 'r') as f:
                in_setup_fn = False
                for line in f.readlines():
                    if 'setup(' in line:
                        in_setup_fn = True
                    if in_setup_fn and 'name' in line:
                        _, _, partition = line.partition('name=')
                        re_match_name = obj.Pattern.MinOneWordPattern.match(
                            partition
                            )
                        if re_match_name is not None:
                            package_name = re_match_name.group()
                            break

    else:
        is_src_package = False

    package_name = obj.Pattern.PathPattern.sub('.', package_name)
    re_match_root = obj.Pattern.MinOneWordPattern.match(package_name)
    if re_match_root is not None:
        package_root = re_match_root.group()
    else:
        package_root = package_name

    _do_api_doc(
        (
            lib.os.path.join('src', package_root)
            if is_src_package
            else package_root
            ),
        output_dir,
        is_namespace_package,
        include_private_modules,
        make_index or bool(readme_path),
        )

    source_dir = lib.os.path.join(output_dir, 'docs', 'source')
    static_dir = lib.os.path.join(source_dir, '_static')
    lib.shutil.copyfile(
        favicon_path,
        lib.os.path.join(static_dir, 'favicon.ico'),
        )
    lib.shutil.copyfile(
        logo_path,
        lib.os.path.join(static_dir, 'logo.png'),
        )

    # Below is done to fix static asset rendering on github pages.
    # See: https://github.com/sphinx-doc/sphinx/issues/2202
    with open(
        lib.os.path.join(output_dir, 'docs', '.nojekyll'),
        'w'
        ) as jkl_file:
        jkl_file.write('')

    # Remove generated files irrelevant to the
    # targeted namespace.
    if is_namespace_package:
        for pre_file_name in lib.os.listdir(source_dir):
            if (
                pre_file_name.endswith('.rst')
                and not pre_file_name.endswith('index.rst')
                and not pre_file_name.startswith(package_name)
                ):
                lib.os.remove(
                    lib.os.path.join(
                        output_dir,
                        'docs',
                        'source',
                        pre_file_name
                        )
                    )

    _export_conf(
        package_name,
        version,
        author,
        sphinx_theme,
        add_module_names,
        autodoc_inherit_docstrings,
        output_dir,
        )

    # Append meta tags to files.
    if not no_include_meta_tags:
        for file_name in lib.os.listdir(source_dir):
            if not file_name.endswith('.rst'):
                continue
            module_name = file_name.removesuffix('.rst')
            if (
                (
                    module_name == package_root
                    and not (make_index or readme_path)
                    )
                or file_name.startswith('index')
                ):
                txt = ''.join(
                    (
                        '      ',
                        f"Documentation homepage for the '{package_name}' ",
                        'project.'
                        )
                    )
            else:
                txt = ' '.join(
                    (
                        f"      Documentation page for the '{module_name}'",
                        f"component of the '{package_name}' project."
                        )
                    )
            lines = [
                '',
                '.. meta::',
                '   :description lang=en:',
                txt,
                '',
                ]
            with open(
                lib.os.path.join(source_dir, file_name),
                'a'
                ) as file_buf:
                file_buf.write('\n'.join(lines))

    _do_build(output_dir)

    # Optionally include sitemap.
    if site_map_urls:
        html_dir = lib.os.path.join(output_dir, 'docs', 'html')
        pages: list[str] = [
            html_file_name
            for html_file_name
            in lib.os.listdir(html_dir)
            if (
                html_file_name.endswith('.html')
                and (
                    html_file_name.startswith(package_root)
                    or html_file_name.startswith('index')
                    )
                )
            ]
        page_depths = [
            len(page_name.split('.'))
            for page_name
            in pages
            ]
        min_depth = min(page_depths)
        max_depth = max(page_depths)
        lastmod = lib.datetime.datetime.now(
            lib.datetime.timezone.utc
            ).isoformat()

        url_set: list[str] = [
            (
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
                ' xmlns:xhtml="http://www.w3.org/1999/xhtml">'
                ),
            ]
        for site_map_url in site_map_urls:
            parsed = lib.urllib.parse.urlparse(site_map_url)
            for page in pages:
                page_depth = len(page.split('.'))
                page_loc = '/'.join((site_map_url.rstrip('/'), page))
                priority = (max_depth - page_depth + min_depth) / max_depth
                xml_url = '\n'.join(
                    (
                        '<url>',
                        f'    <loc>{page_loc}</loc>',
                        f'    <changefreq>{site_map_change_freq}</changefreq>',
                        f'    <lastmod>{lastmod}</lastmod>',
                        f'    <priority>{priority!s}</priority>',
                        '</url>',
                        )
                    )
                url_set.append(xml_url)

        xml_path = lib.os.path.join(output_dir, 'docs', 'html', 'sitemap.xml')
        with open(xml_path, 'w') as xml_file:
            xml_file.write(
                '\n'.join(
                    (
                        '<?xml version="1.0" encoding="UTF-8"?>',
                        *url_set,
                        '</urlset>'
                        )
                    )
                )

    # Include robotos.txt unless otherwise specified.
    if not no_include_robots:
        robots_path = lib.os.path.join(
            output_dir,
            'docs',
            'html',
            'robots.txt'
            )
        with open(robots_path, 'w') as robots_file:
            robots_txt = '\n'.join(
                (
                    'User-agent: *',
                    'Allow: /',
                    *enm.NoCrawlPath._value2member_map_,
                    )
                )
            if site_map_urls:
                parsed = lib.urllib.parse.urlparse(site_map_urls[0])
                url_root = '://'.join((parsed.scheme, parsed.hostname or ''))
                path = parsed.path.strip('/')
                robots_txt += f'\n\nSitemap: {url_root}/{path}/sitemap.xml'
            robots_file.write(robots_txt)

    # Inject readme.md if exists.
    if readme_path:
        with open(readme_path, 'r', errors='ignore') as md_file:
            md = md_file.read()

        html = commonmark.commonmark(md, format='html')

        index_path = lib.os.path.join(
            output_dir,
            'docs',
            'html',
            'index.html'
            )
        with open(index_path, 'r') as html_file:
            index_html = html_file.read()

        new_lines = []
        for line in index_html.split('\n'):
            if line.strip() == f'<section id="{package_name}">':
                new_lines.extend(html.split('\n'))
                line = f'<section id="{package_name}" hidden=true>'
            new_lines.append(line)

        with open(index_path, 'w') as html_file:
            html_file.write('\n'.join(new_lines))

    if not no_cleanup:
        lib.shutil.rmtree(source_dir)
