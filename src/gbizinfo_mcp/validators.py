from __future__ import annotations

import datetime as dt
import re

CORPORATE_NUMBER_RE = re.compile(r"^\d{13}$")
YYYYMMDD_RE = re.compile(r"^\d{8}$")


def ensure_corporate_number(value: str) -> str:
    if not isinstance(value, str) or not CORPORATE_NUMBER_RE.fullmatch(value):
        raise ValueError("corporate_number must be a 13-digit string")
    return value


def ensure_yyyymmdd(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not YYYYMMDD_RE.fullmatch(value):
        raise ValueError(f"{field_name} must be in yyyyMMdd format")
    try:
        dt.datetime.strptime(value, "%Y%m%d")
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid date in yyyyMMdd format") from exc
    return value


def ensure_from_to_range(from_date: str, to_date: str) -> None:
    parsed_from = dt.datetime.strptime(from_date, "%Y%m%d")
    parsed_to = dt.datetime.strptime(to_date, "%Y%m%d")
    if parsed_from > parsed_to:
        raise ValueError("from_date must be less than or equal to to_date")


def ensure_page(page: int | None) -> int | None:
    if page is None:
        return None
    if not isinstance(page, int):
        raise ValueError("page must be an integer")
    if page < 1:
        raise ValueError("page must be greater than or equal to 1")
    return page


def ensure_limit(limit: int | None) -> int | None:
    if limit is None:
        return None
    if not isinstance(limit, int):
        raise ValueError("limit must be an integer")
    if not 0 <= limit <= 5000:
        raise ValueError("limit must be between 0 and 5000")
    return limit


def ensure_metadata_flag(metadata_flg: bool | None) -> bool | None:
    if metadata_flg is None:
        return None
    if not isinstance(metadata_flg, bool):
        raise ValueError("metadata_flg must be a boolean")
    return metadata_flg
