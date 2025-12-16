"""A set of helper functions for dynamic module loading."""

from __future__ import annotations

import sys
from threading import RLock
from types import FrameType, ModuleType
from typing import Any, ClassVar, final, overload

from lazy_bear.lazy_attribute import LazyAttr

_lock: RLock = RLock()


def get_calling_file(d: int = 2) -> str:
    """Get the filename of the calling frame.

    Args:
        d (int): The depth of the frame to inspect. Default is 2.
    """
    return sys._getframe(d).f_code.co_filename  # type: ignore[attr-defined]


def get_calling_globals(d: int = 2) -> dict[str, Any]:
    """Get the globals of the calling frame.

    Args:
        d (int): The depth of the frame to inspect. Default is 2.
    """
    return sys._getframe(d).f_globals  # type: ignore[attr-defined]


@final
class LazyLoader(ModuleType):
    """Class for module lazy loading."""

    __slots__: tuple = ("_module", "_name", "_parent_globals")

    _module: ModuleType | None
    _name: str
    _parent_globals: dict[str, Any]
    _globals_modules: ClassVar[dict[str, dict[str, Any]]] = {}

    def __init__(self, name: str) -> None:
        """Initialize the LazyLoader.

        Args:
            name (str): The full name of the module to load, must be the full path.
        """
        self._name: str = name
        self._module = None
        with _lock:
            frame: FrameType = sys._getframe(1)
            f: str = frame.f_code.co_filename
            if f not in self._globals_modules:
                self._globals_modules[f] = frame.f_globals
            self._parent_globals: dict[str, Any] = self._globals_modules[f]
        super().__init__(str(name))

    @classmethod
    def clear_globals(cls) -> None:
        """Clear the stored globals modules mapping."""
        with _lock:
            cls._globals_modules.clear()

    def _load(self) -> ModuleType:
        """Load the module and insert it into the parent's globals."""
        import importlib  # noqa: PLC0415

        if self._module:
            return self._module

        with _lock:
            if self._module:
                return self._module
            module: ModuleType = importlib.import_module(self.__name__)
            self._parent_globals[self._name] = module
            sys.modules[self._name] = module
            self.__dict__.update(module.__dict__)
            self._module = module
            return module

    @overload
    def to(self, n: str) -> LazyAttr: ...
    @overload
    def to(self, *n: str) -> tuple[LazyAttr, ...]: ...
    def to(self, n: str, *rest: str) -> LazyAttr | tuple[LazyAttr, ...]:
        """Get a lazy attribute from the module.

        Args:
            n (str): The name of the attribute to get.
            *rest (str): Additional attribute names to get.

        Returns:
            Any: The attribute from the module, or a tuple of attributes.
        """
        if rest:
            return tuple(LazyAttr(name, self) for name in (n, *rest))

        return LazyAttr(n, self)

    def to_many(self, *names: str) -> tuple[LazyAttr, ...]:
        """Get multiple lazy attributes from the module.

        Args:
            *names (str): The names of the attributes to get.

        Returns:
            tuple[LazyAttr, ...]: The attributes from the module.
        """
        return tuple(LazyAttr(n, self) for n in names)

    def __getattr__(self, item: str) -> Any:
        module: ModuleType = self._load()
        return getattr(module, item)

    def __dir__(self) -> list[str]:
        module: ModuleType = self._load()
        return dir(module)

    def __repr__(self) -> str:
        if not self._module:
            return f"<module '{self.__name__} (Not loaded yet)'>"
        return repr(self._module)


def lazy_module(n: str) -> LazyLoader:
    """Lazily load a module by its full name.

    Args:
        n (str): The full name of the module to load.

    Returns:
        LazyLoader: The lazy loader for the module.

    Raises:
        ImportError: If the module cannot be found or loaded.
    """
    return LazyLoader(n)


def lazy_attr(n: str, attr: str) -> LazyAttr:
    """Lazily load an attribute from a module by its full name.

    Args:
        n (str): The full name of the module to load.
        attr (str): The attribute name to load lazily from the module.

    Returns:
        LazyAttr: The lazy attribute.

    Raises:
        ImportError: If the module cannot be found or loaded.
    """
    loader: LazyLoader = LazyLoader(n)
    return loader.to(attr)


def lazy_attrs(n: str, *attrs: str) -> tuple[LazyAttr, ...]:
    """Lazily load attributes from a module by its full name.

    Args:
        n (str): The full name of the module to load.
        *attrs (str): The attribute names to load lazily from the module.

    Returns:
        tuple[LazyAttr, ...]: A tuple of lazy attributes.

    Raises:
        ImportError: If the module cannot be found or loaded.
    """
    loader: LazyLoader = LazyLoader(n)
    return loader.to_many(*attrs)


def lazy(n: str, *attrs: str) -> LazyLoader | tuple[LazyAttr, ...] | LazyAttr:
    """Lazily load a module by its full name.

    Args:
        n (str): The full name of the module to load.
        *attrs (str): Optional attribute names to load lazily from the module.

    Returns:
        LazyLoader | tuple[LazyAttr, ...] | LazyAttr: The loaded module, a tuple of lazy attributes, or a single lazy attribute.

    Raises:
        ImportError: If the module cannot be found or loaded.
    """
    if attrs:
        loader: LazyLoader = LazyLoader(n)

        if len(attrs) == 1:
            return loader.to(attrs[0])

        return loader.to_many(*attrs)
    return LazyLoader(n)


__all__ = ["LazyLoader", "lazy", "lazy_attr", "lazy_attrs", "lazy_module"]
