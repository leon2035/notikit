from notikit.exceptions import (
    ConfigError,
    NotikitError,
    ProviderError,
    SendError,
    NotikitTimeoutError,
)


def test_exception_hierarchy():
    assert issubclass(ConfigError, NotikitError)
    assert issubclass(ProviderError, NotikitError)
    assert issubclass(NotikitTimeoutError, NotikitError)
    assert issubclass(SendError, NotikitError)


def test_provider_error_contains_provider_name():
    err = ProviderError("lark", "发送失败")
    assert err.provider == "lark"
    assert "lark" in str(err)
    assert "发送失败" in str(err)


def test_send_error_aggregates():
    errors = [ProviderError("lark", "fail"), ProviderError("bark", "timeout")]
    err = SendError(errors)
    assert len(err.errors) == 2
    assert "lark" in str(err)
    assert "bark" in str(err)
