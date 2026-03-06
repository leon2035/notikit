# tests/test_providers/test_dingtalk.py
import httpx
import pytest
import respx

from notikit.providers.dingtalk import DingtalkProvider


@respx.mock
def test_dingtalk_send():
    route = respx.post(url__startswith="https://oapi.dingtalk.com/robot/send").mock(
        return_value=httpx.Response(200, json={"errcode": 0})
    )
    provider = DingtalkProvider({
        "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=abc",
        "sign_secret": "SEC123",
    })
    with httpx.Client() as client:
        provider.send("测试消息", client)
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_dingtalk_asend():
    route = respx.post(url__startswith="https://oapi.dingtalk.com/robot/send").mock(
        return_value=httpx.Response(200, json={"errcode": 0})
    )
    provider = DingtalkProvider({
        "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=abc",
        "sign_secret": "SEC123",
    })
    async with httpx.AsyncClient() as client:
        await provider.asend("测试消息", client)
    assert route.called


@respx.mock
def test_dingtalk_send_error():
    respx.post(url__startswith="https://oapi.dingtalk.com/robot/send").mock(
        return_value=httpx.Response(200, json={"errcode": 310000, "errmsg": "sign not match"})
    )
    provider = DingtalkProvider({
        "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=abc",
        "sign_secret": "SEC123",
    })
    from notikit.exceptions import ProviderError
    with httpx.Client() as client:
        with pytest.raises(ProviderError):
            provider.send("测试消息", client)
