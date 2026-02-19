from __future__ import annotations

import pytest

from gbizinfo_mcp.validators import (
    ensure_corporate_number,
    ensure_from_to_range,
    ensure_limit,
    ensure_metadata_flag,
    ensure_page,
    ensure_yyyymmdd,
    normalize_prefecture,
)


def test_corporate_number_validation() -> None:
    assert ensure_corporate_number("1234567890123") == "1234567890123"
    with pytest.raises(ValueError, match="13-digit"):
        ensure_corporate_number("123")


def test_yyyymmdd_validation() -> None:
    assert ensure_yyyymmdd("20240101", field_name="from_date") == "20240101"
    with pytest.raises(ValueError, match="yyyyMMdd"):
        ensure_yyyymmdd("2024-01-01", field_name="from_date")


def test_from_to_range_validation() -> None:
    ensure_from_to_range("20240101", "20240101")
    with pytest.raises(ValueError, match="less than or equal"):
        ensure_from_to_range("20240201", "20240101")


def test_page_and_limit_validation() -> None:
    assert ensure_page(1) == 1
    assert ensure_limit(5000) == 5000
    with pytest.raises(ValueError, match="greater than or equal"):
        ensure_page(0)
    with pytest.raises(ValueError, match="between 0 and 5000"):
        ensure_limit(5001)


def test_metadata_flag_validation() -> None:
    assert ensure_metadata_flag(True) is True
    assert ensure_metadata_flag(False) is False
    assert ensure_metadata_flag(None) is None
    with pytest.raises(ValueError, match="boolean"):
        ensure_metadata_flag("true")  # type: ignore[arg-type]


def test_prefecture_normalization() -> None:
    assert normalize_prefecture(None) is None
    assert normalize_prefecture("13") == "13"
    assert normalize_prefecture("1") == "01"
    assert normalize_prefecture("０１") == "01"
    assert normalize_prefecture("東京都") == "13"
    assert normalize_prefecture("東京") == "13"
    assert normalize_prefecture("東京都,神奈川県") == "13,14"

    with pytest.raises(ValueError, match="1-2 digit code"):
        normalize_prefecture("Tokyo")
