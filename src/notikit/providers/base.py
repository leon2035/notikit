# src/notikit/providers/base.py
from __future__ import annotations

from abc import ABC, abstractmethod

import httpx


class BaseProvider(ABC):
    """Provider 抽象基类"""

    name: str

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def send(self, message: str, client: httpx.Client, extra: dict | None = None) -> None: ...

    @abstractmethod
    async def asend(self, message: str, client: httpx.AsyncClient, extra: dict | None = None) -> None: ...
