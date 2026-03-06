# src/notikit/providers/dingtalk.py
from __future__ import annotations

import hashlib
import hmac
import base64
import time
from urllib.parse import urlencode

import httpx

from notikit.exceptions import ProviderError
from notikit.providers import register
from notikit.providers.base import BaseProvider


@register("dingtalk")
class DingtalkProvider(BaseProvider):

    def __init__(self, config: dict):
        super().__init__(config)
        self.webhook_url = config["webhook_url"]
        self.sign_secret = config.get("sign_secret", "")

    def _sign_url(self) -> str:
        if not self.sign_secret:
            return self.webhook_url
        timestamp = str(int(time.time() * 1000))
        string_to_sign = f"{timestamp}\n{self.sign_secret}"
        hmac_code = hmac.new(
            self.sign_secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        sign = base64.b64encode(hmac_code).decode("utf-8")
        sep = "&" if "?" in self.webhook_url else "?"
        return f"{self.webhook_url}{sep}{urlencode({'timestamp': timestamp, 'sign': sign})}"

    @staticmethod
    def _payload(message: str, extra: dict | None = None) -> dict:
        data: dict = {"msgtype": "text", "text": {"content": message}}
        if extra:
            data.update(extra)
        return data

    def send(self, message: str, client: httpx.Client, extra: dict | None = None) -> None:
        resp = client.post(self._sign_url(), json=self._payload(message, extra))
        self._check_response(resp)

    async def asend(self, message: str, client: httpx.AsyncClient, extra: dict | None = None) -> None:
        resp = await client.post(self._sign_url(), json=self._payload(message, extra))
        self._check_response(resp)

    def _check_response(self, resp: httpx.Response) -> None:
        if resp.status_code != 200:
            raise ProviderError(self.name, f"HTTP {resp.status_code}: {resp.text}")
        data = resp.json()
        if data.get("errcode", 0) != 0:
            raise ProviderError(self.name, data.get("errmsg", "未知错误"))
