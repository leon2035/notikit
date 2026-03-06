# tests/test_providers/test_telegram.py
import httpx
import pytest
import respx

from notikit.providers.telegram import TelegramProvider

API_URL = "https://api.telegram.org/botTOKEN123/sendMessage"


@respx.mock
def test_telegram_send():
    route = respx.post(API_URL).mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    provider = TelegramProvider({"bot_token": "TOKEN123", "chat_id": "999"})
    with httpx.Client() as client:
        provider.send("测试消息", client)
    assert route.called
    request = route.calls[0].request
    assert b"999" in request.content


@respx.mock
@pytest.mark.asyncio
async def test_telegram_asend():
    route = respx.post(API_URL).mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    provider = TelegramProvider({"bot_token": "TOKEN123", "chat_id": "999"})
    async with httpx.AsyncClient() as client:
        await provider.asend("测试消息", client)
    assert route.called
