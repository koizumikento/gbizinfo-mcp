from __future__ import annotations

import httpx
import pytest
import respx

from gbizinfo_mcp.client import ApiRequestError, GbizInfoClient
from gbizinfo_mcp.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        api_token="secret-token",
        base_url="https://example.com/hojin/",
        timeout_seconds=5,
    )


@pytest.mark.asyncio
@respx.mock
async def test_client_sends_token_header(settings: Settings) -> None:
    route = respx.get("https://example.com/hojin/v2/hojin").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    client = GbizInfoClient(settings)

    payload = await client.get("/v2/hojin", query={"page": "1"})

    assert payload == {"ok": True}
    assert route.called
    request = route.calls.last.request
    assert request.headers["X-hojinInfo-api-token"] == "secret-token"


@pytest.mark.asyncio
@respx.mock
async def test_client_retries_on_429_and_5xx(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def no_sleep(_: float) -> None:
        return None

    monkeypatch.setattr("gbizinfo_mcp.client.asyncio.sleep", no_sleep)

    route = respx.get("https://example.com/hojin/v2/hojin").mock(
        side_effect=[
            httpx.Response(500, json={"message": "server error"}),
            httpx.Response(429, json={"message": "rate limit"}),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    client = GbizInfoClient(settings)

    payload = await client.get("/v2/hojin")

    assert payload == {"ok": True}
    assert route.call_count == 3


@pytest.mark.asyncio
@respx.mock
async def test_client_raises_api_error_on_non_2xx(settings: Settings) -> None:
    respx.get("https://example.com/hojin/v2/hojin").mock(
        return_value=httpx.Response(400, json={"message": "invalid parameter"})
    )
    client = GbizInfoClient(settings)

    with pytest.raises(ApiRequestError, match="invalid parameter"):
        await client.get("/v2/hojin")
