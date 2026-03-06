# notikit 设计文档

## 概述

notikit 是一个轻量级 Python 通知工具包，提供统一接口向多个通知渠道发送消息。适合脚本、自动化任务、CI、监控通知等场景。

## 设计原则

- Simple > Feature rich
- Minimal dependencies
- Pythonic API
- 易扩展 provider

## 技术约束

- Python 3.10+
- 唯一第三方依赖：httpx
- 使用 Python 3.10+ 内置 tomllib 解析配置
- 构建后端：hatchling，src layout

## 支持的 Provider

| Provider | 说明 |
|----------|------|
| bark | iOS Bark 推送 |
| telegram | Telegram Bot |
| dingtalk | 钉钉机器人 |
| lark | 飞书机器人 |

## 项目结构

```
notikit/
├── pyproject.toml
├── src/
│   └── notikit/
│       ├── __init__.py          # 公共 API: notify, anotify, Notikit
│       ├── core.py              # Notikit 类，核心逻辑
│       ├── config.py            # 配置加载
│       ├── exceptions.py        # 异常体系
│       └── providers/
│           ├── __init__.py      # Provider 注册表
│           ├── base.py          # BaseProvider 抽象基类
│           ├── bark.py          # Bark
│           ├── telegram.py      # Telegram
│           ├── dingtalk.py      # 钉钉
│           └── lark.py          # 飞书
└── tests/
    ├── test_config.py
    ├── test_core.py
    └── test_providers/
        ├── test_bark.py
        ├── test_telegram.py
        ├── test_dingtalk.py
        └── test_lark.py
```

## API 设计

### 简单用法（函数式，内部单例）

```python
from notikit import notify, anotify

notify("部署完成")
await anotify("部署完成")
```

### 灵活用法（实例化）

```python
from notikit import Notikit

nk = Notikit(config_path="custom.toml")
nk.notify("部署完成", channels=["lark"])
await nk.anotify("部署完成", channels=["bark", "telegram"])
```

### 异步支持

同一个 Notikit 类，提供同步和异步方法：

- `notify(message, channels=None)` — 同步发送
- `anotify(message, channels=None)` — 异步发送

内部同步使用 `httpx.Client`，异步使用 `httpx.AsyncClient`。

## Provider 抽象

```python
class BaseProvider(ABC):
    def __init__(self, config: dict): ...

    @abstractmethod
    def send(self, message: str, client: httpx.Client) -> None: ...

    @abstractmethod
    async def asend(self, message: str, client: httpx.AsyncClient) -> None: ...
```

每个 provider 只负责构造请求参数并调用 httpx，client 由 Notikit 统一管理。

## 配置

### 查找策略

当不指定 config_path 时，按以下顺序查找：

1. `./notikit.toml`（当前目录）
2. `~/.notikit.toml`（用户目录）

支持 `config_path` 手动指定，也支持运行时传入 dict 直接构造。

### 配置格式

```toml
[notikit]
channels = ["lark", "bark"]
timeout = 10

[notikit.bark]
server_url = "https://api.day.app"
device_key = "YOUR_DEVICE_KEY"

[notikit.dingtalk]
webhook_url = "YOUR_WEBHOOK_URL"
sign_secret = "YOUR_SIGN_SECRET"

[notikit.lark]
webhook_url = "YOUR_WEBHOOK_URL"
sign_secret = "YOUR_SIGN_SECRET"

[notikit.telegram]
bot_token = "YOUR_BOT_TOKEN"
chat_id = "YOUR_CHAT_ID"
```

## 异常体系

```python
class NotikitError(Exception): ...       # 基类
class ConfigError(NotikitError): ...     # 配置错误
class ProviderError(NotikitError): ...   # Provider 发送失败
class TimeoutError(NotikitError): ...    # 超时
```

多渠道发送时，失败不中断其他渠道，最后统一报告所有错误。

## 依赖

- httpx（HTTP 客户端，同步 + 异步）
- 无其他第三方依赖
