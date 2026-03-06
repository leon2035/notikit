# src/notikit/config.py
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from notikit.exceptions import ConfigError

_KNOWN_KEYS = {"channels", "timeout"}


@dataclass
class NotikitConfig:
    channels: list[str]
    timeout: int = 10
    providers: dict[str, dict] = field(default_factory=dict)


def load_config(
    config_path: Path | None = None,
    config_dict: dict | None = None,
) -> NotikitConfig:
    if config_dict is not None:
        return NotikitConfig(
            channels=config_dict["channels"],
            timeout=config_dict.get("timeout", 10),
            providers=config_dict.get("providers", {}),
        )

    path = _resolve_path(config_path)
    return _parse_file(path)


def _resolve_path(config_path: Path | None) -> Path:
    if config_path is not None:
        if not config_path.exists():
            raise ConfigError(f"找不到配置文件: {config_path}")
        return config_path

    candidates = [
        Path.cwd() / "notikit.toml",
        Path.home() / ".notikit.toml",
    ]
    for p in candidates:
        if p.exists():
            return p

    raise ConfigError("找不到配置文件，请创建 notikit.toml 或 ~/.notikit.toml")


def _parse_file(path: Path) -> NotikitConfig:
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    section = raw.get("notikit", {})
    channels = section.get("channels", [])
    timeout = section.get("timeout", 10)

    providers = {}
    for key, value in section.items():
        if key not in _KNOWN_KEYS and isinstance(value, dict):
            providers[key] = value

    return NotikitConfig(channels=channels, timeout=timeout, providers=providers)
