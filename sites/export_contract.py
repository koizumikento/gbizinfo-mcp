"""Export the existing Python discovery contract, without loading real credentials."""

from __future__ import annotations

import asyncio
import json
import sys
from importlib.metadata import version
from pathlib import Path

from gbizinfo_mcp.client import MAX_RETRIES, RETRYABLE_STATUS_CODES
from gbizinfo_mcp.config import DEFAULT_BASE_URL, DEFAULT_TIMEOUT_SECONDS, Settings
from gbizinfo_mcp.server import create_server
from gbizinfo_mcp.tool_specs import TOOL_SPECS
from gbizinfo_mcp.validators import PREFECTURE_CODE_BY_ALIAS, PREFECTURE_CODE_BY_NAME


async def main() -> None:
    server = create_server(Settings(api_token="build-fixture"))
    tools = await server.list_tools()
    assert {tool.name for tool in tools} == {spec.name for spec in TOOL_SPECS}
    contract = {
        "version": version("gbizinfo-mcp"),
        "tools": [tool.model_dump(by_alias=True, exclude_none=True) for tool in tools],
        "routes": {spec.name: {"path": spec.path, "kind": spec.kind} for spec in TOOL_SPECS},
        "prefectures": PREFECTURE_CODE_BY_NAME | PREFECTURE_CODE_BY_ALIAS,
        "baseUrl": DEFAULT_BASE_URL,
        "timeoutSeconds": DEFAULT_TIMEOUT_SECONDS,
        "maxRetries": MAX_RETRIES,
        "retryableStatuses": sorted(RETRYABLE_STATUS_CODES),
    }
    target = Path(__file__).parent / "worker" / "contract.json"
    serialized = json.dumps(contract, ensure_ascii=False, separators=(",", ":")) + "\n"
    if "--check" in sys.argv:
        assert target.read_text(encoding="utf-8") == serialized, (
            "Regenerate sites/worker/contract.json"
        )
    else:
        target.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
