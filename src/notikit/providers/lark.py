# src/notikit/providers/lark.py
from __future__ import annotations

import hashlib
import hmac
import base64
import time

import httpx

from notikit.exceptions import ProviderError
from notikit.providers import register
from notikit.providers.base import BaseProvider


@register("lark")
class LarkProvider(BaseProvider):

    def __init__(self, config: dict):
        super().__init__(config)
        self.webhook_url = config["webhook_url"]
        self.sign_secret = config.get("sign_secret", "")

    def _build_payload(self, message: str) -> dict:
        payload: dict = {
            "msg_type": "text",
            "content": {"text": message},
        }
        if self.sign_secret:
            timestamp = str(int(time.time()))
            string_to_sign = f"{timestamp}\n{self.sign_secret}"
            hmac_code = hmac.new(
                string_to_sign.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
            sign = base64.b64encode(hmac_code).decode("utf-8")
            payload["timestamp"] = timestamp
            payload["sign"] = sign
        return payload

    def send(self, message: str, client: httpx.Client, extra: dict | None = None) -> None:
        resp = client.post(self.webhook_url, json=self._build_payload(message))
        self._check_response(resp)

    async def asend(self, message: str, client: httpx.AsyncClient, extra: dict | None = None) -> None:
        resp = await client.post(self.webhook_url, json=self._build_payload(message))
        self._check_response(resp)

    def _check_response(self, resp: httpx.Response) -> None:
        if resp.status_code != 200:
            raise ProviderError(self.name, f"HTTP {resp.status_code}: {resp.text}")
        data = resp.json()
        if data.get("code", 0) != 0:
            raise ProviderError(self.name, data.get("msg", "未知错误"))
