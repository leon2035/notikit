# notikit Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 创建轻量级 Python 通知工具包 notikit，支持 bark/telegram/dingtalk/lark 四个渠道，同步+异步 API。

**Architecture:** src layout + hatchling 构建。Notikit 核心类管理配置和 provider，BaseProvider 抽象基类定义 send/asend 接口，每个渠道一个 provider 实现。函数式 API (notify/anotify) 通过内部单例代理。

**Tech Stack:** Python 3.10+, httpx, tomllib (stdlib), hatchling, pytest + pytest-asyncio

---

### Task 1: 项目脚手架

**Files:**
- Create: `pyproject.toml`
- Create: `src/notikit/__init__.py`
- Create: `README.md`

**Step 1: 创建 pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "notikit"
version = "0.1.0"
description = "轻量级 Python 通知工具包，统一接口发送多渠道消息"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
dependencies = ["httpx>=0.24.0"]

[project.optional-dependencies]
dev = ["pytest>=7.0", "pytest-asyncio>=0.21", "respx>=0.20"]

[tool.hatch.build.targets.wheel]
packages = ["src/notikit"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

**Step 2: 创建空的 `src/notikit/__init__.py`**

```python
"""notikit - 轻量级 Python 通知工具包"""
```

**Step 3: 创建 README.md**

简要说明项目用途的 README。

**Step 4: 安装项目到开发环境**

Run: `pip install -e ".[dev]"`
Expected: 成功安装 notikit 及开发依赖

**Step 5: Commit**

```bash
git init
git add pyproject.toml src/notikit/__init__.py README.md
git commit -m "chore: 初始化项目脚手架"
```

---

### Task 2: 异常体系

**Files:**
- Create: `src/notikit/exceptions.py`
- Create: `tests/test_exceptions.py`

**Step 1: 编写异常测试**

```python
# tests/test_exceptions.py
from notikit.exceptions import NotikitError, ConfigError, ProviderError, TimeoutError


def test_exception_hierarchy():
    assert issubclass(ConfigError, NotikitError)
    assert issubclass(ProviderError, NotikitError)
    assert issubclass(TimeoutError, NotikitError)


def test_provider_error_contains_provider_name():
    err = ProviderError("lark", "发送失败")
    assert err.provider == "lark"
    assert "lark" in str(err)
    assert "发送失败" in str(err)
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_exceptions.py -v`
Expected: FAIL - ModuleNotFoundError

**Step 3: 实现异常类**

```python
# src/notikit/exceptions.py


class NotikitError(Exception):
    """notikit 基础异常"""


class ConfigError(NotikitError):
    """配置错误"""


class ProviderError(NotikitError):
    """Provider 发送失败"""

    def __init__(self, provider: str, message: str):
        self.provider = provider
        super().__init__(f"[{provider}] {message}")


class TimeoutError(NotikitError):
    """请求超时"""


class SendError(NotikitError):
    """聚合多个 provider 的发送错误"""

    def __init__(self, errors: list[ProviderError]):
        self.errors = errors
        names = ", ".join(e.provider for e in errors)
        super().__init__(f"发送失败: {names}")
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_exceptions.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/notikit/exceptions.py tests/test_exceptions.py
git commit -m "feat: 添加异常体系"
```

---

### Task 3: 配置加载

**Files:**
- Create: `src/notikit/config.py`
- Create: `tests/test_config.py`

**Step 1: 编写配置测试**

```python
# tests/test_config.py
import pytest
from pathlib import Path
from notikit.config import load_config
from notikit.exceptions import ConfigError


def test_load_config_from_path(tmp_path: Path):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["lark"]

[notikit.lark]
webhook_url = "https://example.com/hook"
sign_secret = "secret123"
""")
    config = load_config(config_path=config_file)
    assert config.channels == ["lark"]
    assert config.providers["lark"]["webhook_url"] == "https://example.com/hook"


def test_load_config_with_timeout(tmp_path: Path):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark"]
timeout = 5

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"
""")
    config = load_config(config_path=config_file)
    assert config.timeout == 5


def test_load_config_default_timeout(tmp_path: Path):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark"]

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"
""")
    config = load_config(config_path=config_file)
    assert config.timeout == 10


def test_load_config_file_not_found():
    with pytest.raises(ConfigError, match="找不到配置文件"):
        load_config(config_path=Path("/nonexistent/notikit.toml"))


def test_load_config_from_dict():
    data = {
        "channels": ["telegram"],
        "timeout": 10,
        "providers": {
            "telegram": {"bot_token": "token", "chat_id": "123"},
        },
    }
    config = load_config(config_dict=data)
    assert config.channels == ["telegram"]


def test_load_config_auto_discover(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark"]

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"
""")
    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert config.channels == ["bark"]
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_config.py -v`
Expected: FAIL

**Step 3: 实现配置加载**

```python
# src/notikit/config.py
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from notikit.exceptions import ConfigError

_KNOWN_KEYS = {"channels", "timeout"}


@dataclass
class NotikitConfig:
    channels: list[str]
    timeout: int = 10
    providers: dict[str, dict] = field(default_factory=dict)


def load_config(
    config_path: Path | None = None,
    config_dict: dict | None = None,
) -> NotikitConfig:
    if config_dict is not None:
        return NotikitConfig(
            channels=config_dict["channels"],
            timeout=config_dict.get("timeout", 10),
            providers=config_dict.get("providers", {}),
        )

    path = _resolve_path(config_path)
    return _parse_file(path)


def _resolve_path(config_path: Path | None) -> Path:
    if config_path is not None:
        if not config_path.exists():
            raise ConfigError(f"找不到配置文件: {config_path}")
        return config_path

    candidates = [
        Path.cwd() / "notikit.toml",
        Path.home() / ".notikit.toml",
    ]
    for p in candidates:
        if p.exists():
            return p

    raise ConfigError("找不到配置文件，请创建 notikit.toml 或 ~/.notikit.toml")


def _parse_file(path: Path) -> NotikitConfig:
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    section = raw.get("notikit", {})
    channels = section.get("channels", [])
    timeout = section.get("timeout", 10)

    providers = {}
    for key, value in section.items():
        if key not in _KNOWN_KEYS and isinstance(value, dict):
            providers[key] = value

    return NotikitConfig(channels=channels, timeout=timeout, providers=providers)
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/notikit/config.py tests/test_config.py
git commit -m "feat: 添加配置加载模块"
```

---

### Task 4: Provider 基类

**Files:**
- Create: `src/notikit/providers/__init__.py`
- Create: `src/notikit/providers/base.py`

**Step 1: 创建 provider 基类**

```python
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
    def send(self, message: str, client: httpx.Client) -> None: ...

    @abstractmethod
    async def asend(self, message: str, client: httpx.AsyncClient) -> None: ...
```

**Step 2: 创建 provider 注册表**

```python
# src/notikit/providers/__init__.py
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from notikit.providers.base import BaseProvider

_PROVIDERS: dict[str, type[BaseProvider]] = {}


def register(name: str):
    def decorator(cls: type[BaseProvider]):
        _PROVIDERS[name] = cls
        cls.name = name
        return cls
    return decorator


def get_provider(name: str) -> type[BaseProvider]:
    if name not in _PROVIDERS:
        # 延迟导入以触发 register 装饰器
        _import_provider(name)
    return _PROVIDERS[name]


def _import_provider(name: str) -> None:
    import importlib
    try:
        importlib.import_module(f"notikit.providers.{name}")
    except ImportError:
        pass
    if name not in _PROVIDERS:
        from notikit.exceptions import ConfigError
        raise ConfigError(f"未知的 provider: {name}")
```

**Step 3: Commit**

```bash
git add src/notikit/providers/__init__.py src/notikit/providers/base.py
git commit -m "feat: 添加 provider 基类和注册表"
```

---

### Task 5: Bark Provider

**Files:**
- Create: `src/notikit/providers/bark.py`
- Create: `tests/test_providers/test_bark.py`

**Step 1: 编写测试**

```python
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
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_providers/test_bark.py -v`
Expected: FAIL

**Step 3: 实现 BarkProvider**

```python
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

    def send(self, message: str, client: httpx.Client) -> None:
        resp = client.post(self._url, json={"body": message})
        self._check_response(resp)

    async def asend(self, message: str, client: httpx.AsyncClient) -> None:
        resp = await client.post(self._url, json={"body": message})
        self._check_response(resp)

    def _check_response(self, resp: httpx.Response) -> None:
        if resp.status_code != 200:
            raise ProviderError("bark", f"HTTP {resp.status_code}: {resp.text}")
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_providers/test_bark.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/notikit/providers/bark.py tests/test_providers/test_bark.py
git commit -m "feat: 添加 bark provider"
```

---

### Task 6: Telegram Provider

**Files:**
- Create: `src/notikit/providers/telegram.py`
- Create: `tests/test_providers/test_telegram.py`

**Step 1: 编写测试**

```python
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
    assert b"测试消息" in request.content or "测试消息" in request.content.decode()


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
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_providers/test_telegram.py -v`
Expected: FAIL

**Step 3: 实现 TelegramProvider**

```python
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

    def _payload(self, message: str) -> dict:
        return {"chat_id": self.chat_id, "text": message}

    def send(self, message: str, client: httpx.Client) -> None:
        resp = client.post(self._url, json=self._payload(message))
        self._check_response(resp)

    async def asend(self, message: str, client: httpx.AsyncClient) -> None:
        resp = await client.post(self._url, json=self._payload(message))
        self._check_response(resp)

    def _check_response(self, resp: httpx.Response) -> None:
        if resp.status_code != 200:
            raise ProviderError("telegram", f"HTTP {resp.status_code}: {resp.text}")
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_providers/test_telegram.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/notikit/providers/telegram.py tests/test_providers/test_telegram.py
git commit -m "feat: 添加 telegram provider"
```

---

### Task 7: 钉钉 Provider

**Files:**
- Create: `src/notikit/providers/dingtalk.py`
- Create: `tests/test_providers/test_dingtalk.py`

**Step 1: 编写测试**

```python
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
    with httpx.Client() as client:
        with pytest.raises(Exception):
            provider.send("测试消息", client)
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_providers/test_dingtalk.py -v`
Expected: FAIL

**Step 3: 实现 DingtalkProvider**

```python
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
        self.sign_secret = config["sign_secret"]

    def _sign_url(self) -> str:
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
    def _payload(message: str) -> dict:
        return {"msgtype": "text", "text": {"content": message}}

    def send(self, message: str, client: httpx.Client) -> None:
        resp = client.post(self._sign_url(), json=self._payload(message))
        self._check_response(resp)

    async def asend(self, message: str, client: httpx.AsyncClient) -> None:
        resp = await client.post(self._sign_url(), json=self._payload(message))
        self._check_response(resp)

    def _check_response(self, resp: httpx.Response) -> None:
        if resp.status_code != 200:
            raise ProviderError("dingtalk", f"HTTP {resp.status_code}: {resp.text}")
        data = resp.json()
        if data.get("errcode", 0) != 0:
            raise ProviderError("dingtalk", data.get("errmsg", "未知错误"))
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_providers/test_dingtalk.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/notikit/providers/dingtalk.py tests/test_providers/test_dingtalk.py
git commit -m "feat: 添加钉钉 provider"
```

---

### Task 8: 飞书 Provider

**Files:**
- Create: `src/notikit/providers/lark.py`
- Create: `tests/test_providers/test_lark.py`

**Step 1: 编写测试**

```python
# tests/test_providers/test_lark.py
import httpx
import pytest
import respx

from notikit.providers.lark import LarkProvider


@respx.mock
def test_lark_send():
    route = respx.post("https://open.feishu.cn/open-apis/bot/v2/hook/abc123").mock(
        return_value=httpx.Response(200, json={"code": 0})
    )
    provider = LarkProvider({
        "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/abc123",
        "sign_secret": "secret",
    })
    with httpx.Client() as client:
        provider.send("测试消息", client)
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_lark_asend():
    route = respx.post("https://open.feishu.cn/open-apis/bot/v2/hook/abc123").mock(
        return_value=httpx.Response(200, json={"code": 0})
    )
    provider = LarkProvider({
        "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/abc123",
        "sign_secret": "secret",
    })
    async with httpx.AsyncClient() as client:
        await provider.asend("测试消息", client)
    assert route.called


@respx.mock
def test_lark_send_error():
    respx.post("https://open.feishu.cn/open-apis/bot/v2/hook/abc123").mock(
        return_value=httpx.Response(200, json={"code": 19021, "msg": "sign match fail"})
    )
    provider = LarkProvider({
        "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/abc123",
        "sign_secret": "secret",
    })
    with httpx.Client() as client:
        with pytest.raises(Exception):
            provider.send("测试消息", client)
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_providers/test_lark.py -v`
Expected: FAIL

**Step 3: 实现 LarkProvider**

```python
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

    def send(self, message: str, client: httpx.Client) -> None:
        resp = client.post(self.webhook_url, json=self._build_payload(message))
        self._check_response(resp)

    async def asend(self, message: str, client: httpx.AsyncClient) -> None:
        resp = await client.post(self.webhook_url, json=self._build_payload(message))
        self._check_response(resp)

    def _check_response(self, resp: httpx.Response) -> None:
        if resp.status_code != 200:
            raise ProviderError("lark", f"HTTP {resp.status_code}: {resp.text}")
        data = resp.json()
        if data.get("code", 0) != 0:
            raise ProviderError("lark", data.get("msg", "未知错误"))
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_providers/test_lark.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/notikit/providers/lark.py tests/test_providers/test_lark.py
git commit -m "feat: 添加飞书 provider"
```

---

### Task 9: Notikit 核心类

**Files:**
- Create: `src/notikit/core.py`
- Create: `tests/test_core.py`

**Step 1: 编写测试**

```python
# tests/test_core.py
import httpx
import pytest
import respx

from notikit.core import Notikit


@respx.mock
def test_notify_single_channel(tmp_path):
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
    nk = Notikit(config_path=config_file)
    nk.notify("测试")
    assert route.called


@respx.mock
def test_notify_override_channels(tmp_path):
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
    nk = Notikit(config_path=config_file)
    nk.notify("测试", channels=["telegram"])
    assert not bark_route.called
    assert tg_route.called


@respx.mock
@pytest.mark.asyncio
async def test_anotify(tmp_path):
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
    nk = Notikit(config_path=config_file)
    await nk.anotify("测试")
    assert route.called


@respx.mock
def test_notify_partial_failure(tmp_path):
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
    respx.post("https://api.day.app/key123/").mock(
        return_value=httpx.Response(500)
    )
    tg_route = respx.post("https://api.telegram.org/botTOKEN/sendMessage").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    nk = Notikit(config_path=config_file)
    from notikit.exceptions import SendError
    with pytest.raises(SendError) as exc_info:
        nk.notify("测试")
    assert len(exc_info.value.errors) == 1
    assert exc_info.value.errors[0].provider == "bark"
    assert tg_route.called  # telegram 仍然被调用


def test_notify_from_dict():
    nk = Notikit(config_dict={
        "channels": ["bark"],
        "providers": {
            "bark": {"server_url": "https://api.day.app", "device_key": "k"},
        },
    })
    assert nk._config.channels == ["bark"]
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_core.py -v`
Expected: FAIL

**Step 3: 实现 Notikit 核心类**

```python
# src/notikit/core.py
from __future__ import annotations

from pathlib import Path

import httpx

from notikit.config import NotikitConfig, load_config
from notikit.exceptions import ProviderError, SendError, TimeoutError
from notikit.providers import get_provider
from notikit.providers.base import BaseProvider


class Notikit:

    def __init__(
        self,
        config_path: Path | None = None,
        config_dict: dict | None = None,
    ):
        self._config = load_config(config_path=config_path, config_dict=config_dict)
        self._providers: dict[str, BaseProvider] = {}
        for name, cfg in self._config.providers.items():
            cls = get_provider(name)
            self._providers[name] = cls(cfg)

    def notify(self, message: str, *, channels: list[str] | None = None) -> None:
        targets = channels or self._config.channels
        errors: list[ProviderError] = []
        with httpx.Client(timeout=self._config.timeout) as client:
            for name in targets:
                provider = self._providers[name]
                try:
                    provider.send(message, client)
                except httpx.TimeoutException:
                    errors.append(ProviderError(name, "请求超时"))
                except ProviderError as e:
                    errors.append(e)
        if errors:
            raise SendError(errors)

    async def anotify(self, message: str, *, channels: list[str] | None = None) -> None:
        targets = channels or self._config.channels
        errors: list[ProviderError] = []
        async with httpx.AsyncClient(timeout=self._config.timeout) as client:
            for name in targets:
                provider = self._providers[name]
                try:
                    await provider.asend(message, client)
                except httpx.TimeoutException:
                    errors.append(ProviderError(name, "请求超时"))
                except ProviderError as e:
                    errors.append(e)
        if errors:
            raise SendError(errors)
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_core.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/notikit/core.py tests/test_core.py
git commit -m "feat: 添加 Notikit 核心类"
```

---

### Task 10: 公共 API 导出 + 函数式接口

**Files:**
- Modify: `src/notikit/__init__.py`
- Create: `tests/test_init.py`

**Step 1: 编写测试**

```python
# tests/test_init.py
import httpx
import respx

from notikit import Notikit, notify, anotify


def test_public_api_exports():
    from notikit import Notikit, notify, anotify, NotikitError, ConfigError, ProviderError, SendError
    assert callable(notify)
    assert callable(anotify)


@respx.mock
def test_notify_function(tmp_path, monkeypatch):
    config_file = tmp_path / "notikit.toml"
    config_file.write_text("""
[notikit]
channels = ["bark"]

[notikit.bark]
server_url = "https://api.day.app"
device_key = "key123"
""")
    monkeypatch.chdir(tmp_path)
    route = respx.post("https://api.day.app/key123/").mock(
        return_value=httpx.Response(200, json={"code": 200})
    )
    # 重置单例以便测试
    import notikit
    notikit._default_instance = None
    notify("测试")
    assert route.called
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_init.py -v`
Expected: FAIL

**Step 3: 实现公共 API**

```python
# src/notikit/__init__.py
"""notikit - 轻量级 Python 通知工具包"""

from notikit.core import Notikit
from notikit.exceptions import ConfigError, NotikitError, ProviderError, SendError, TimeoutError

__all__ = [
    "Notikit",
    "notify",
    "anotify",
    "NotikitError",
    "ConfigError",
    "ProviderError",
    "SendError",
    "TimeoutError",
]

_default_instance: Notikit | None = None


def _get_default() -> Notikit:
    global _default_instance
    if _default_instance is None:
        _default_instance = Notikit()
    return _default_instance


def notify(message: str, *, channels: list[str] | None = None) -> None:
    _get_default().notify(message, channels=channels)


async def anotify(message: str, *, channels: list[str] | None = None) -> None:
    await _get_default().anotify(message, channels=channels)
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_init.py -v`
Expected: PASS

**Step 5: 运行全部测试**

Run: `pytest -v`
Expected: 全部 PASS

**Step 6: Commit**

```bash
git add src/notikit/__init__.py tests/test_init.py
git commit -m "feat: 添加公共 API 和函数式接口"
```

---

### Task 11: 创建 tests/__init__.py 和 tests/test_providers/__init__.py

**Files:**
- Create: `tests/__init__.py`（空文件）
- Create: `tests/test_providers/__init__.py`（空文件）

注意：这些文件在 Task 1 之后、运行测试之前就需要存在。实际执行时应在首次运行测试前创建。

---

### Task 12: 最终验证

**Step 1:** 运行全部测试 `pytest -v`
**Step 2:** 验证可以 `pip install -e .` 并 `python -c "from notikit import Notikit, notify"`
**Step 3:** 验证构建 `python -m build`
