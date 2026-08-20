from __future__ import annotations

from typing import Any

import pytest

from gbizinfo_mcp.client import ApiRequestError
from gbizinfo_mcp.config import Settings
from gbizinfo_mcp.server import GbizInfoToolset, create_server
from gbizinfo_mcp.tool_specs import TOOL_SPECS


class FakeClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def get(
        self,
        path: str,
        *,
        query: dict[str, str] | None = None,
        path_params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        call = {"path": path, "query": query or {}, "path_params": path_params or {}}
        self.calls.append(call)
        return call


@pytest.mark.asyncio
async def test_all_tool_specs_are_callable_and_use_expected_paths() -> None:
    client = FakeClient()
    toolset = GbizInfoToolset(client=client)  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]

    for spec in TOOL_SPECS:
        method = getattr(toolset, spec.name)
        if spec.kind == "search":
            result = await method(name="Test Corporation", page=1, limit=10, metadata_flg=True)
            assert result["query"]["metadata_flg"] == "true"
        elif spec.kind == "update":
            result = await method(
                from_date="20240101",
                to_date="20240131",
                page=1,
                metadata_flg=False,
            )
            assert result["query"]["from"] == "20240101"
            assert result["query"]["to"] == "20240131"
            assert "from_date" not in result["query"]
            assert "to_date" not in result["query"]
        else:
            result = await method(corporate_number="1234567890123", metadata_flg=True)
            assert result["path_params"]["corporate_number"] == "1234567890123"

        assert result["path"] == spec.path


@pytest.mark.asyncio
async def test_toolset_validates_metadata_type() -> None:
    client = FakeClient()
    toolset = GbizInfoToolset(client=client)  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]

    with pytest.raises(ValueError, match="boolean"):
        await toolset.hojin_get_basic(
            corporate_number="1234567890123",
            metadata_flg="true",  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]
        )


class ErrorClient:
    async def get(
        self,
        path: str,
        *,
        query: dict[str, str] | None = None,
        path_params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        raise ApiRequestError(400, "bad request", '{"message":"bad request"}')


@pytest.mark.asyncio
async def test_toolset_wraps_api_errors_as_value_errors() -> None:
    toolset = GbizInfoToolset(client=ErrorClient())  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]

    with pytest.raises(ValueError, match="gBizINFO API request failed"):
        await toolset.hojin_get_basic(corporate_number="1234567890123")


@pytest.mark.asyncio
async def test_hojin_search_normalizes_prefecture_name_to_code() -> None:
    client = FakeClient()
    toolset = GbizInfoToolset(client=client)  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]

    result = await toolset.hojin_search(name="Test Corporation", prefecture="東京都")

    assert result["query"]["prefecture"] == "13"


@pytest.mark.asyncio
async def test_hojin_search_rejects_invalid_prefecture() -> None:
    client = FakeClient()
    toolset = GbizInfoToolset(client=client)  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]

    with pytest.raises(ValueError, match="prefecture must be a 1-2 digit code"):
        await toolset.hojin_search(name="Test Corporation", prefecture="Tokyo")
    assert client.calls == []


def test_create_server_requires_token_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GBIZINFO_API_TOKEN", raising=False)
    with pytest.raises(ValueError, match="GBIZINFO_API_TOKEN is required"):
        create_server(settings=None)


def test_create_server_accepts_explicit_settings() -> None:
    settings = Settings(api_token="token", base_url="https://example.com/hojin", timeout_seconds=20)
    server = create_server(settings=settings)
    assert server is not None


@pytest.mark.asyncio
async def test_create_server_registers_19_tools() -> None:
    settings = Settings(api_token="token", base_url="https://example.com/hojin", timeout_seconds=20)
    server = create_server(settings=settings)
    tools = await server.list_tools()
    assert len(tools) == 19


@pytest.mark.asyncio
async def test_create_server_exposes_tool_descriptions_and_readonly_annotations() -> None:
    settings = Settings(api_token="token", base_url="https://example.com/hojin", timeout_seconds=20)
    server = create_server(settings=settings)
    tools = await server.list_tools()

    assert all(tool.description for tool in tools)
    assert all(tool.annotations is not None for tool in tools)
    assert all(
        tool.annotations.read_only_hint is True for tool in tools if tool.annotations is not None
    )


@pytest.mark.asyncio
async def test_create_server_exposes_key_parameter_descriptions() -> None:
    settings = Settings(api_token="token", base_url="https://example.com/hojin", timeout_seconds=20)
    server = create_server(settings=settings)
    tools = await server.list_tools()

    search = next(tool for tool in tools if tool.name == "hojin_search")
    search_props = search.input_schema["properties"]
    assert search_props["prefecture"]["description"]
    assert search_props["city"]["description"]
    assert search_props["metadata_flg"]["description"]

    get_basic = next(tool for tool in tools if tool.name == "hojin_get_basic")
    get_props = get_basic.input_schema["properties"]
    assert get_props["corporate_number"]["description"]
