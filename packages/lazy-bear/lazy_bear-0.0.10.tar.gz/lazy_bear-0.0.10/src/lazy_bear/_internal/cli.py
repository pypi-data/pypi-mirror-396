from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from lazy_bear._internal._cmds import ExitCode, _bump, _debug_info, _version, to_args

if TYPE_CHECKING:
    from argparse import Namespace


def main(args: list[str] | None = None) -> ExitCode:  # pragma: no cover
    """Entry point for the CLI application.

    This function is executed when you type `lazy_bear` or `python -m lazy_bear`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    if args is None:
        args = sys.argv[1:]
    arguments: Namespace = to_args(args)
    command: str = arguments.command
    match command:
        case "debug-info":
            return _debug_info()
        case "version":
            return _version(name=arguments.name)
        case "bump":
            return _bump(bump_type=arguments.bump_type)
        case _:  # pragma: no cover
            print(f"Unknown command: {command}")
            return ExitCode.FAILURE


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))  # pragma: no cover
