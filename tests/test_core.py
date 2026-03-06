# tests/test_core.py
import httpx
import pytest
import respx

from notikit.core import Notikit


@respx.mock
def test_notify_single_channel(tmp_path):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark"]

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"
""")
    route = respx.post("https://api.day.app/key123/").mock(
        return_value=httpx.Response(200, json={"code": 200})
    )
    nk = Notikit(config_path=config_file)
    nk.notify("测试")
    assert route.called


@respx.mock
def test_notify_override_channels(tmp_path):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark", "telegram"]

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"

[notikit.telegram]
bot_token = "TOKEN"
chat_id = "999"
""")
    bark_route = respx.post("https://api.day.app/key123/").mock(
        return_value=httpx.Response(200, json={"code": 200})
    )
    tg_route = respx.post("https://api.telegram.org/botTOKEN/sendMessage").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    nk = Notikit(config_path=config_file)
    nk.notify("测试", channels=["telegram"])
    assert not bark_route.called
    assert tg_route.called


@respx.mock
@pytest.mark.asyncio
async def test_anotify(tmp_path):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark"]

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"
""")
    route = respx.post("https://api.day.app/key123/").mock(
        return_value=httpx.Response(200, json={"code": 200})
    )
    nk = Notikit(config_path=config_file)
    await nk.anotify("测试")
    assert route.called


@respx.mock
def test_notify_partial_failure(tmp_path):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark", "telegram"]

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"

[notikit.telegram]
bot_token = "TOKEN"
chat_id = "999"
""")
    respx.post("https://api.day.app/key123/").mock(
        return_value=httpx.Response(500)
    )
    tg_route = respx.post("https://api.telegram.org/botTOKEN/sendMessage").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    nk = Notikit(config_path=config_file)
    from notikit.exceptions import SendError
    with pytest.raises(SendError) as exc_info:
        nk.notify("测试")
    assert len(exc_info.value.errors) == 1
    assert exc_info.value.errors[0].provider == "bark"
    assert tg_route.called


@respx.mock
def test_notify_unknown_channel(tmp_path):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark"]

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"
""")
    nk = Notikit(config_path=config_file)
    from notikit.exceptions import SendError
    with pytest.raises(SendError) as exc_info:
        nk.notify("测试", channels=["nonexistent"])
    assert len(exc_info.value.errors) == 1
    assert "未配置的渠道" in str(exc_info.value.errors[0])


@respx.mock
@pytest.mark.asyncio
async def test_anotify_unknown_channel(tmp_path):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark"]

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"
""")
    nk = Notikit(config_path=config_file)
    from notikit.exceptions import SendError
    with pytest.raises(SendError) as exc_info:
        await nk.anotify("测试", channels=["nonexistent"])
    assert len(exc_info.value.errors) == 1
    assert "未配置的渠道" in str(exc_info.value.errors[0])


def test_notify_from_dict():
    nk = Notikit(config_dict={
        "channels": ["bark"],
        "providers": {
            "bark": {"server_url": "https://api.day.app", "device_key": "k"},
        },
    })
    assert nk._config.channels == ["bark"]
