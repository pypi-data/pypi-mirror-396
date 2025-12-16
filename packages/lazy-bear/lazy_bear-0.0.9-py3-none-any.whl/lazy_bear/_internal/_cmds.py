from __future__ import annotations

from argparse import ArgumentParser, Namespace

from lazy_bear._internal._versioning import BumpType, ExitCode, cli_bump
from lazy_bear._internal.debug import METADATA, _print_debug_info


def _debug_info() -> ExitCode:  # pragma: no cover
    """CLI command to print debug information."""
    _print_debug_info()
    return ExitCode.SUCCESS


def _bump(bump_type: BumpType) -> ExitCode:  # pragma: no cover
    """CLI command to bump the version of the package."""
    return cli_bump(bump_type, METADATA.version_tuple)


def _version(name: bool = False) -> ExitCode:  # pragma: no cover
    """CLI command to get the current version of the package."""
    print(f"{METADATA.name} {METADATA.version}" if name else METADATA.version)
    return ExitCode.SUCCESS


def to_args(args: list[str]) -> Namespace:  # pragma: no cover
    """Convert a list of arguments into a Namespace object."""
    parser = ArgumentParser(prog=METADATA.name, description="Lazy Bear CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("debug-info", help="Print debug information")
    version_parser: ArgumentParser = subparsers.add_parser("version", help="Get the current version")
    version_parser.add_argument(
        "--name",
        action="store_true",
        help="Include the package name in the output",
    )
    bump_parser: ArgumentParser = subparsers.add_parser("bump", help="Bump the version of the package")
    bump_parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch"],
        help="Type of version bump",
    )
    return parser.parse_args(args)
