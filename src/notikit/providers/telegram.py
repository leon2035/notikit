# src/notikit/providers/telegram.py
from __future__ import annotations

import httpx

from notikit.exceptions import ProviderError
from notikit.providers import register
from notikit.providers.base import BaseProvider


@register("telegram")
class TelegramProvider(BaseProvider):

    def __init__(self, config: dict):
        super().__init__(config)
        self.bot_token = config["bot_token"]
        self.chat_id = config["chat_id"]

    @property
    def _url(self) -> str:
        return f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def _payload(self, message: str, extra: dict | None = None) -> dict:
        data = {"chat_id": self.chat_id, "text": message}
        if extra:
            data.update(extra)
        return data

    def send(self, message: str, client: httpx.Client, extra: dict | None = None) -> None:
        resp = client.post(self._url, json=self._payload(message, extra))
        self._check_response(resp)

    async def asend(self, message: str, client: httpx.AsyncClient, extra: dict | None = None) -> None:
        resp = await client.post(self._url, json=self._payload(message, extra))
        self._check_response(resp)

    def _check_response(self, resp: httpx.Response) -> None:
        if resp.status_code != 200:
            raise ProviderError(self.name, f"HTTP {resp.status_code}: {resp.text}")
        data = resp.json()
        if data.get("ok") is not True:
            raise ProviderError(self.name, data.get("description", "未知错误"))
