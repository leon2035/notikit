# tests/test_providers/test_bark.py
import httpx
import pytest
import respx

from notikit.providers.bark import BarkProvider


@respx.mock
def test_bark_send():
    route = respx.post("https://api.day.app/key123/").mock(
        return_value=httpx.Response(200, json={"code": 200})
    )
    provider = BarkProvider({"server_url": "https://api.day.app", "device_key": "key123"})
    with httpx.Client() as client:
        provider.send("测试消息", client)
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_bark_asend():
    route = respx.post("https://api.day.app/key123/").mock(
        return_value=httpx.Response(200, json={"code": 200})
    )
    provider = BarkProvider({"server_url": "https://api.day.app", "device_key": "key123"})
    async with httpx.AsyncClient() as client:
        await provider.asend("测试消息", client)
    assert route.called
