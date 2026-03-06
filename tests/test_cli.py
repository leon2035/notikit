import httpx
import pytest
import respx

from notikit.cli import main


@respx.mock
def test_cli_basic(tmp_path, monkeypatch):
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
    main(["测试消息", "--config", str(config_file)])
    assert route.called


@respx.mock
def test_cli_with_channels(tmp_path):
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
    main(["测试", "--config", str(config_file), "-c", "bark"])
    assert bark_route.called
    assert not tg_route.called


def test_cli_version(capsys):
    main(["-v"])
    output = capsys.readouterr().out
    assert "notikit" in output


def test_cli_config_not_found():
    with pytest.raises(SystemExit):
        main(["测试", "--config", "/nonexistent/notikit.toml"])
