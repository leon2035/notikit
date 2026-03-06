# src/notikit/providers/bark.py
from __future__ import annotations

import httpx

from notikit.exceptions import ProviderError
from notikit.providers import register
from notikit.providers.base import BaseProvider


@register("bark")
class BarkProvider(BaseProvider):

    def __init__(self, config: dict):
        super().__init__(config)
        self.server_url = config["server_url"].rstrip("/")
        self.device_key = config["device_key"]

    @property
    def _url(self) -> str:
        return f"{self.server_url}/{self.device_key}/"

    def send(self, message: str, client: httpx.Client, extra: dict | None = None) -> None:
        resp = client.post(self._url, json=self._payload(message, extra))
        self._check_response(resp)

    async def asend(self, message: str, client: httpx.AsyncClient, extra: dict | None = None) -> None:
        resp = await client.post(self._url, json=self._payload(message, extra))
        self._check_response(resp)

    @staticmethod
    def _payload(message: str, extra: dict | None = None) -> dict:
        data = {"body": message}
        if extra:
            data.update(extra)
        return data

    def _check_response(self, resp: httpx.Response) -> None:
        if resp.status_code != 200:
            raise ProviderError(self.name, f"HTTP {resp.status_code}: {resp.text}")
        data = resp.json()
        if data.get("code") != 200:
            raise ProviderError(self.name, data.get("message", "未知错误"))
