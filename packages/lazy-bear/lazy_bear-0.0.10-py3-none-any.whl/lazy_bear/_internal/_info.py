from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError, distribution, version
from typing import Literal

from lazy_bear._internal._version import __commit_id__, __version__, __version_tuple__


@dataclass(slots=True)
class _Package:
    """Dataclass to store package information."""

    name: str
    """Package name."""
    version: str = "0.0.0"
    """Package version."""
    description: str = "No description available."
    """Package description."""

    def __str__(self) -> str:  # pragma: no cover
        """String representation of the package information."""
        return f"{self.name} v{self.version}: {self.description}"


def _get_version(dist: str) -> str:  # pragma: no cover
    """Get version of the given distribution or the current package.

    Parameters:
        dist: A distribution name.

    Returns:
        A version number.
    """
    try:
        return version(dist)
    except PackageNotFoundError:
        return "0.0.0"


def _get_description(dist: str) -> str:  # pragma: no cover
    """Get description of the given distribution or the current package.

    Parameters:
        dist: A distribution name.

    Returns:
        A description string.
    """
    try:
        return distribution(dist).metadata.get("summary", "No description available.")
    except PackageNotFoundError:
        return "No description available."


def _get_package_info(dist: str) -> _Package:  # pragma: no cover
    """Get package information for the given distribution.

    Parameters:
        dist: A distribution name.

    Returns:
        Package information with version, name, and description.
    """
    return _Package(name=dist, version=_get_version(dist), description=_get_description(dist))


# fmt: off
@dataclass(slots=True, frozen=True)
class _ProjectName:# pragma: no cover
    """A class to represent the project name and its metadata as literals for type safety.

    This is done this way to make it easier to see the values in the IDE and to ensure that the values are consistent throughout the codebase.
    """

    package_distribution: Literal["lazy-bear"] = "lazy-bear"
    project: Literal["lazy_bear"] = "lazy_bear"
    project_upper: Literal["LAZY_BEAR"] = "LAZY_BEAR"
    env_variable: Literal["LAZY_BEAR_ENV"] = ("LAZY_BEAR_ENV")
# fmt: on


@dataclass(slots=True, frozen=True)
class _ModulePaths:  # pragma: no cover
    """A class to hold the module import paths, mostly for the CLI."""

    _internal: str = "lazy_bear._internal"
    _commands: str = f"{_internal}._cmds"


def get_version() -> str:  # pragma: no cover
    """Get the current project version."""
    return __version__ if __version__ != "0.0.0" else _get_version("lazy-bear")


@dataclass(slots=True)
class _ProjectMetadata:  # pragma: no cover
    """Dataclass to store the current project metadata."""

    version: str = field(default_factory=get_version)
    version_tuple: tuple[int, int, int] = field(default=__version_tuple__)
    commit_id: str = field(default=__commit_id__)
    _name: _ProjectName = field(default_factory=_ProjectName)
    _paths: _ModulePaths = field(default_factory=_ModulePaths)

    @property
    def cmds(self) -> str:
        """Get the commands module path."""
        return self._paths._commands

    @property
    def full_version(self) -> str:
        """Get the full version string."""
        return f"{self.name} v{self.version}"

    @property
    def description(self) -> str:
        """Get the project description from the distribution metadata."""
        return _get_description(self.name)

    @property
    def name(self) -> Literal["lazy-bear"]:
        """Get the package distribution name."""
        return self._name.package_distribution

    @property
    def name_upper(self) -> Literal["LAZY_BEAR"]:
        """Get the project name in uppercase with underscores."""
        return self._name.project_upper

    @property
    def project_name(self) -> Literal["lazy_bear"]:
        """Get the project name."""
        return self._name.project

    @property
    def env_variable(self) -> Literal["LAZY_BEAR_ENV"]:
        """Get the environment variable name for the project.

        Used to check if the project is running in a specific environment.
        """
        return self._name.env_variable

    def __str__(self) -> str:
        """String representation of the project metadata."""
        return f"{self.full_version}: {self.description}"


METADATA = _ProjectMetadata()


__all__ = ["METADATA"]
