from __future__ import annotations

import os
from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

DEFAULT_BASE_URL = "https://api.info.gbiz.go.jp/hojin"
DEFAULT_TIMEOUT_SECONDS = 20.0


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    api_token: str = Field(min_length=1)
    base_url: str = Field(default=DEFAULT_BASE_URL, min_length=1)
    timeout_seconds: float = Field(default=DEFAULT_TIMEOUT_SECONDS, gt=0)

    @field_validator("base_url")
    @classmethod
    def normalize_base_url(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("GBIZINFO_BASE_URL must not be empty")
        return trimmed.rstrip("/")


def load_settings_from_env(environ: Mapping[str, str] | None = None) -> Settings:
    env = environ or os.environ
    token = env.get("GBIZINFO_API_TOKEN")
    if not token:
        raise ValueError("GBIZINFO_API_TOKEN is required")

    payload = {
        "api_token": token,
        "base_url": env.get("GBIZINFO_BASE_URL", DEFAULT_BASE_URL),
        "timeout_seconds": env.get("GBIZINFO_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)),
    }
    try:
        return Settings.model_validate(payload)
    except ValidationError as exc:  # pragma: no cover - pydantic owns error details
        raise ValueError(f"Invalid environment configuration: {exc}") from exc
