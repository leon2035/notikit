# notikit

轻量级 Python 通知工具包，提供统一接口向多个通知渠道发送消息。

适用于脚本、自动化任务、CI/CD、监控告警等场景。

## 特性

- 统一 API，一行代码发送通知
- 支持同步和异步调用
- 多渠道支持：Bark / Telegram / 钉钉 / 飞书
- 支持 Provider 个性化参数
- 部分渠道失败不影响其他渠道
- 仅依赖 httpx，无其他第三方依赖
- Python 3.10+

## 安装

```bash
pip install notikit
```

## 快速开始

### 1. 创建配置文件

在项目目录下创建 `notikit.toml`（或在用户目录下创建 `~/.notikit.toml` 作为全局配置）：

```toml
[notikit]
channels = ["bark", "telegram", "lark"]
timeout = 10  # 可选，默认 10 秒

[notikit.bark]
server_url = "https://api.day.app"
device_key = "YOUR_DEVICE_KEY"

[notikit.telegram]
bot_token = "YOUR_BOT_TOKEN"
chat_id = "YOUR_CHAT_ID"

[notikit.dingtalk]
webhook_url = "YOUR_WEBHOOK_URL"
sign_secret = "YOUR_SIGN_SECRET"  # 可选，使用关键词或 IP 白名单时无需配置

[notikit.lark]
webhook_url = "YOUR_WEBHOOK_URL"
sign_secret = "YOUR_SIGN_SECRET"  # 可选
```

### 2. 发送通知

```python
from notikit import notify

notify("部署完成，服务已上线")
```

就这么简单。

## 使用方式

### 函数式调用

```python
from notikit import notify, anotify

# 同步发送到所有配置的渠道
notify("构建成功: v1.2.0")

# 异步发送
await anotify("异步消息")
```

### 实例化调用

```python
from notikit import Notikit

nk = Notikit()

# 发送到所有配置的渠道
nk.notify("构建成功")

# 只发送到指定渠道
nk.notify("紧急告警", channels=["lark", "bark"])
```

### 指定配置文件

```python
from pathlib import Path
from notikit import Notikit

nk = Notikit(config_path=Path("/path/to/notikit.toml"))
nk.notify("来自自定义配置的消息")
```

### 字典配置（无需配置文件）

```python
from notikit import Notikit

nk = Notikit(config_dict={
    "channels": ["bark"],
    "timeout": 5,
    "providers": {
        "bark": {
            "server_url": "https://api.day.app",
            "device_key": "YOUR_DEVICE_KEY",
        },
    },
})
nk.notify("通过字典配置发送的消息")
```

### Provider 个性化参数

通过 `params` 传递各渠道专属参数：

```python
from notikit import notify

# Bark: 设置推送级别和音量
notify("重要警告", params={"bark": {"level": "critical", "volume": 5}})

# Telegram: 使用 HTML 格式
notify("<b>构建成功</b>", params={"telegram": {"parse_mode": "HTML"}})

# 多渠道各自设置不同参数
notify("服务器告警", params={
    "bark": {"level": "timeSensitive", "sound": "alarm"},
    "telegram": {"disable_notification": False},
})
```

### 异步调用

```python
import asyncio
from notikit import Notikit, anotify

async def main():
    # 函数式
    await anotify("异步消息")

    # 实例化
    nk = Notikit()
    await nk.anotify("异步消息", channels=["lark"])

asyncio.run(main())
```

### 错误处理

```python
from notikit import Notikit, SendError

nk = Notikit()
try:
    nk.notify("测试消息")
except SendError as e:
    print(f"发送失败，共 {len(e.errors)} 个渠道出错:")
    for err in e.errors:
        print(f"  - [{err.provider}] {err}")
```

多渠道发送时，单个渠道失败不会中断其他渠道，所有错误最后通过 `SendError` 统一抛出。

## 配置查找顺序

未指定 `config_path` 时，自动按以下顺序查找：

1. `./notikit.toml` — 当前目录（项目级配置）
2. `~/.notikit.toml` — 用户目录（全局默认配置）

## 支持的渠道

| 渠道 | 说明 | 个性化参数示例 |
|------|------|---------------|
| bark | iOS Bark 推送 | `level`, `volume`, `sound`, `icon`, `group`, `url` |
| telegram | Telegram Bot | `parse_mode`, `disable_notification` |
| dingtalk | 钉钉机器人 | — |
| lark | 飞书机器人 | — |

## 异常类型

| 异常 | 说明 |
|------|------|
| `NotikitError` | 基类 |
| `ConfigError` | 配置文件不存在或格式错误 |
| `ProviderError` | 单个渠道发送失败 |
| `SendError` | 聚合多个渠道的发送错误 |
| `NotikitTimeoutError` | 请求超时 |

## 开发

```bash
git clone https://github.com/leon2035/notikit.git
cd notikit
pip install -e ".[dev]"
pytest -v
```

## License

MIT
