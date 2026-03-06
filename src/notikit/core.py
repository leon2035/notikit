# src/notikit/core.py
from __future__ import annotations

from pathlib import Path

import httpx

from notikit.config import NotikitConfig, load_config
from notikit.exceptions import ProviderError, SendError
from notikit.providers import get_provider
from notikit.providers.base import BaseProvider


class Notikit:

    def __init__(
        self,
        config_path: Path | None = None,
        config_dict: dict | None = None,
    ):
        self._config = load_config(config_path=config_path, config_dict=config_dict)
        self._providers: dict[str, BaseProvider] = {}
        for name, cfg in self._config.providers.items():
            cls = get_provider(name)
            self._providers[name] = cls(cfg)

    def notify(
        self,
        message: str,
        *,
        channels: list[str] | None = None,
        params: dict[str, dict] | None = None,
    ) -> None:
        targets = channels or self._config.channels
        errors: list[ProviderError] = []
        with httpx.Client(timeout=self._config.timeout) as client:
            for name in targets:
                if name not in self._providers:
                    errors.append(ProviderError(name, f"未配置的渠道: {name}"))
                    continue
                provider = self._providers[name]
                extra = (params or {}).get(name)
                try:
                    provider.send(message, client, extra)
                except httpx.TimeoutException:
                    errors.append(ProviderError(name, "请求超时"))
                except ProviderError as e:
                    errors.append(e)
        if errors:
            raise SendError(errors)

    async def anotify(
        self,
        message: str,
        *,
        channels: list[str] | None = None,
        params: dict[str, dict] | None = None,
    ) -> None:
        targets = channels or self._config.channels
        errors: list[ProviderError] = []
        async with httpx.AsyncClient(timeout=self._config.timeout) as client:
            for name in targets:
                if name not in self._providers:
                    errors.append(ProviderError(name, f"未配置的渠道: {name}"))
                    continue
                provider = self._providers[name]
                extra = (params or {}).get(name)
                try:
                    await provider.asend(message, client, extra)
                except httpx.TimeoutException:
                    errors.append(ProviderError(name, "请求超时"))
                except ProviderError as e:
                    errors.append(e)
        if errors:
            raise SendError(errors)
