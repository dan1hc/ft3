"""CLI utility functions."""

__all__ = (
    'main',
    )

from . import obj


def main() -> None:  # pragma: no cover
    """
    Main CLI entrypoint.

    Commands follow the structure:

    `$ ft3 {ft3_module_name} ...`

    """

    args = obj.root_parser.parse_args()
    kwargs = args._get_kwargs()
    as_args = [v for k, v in kwargs if k != 'func']
    args.func(*as_args)  # type: ignore[attr-defined]

    return None
