from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ToolKind = Literal["search", "update", "get"]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    path: str
    kind: ToolKind


TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec("hojin_search", "/v2/hojin", "search"),
    ToolSpec("hojin_update_info_basic", "/v2/hojin/updateInfo", "update"),
    ToolSpec("hojin_update_info_certification", "/v2/hojin/updateInfo/certification", "update"),
    ToolSpec("hojin_update_info_commendation", "/v2/hojin/updateInfo/commendation", "update"),
    ToolSpec("hojin_update_info_corporation", "/v2/hojin/updateInfo/corporation", "update"),
    ToolSpec("hojin_update_info_finance", "/v2/hojin/updateInfo/finance", "update"),
    ToolSpec("hojin_update_info_patent", "/v2/hojin/updateInfo/patent", "update"),
    ToolSpec("hojin_update_info_procurement", "/v2/hojin/updateInfo/procurement", "update"),
    ToolSpec("hojin_update_info_subsidy", "/v2/hojin/updateInfo/subsidy", "update"),
    ToolSpec("hojin_update_info_workplace", "/v2/hojin/updateInfo/workplace", "update"),
    ToolSpec("hojin_get_basic", "/v2/hojin/{corporate_number}", "get"),
    ToolSpec("hojin_get_certification", "/v2/hojin/{corporate_number}/certification", "get"),
    ToolSpec("hojin_get_commendation", "/v2/hojin/{corporate_number}/commendation", "get"),
    ToolSpec("hojin_get_corporation", "/v2/hojin/{corporate_number}/corporation", "get"),
    ToolSpec("hojin_get_finance", "/v2/hojin/{corporate_number}/finance", "get"),
    ToolSpec("hojin_get_patent", "/v2/hojin/{corporate_number}/patent", "get"),
    ToolSpec("hojin_get_procurement", "/v2/hojin/{corporate_number}/procurement", "get"),
    ToolSpec("hojin_get_subsidy", "/v2/hojin/{corporate_number}/subsidy", "get"),
    ToolSpec("hojin_get_workplace", "/v2/hojin/{corporate_number}/workplace", "get"),
)
