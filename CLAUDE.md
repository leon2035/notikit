# notikit

轻量级 Python 通知工具包，统一接口发送多渠道通知。

## 项目结构

```
src/notikit/
├── __init__.py          # 公共 API: notify, anotify, Notikit
├── core.py              # Notikit 核心类
├── config.py            # 配置加载（toml 解析、自动发现）
├── exceptions.py        # 异常体系
└── providers/
    ├── __init__.py      # Provider 注册表（装饰器 + 延迟导入）
    ├── base.py          # BaseProvider 抽象基类
    ├── bark.py          # iOS Bark 推送
    ├── telegram.py      # Telegram Bot
    ├── dingtalk.py      # 钉钉机器人
    └── lark.py          # 飞书机器人
```

## API 速查

```python
from notikit import notify, anotify, Notikit

# 函数式（自动读取 ./notikit.toml 或 ~/.notikit.toml）
notify("消息")
await anotify("异步消息")

# 实例化
nk = Notikit()
nk = Notikit(config_path=Path("custom.toml"))
nk = Notikit(config_dict={"channels": ["bark"], "providers": {"bark": {...}}})

# 指定渠道
nk.notify("消息", channels=["lark", "bark"])

# Provider 个性化参数
nk.notify("告警", params={"bark": {"level": "critical", "volume": 5}})
```

## 配置格式

```toml
[notikit]
channels = ["bark", "telegram", "lark"]
timeout = 10

[notikit.bark]
server_url = "https://api.day.app"
device_key = "KEY"

[notikit.telegram]
bot_token = "TOKEN"
chat_id = "CHAT_ID"

[notikit.dingtalk]
webhook_url = "URL"
sign_secret = "SECRET"  # 可选

[notikit.lark]
webhook_url = "URL"
sign_secret = "SECRET"  # 可选
```

## 异常

- `NotikitError` — 基类
- `ConfigError` — 配置错误
- `ProviderError` — 单渠道失败（有 .provider 属性）
- `SendError` — 聚合错误（有 .errors 列表），部分失败不中断其他渠道
- `NotikitTimeoutError` — 超时

## 扩展 Provider

1. 在 `src/notikit/providers/` 下创建新文件
2. 继承 `BaseProvider`，实现 `send` 和 `asend`
3. 用 `@register("name")` 装饰器注册

## 注意事项

- 飞书签名：`hmac.new(key=string_to_sign.encode(), digestmod=sha256)`，key 是 `timestamp\nsecret`，msg 为空
- 钉钉签名：`hmac.new(key=secret, msg=string_to_sign, digestmod=sha256)`
- 发布：`python -m build && python -m twine upload dist/*`
