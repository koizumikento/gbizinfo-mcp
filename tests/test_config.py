from __future__ import annotations

import pytest

from gbizinfo_mcp.config import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT_SECONDS,
    Settings,
    load_settings_from_env,
)


def test_load_settings_requires_token() -> None:
    with pytest.raises(ValueError, match="GBIZINFO_API_TOKEN is required"):
        load_settings_from_env({})


def test_load_settings_uses_defaults() -> None:
    settings = load_settings_from_env({"GBIZINFO_API_TOKEN": "token"})
    assert settings.api_token == "token"
    assert settings.base_url == DEFAULT_BASE_URL
    assert settings.timeout_seconds == DEFAULT_TIMEOUT_SECONDS


def test_base_url_trailing_slash_is_removed() -> None:
    settings = Settings(
        api_token="token",
        base_url="https://example.com/hojin/",
        timeout_seconds=20,
    )
    assert settings.base_url == "https://example.com/hojin"
