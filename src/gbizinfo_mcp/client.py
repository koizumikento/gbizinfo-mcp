from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx

from .config import Settings

MAX_RETRIES = 2
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class ApiRequestError(RuntimeError):
    def __init__(self, status_code: int, message: str, response_body: str | None = None) -> None:
        self.status_code = status_code
        self.message = message
        self.response_body = response_body
        details = f"gBizINFO API request failed ({status_code}): {message}"
        if response_body:
            details = f"{details} | body={response_body[:500]}"
        super().__init__(details)

    @classmethod
    def from_response(cls, response: httpx.Response) -> ApiRequestError:
        message = response.reason_phrase
        body_excerpt: str | None = None
        try:
            payload = response.json()
            body_excerpt = json.dumps(payload, ensure_ascii=False)
            if isinstance(payload, dict) and isinstance(payload.get("message"), str):
                message = payload["message"]
        except ValueError:
            body_excerpt = response.text[:500] if response.text else None
        return cls(status_code=response.status_code, message=message, response_body=body_excerpt)


class GbizInfoClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get(
        self,
        path: str,
        *,
        query: dict[str, str] | None = None,
        path_params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        target_path = path.format(**(path_params or {})).lstrip("/")
        headers = {"X-hojinInfo-api-token": self._settings.api_token}

        async with httpx.AsyncClient(
            base_url=self._settings.base_url,
            timeout=self._settings.timeout_seconds,
        ) as http:
            attempt = 0
            while True:
                response = await http.get(target_path, params=query, headers=headers)
                if (
                    response.status_code in RETRYABLE_STATUS_CODES
                    and attempt < MAX_RETRIES
                ):
                    await asyncio.sleep(0.25 * (2**attempt))
                    attempt += 1
                    continue
                break

        if response.is_error:
            raise ApiRequestError.from_response(response)

        try:
            payload = response.json()
        except ValueError as exc:
            raise ApiRequestError(
                status_code=response.status_code,
                message="Response body is not valid JSON",
                response_body=response.text[:500] if response.text else None,
            ) from exc

        if not isinstance(payload, dict):
            raise ApiRequestError(
                status_code=response.status_code,
                message="Response JSON root must be an object",
                response_body=json.dumps(payload, ensure_ascii=False)[:500],
            )
        return payload
