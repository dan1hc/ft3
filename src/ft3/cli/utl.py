"""CLI utility functions."""

__all__ = ('main',)

from . import obj


def main() -> None:
	"""
	Main CLI entrypoint.

	Commands follow the structure:

	`$ ft3 {command} ...`

	Every parsed argument is passed to the command by name, so a \
	command's parameters are its parser's `dest` names.

	"""

	args = obj.root_parser.parse_args()
	kwargs = {k: v for k, v in vars(args).items() if k != 'func'}
	args.func(**kwargs)

	return None
