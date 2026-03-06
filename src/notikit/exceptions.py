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


class NotikitTimeoutError(NotikitError):
    """请求超时"""


class SendError(NotikitError):
    """聚合多个 provider 的发送错误"""

    def __init__(self, errors: list[ProviderError]):
        self.errors = errors
        names = ", ".join(e.provider for e in errors)
        super().__init__(f"发送失败: {names}")
