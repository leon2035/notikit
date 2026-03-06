# src/notikit/providers/__init__.py
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from notikit.providers.base import BaseProvider

_PROVIDERS: dict[str, type[BaseProvider]] = {}


def register(name: str):
    def decorator(cls: type[BaseProvider]):
        _PROVIDERS[name] = cls
        cls.name = name
        return cls

    return decorator


def get_provider(name: str) -> type[BaseProvider]:
    if name not in _PROVIDERS:
        _import_provider(name)
    return _PROVIDERS[name]


def _import_provider(name: str) -> None:
    import importlib

    try:
        importlib.import_module(f"notikit.providers.{name}")
    except ImportError:
        pass
    if name not in _PROVIDERS:
        from notikit.exceptions import ConfigError

        raise ConfigError(f"未知的 provider: {name}")
