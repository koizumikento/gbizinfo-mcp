"""Synthetic cases reconciled against the Python implementation; no real HTTP calls."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from gbizinfo_mcp.server import GbizInfoToolset
from gbizinfo_mcp.tool_specs import TOOL_SPECS


class FixtureClient:
    async def get(
        self,
        path: str,
        *,
        query: dict[str, str] | None = None,
        path_params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return {"path": path.format(**(path_params or {})), "query": query or {}}


async def main() -> None:
    toolset = GbizInfoToolset(FixtureClient())  # ty: ignore[invalid-argument-type]
    cases: list[dict[str, Any]] = []
    for spec in TOOL_SPECS:
        args: dict[str, Any] = {"metadata_flg": True}
        if spec.kind == "get":
            args["corporate_number"] = "1234567890123"
        elif spec.kind == "update":
            args.update(from_date="20240229", to_date="20240301", page=2)
        else:
            args.update(name="架空法人", prefecture="東京都, １,大阪", page=2, limit=0)
        result = await getattr(toolset, spec.name)(**args)
        cases.append({"name": spec.name, "args": args, "expected": result})

    extra_search: list[dict[str, Any]] = [
        {"prefecture": "١"},
        {"name": None, "page": None, "metadata_flg": False},
    ]
    for args in extra_search:
        result = await toolset.hojin_search(**args)
        cases.append({"name": "hojin_search", "args": args, "expected": result})

    invalid = [
        ("hojin_get_basic", {"corporate_number": "../../secret"}),
        ("hojin_search", {"corporate_number": "1"}),
        ("hojin_search", {"page": 0}),
        ("hojin_search", {"limit": -1}),
        ("hojin_search", {"limit": 5001}),
        ("hojin_search", {"metadata_flg": "true"}),
        ("hojin_search", {"prefecture": ""}),
        ("hojin_search", {"prefecture": "Tokyo"}),
        ("hojin_search", {"prefecture": "1,,2"}),
        ("hojin_search", {"prefecture": "123"}),
        ("hojin_update_info_basic", {"from_date": "20240230", "to_date": "20240301"}),
        ("hojin_update_info_basic", {"from_date": "00000201", "to_date": "20240301"}),
        ("hojin_update_info_basic", {"from_date": "20240302", "to_date": "20240301"}),
        ("hojin_update_info_basic", {"from_date": "2024-01-01", "to_date": "20240301"}),
    ]
    for name, args in invalid:
        try:
            await getattr(toolset, name)(**args)
        except ValueError:
            cases.append({"name": name, "args": args, "invalid": True})
        else:
            raise AssertionError(f"Fixture must be rejected: {name}, {args}")
    print(json.dumps(cases, ensure_ascii=True))


if __name__ == "__main__":
    asyncio.run(main())
