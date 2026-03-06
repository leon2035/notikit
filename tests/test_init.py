# tests/test_init.py
import httpx
import respx
import pytest

import notikit
from notikit import Notikit, notify, anotify


def test_public_api_exports():
    from notikit import Notikit, notify, anotify, NotikitError, ConfigError, ProviderError, SendError
    assert callable(notify)
    assert callable(anotify)


@respx.mock
def test_notify_function(tmp_path, monkeypatch):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark"]

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"
""")
    monkeypatch.chdir(tmp_path)
    route = respx.post("https://api.day.app/key123/").mock(
        return_value=httpx.Response(200, json={"code": 200})
    )
    # 重置单例以便测试
    notikit._default_instance = None
    notify("测试")
    assert route.called
