# src/notikit/__init__.py
"""notikit - 轻量级 Python 通知工具包"""

from notikit.core import Notikit
from notikit.exceptions import ConfigError, NotikitError, NotikitTimeoutError, ProviderError, SendError

__all__ = [
    "Notikit",
    "notify",
    "anotify",
    "NotikitError",
    "ConfigError",
    "ProviderError",
    "SendError",
    "NotikitTimeoutError",
]

_default_instance: Notikit | None = None


def _get_default() -> Notikit:
    global _default_instance
    if _default_instance is None:
        _default_instance = Notikit()
    return _default_instance


def notify(
    message: str,
    *,
    channels: list[str] | None = None,
    params: dict[str, dict] | None = None,
) -> None:
    _get_default().notify(message, channels=channels, params=params)


async def anotify(
    message: str,
    *,
    channels: list[str] | None = None,
    params: dict[str, dict] | None = None,
) -> None:
    await _get_default().anotify(message, channels=channels, params=params)
