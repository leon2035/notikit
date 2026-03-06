# tests/test_providers/test_lark.py
import httpx
import pytest
import respx

from notikit.providers.lark import LarkProvider

WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/abc123"


@respx.mock
def test_lark_send():
    route = respx.post(WEBHOOK).mock(
        return_value=httpx.Response(200, json={"code": 0})
    )
    provider = LarkProvider({
        "webhook_url": WEBHOOK,
        "sign_secret": "secret",
    })
    with httpx.Client() as client:
        provider.send("测试消息", client)
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_lark_asend():
    route = respx.post(WEBHOOK).mock(
        return_value=httpx.Response(200, json={"code": 0})
    )
    provider = LarkProvider({
        "webhook_url": WEBHOOK,
        "sign_secret": "secret",
    })
    async with httpx.AsyncClient() as client:
        await provider.asend("测试消息", client)
    assert route.called


@respx.mock
def test_lark_send_error():
    respx.post(WEBHOOK).mock(
        return_value=httpx.Response(200, json={"code": 19021, "msg": "sign match fail"})
    )
    provider = LarkProvider({
        "webhook_url": WEBHOOK,
        "sign_secret": "secret",
    })
    from notikit.exceptions import ProviderError
    with httpx.Client() as client:
        with pytest.raises(ProviderError):
            provider.send("测试消息", client)
