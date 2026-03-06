# tests/test_config.py
import pytest
from pathlib import Path
from notikit.config import load_config
from notikit.exceptions import ConfigError


def test_load_config_from_path(tmp_path: Path):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["lark"]

[notikit.lark]
webhook_url = "https://example.com/hook"
sign_secret = "secret123"
""")
    config = load_config(config_path=config_file)
    assert config.channels == ["lark"]
    assert config.providers["lark"]["webhook_url"] == "https://example.com/hook"


def test_load_config_with_timeout(tmp_path: Path):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark"]
timeout = 5

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"
""")
    config = load_config(config_path=config_file)
    assert config.timeout == 5


def test_load_config_default_timeout(tmp_path: Path):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark"]

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"
""")
    config = load_config(config_path=config_file)
    assert config.timeout == 10


def test_load_config_file_not_found():
    with pytest.raises(ConfigError, match="找不到配置文件"):
        load_config(config_path=Path("/nonexistent/notikit.toml"))


def test_load_config_from_dict():
    data = {
        "channels": ["telegram"],
        "timeout": 10,
        "providers": {
            "telegram": {"bot_token": "token", "chat_id": "123"},
        },
    }
    config = load_config(config_dict=data)
    assert config.channels == ["telegram"]


def test_load_config_auto_discover(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark"]

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"
""")
    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert config.channels == ["bark"]
