from __future__ import annotations

import datetime as dt
import re
import unicodedata

CORPORATE_NUMBER_RE = re.compile(r"^\d{13}$")
YYYYMMDD_RE = re.compile(r"^\d{8}$")

PREFECTURE_CODE_BY_NAME: dict[str, str] = {
    "北海道": "01",
    "青森県": "02",
    "岩手県": "03",
    "宮城県": "04",
    "秋田県": "05",
    "山形県": "06",
    "福島県": "07",
    "茨城県": "08",
    "栃木県": "09",
    "群馬県": "10",
    "埼玉県": "11",
    "千葉県": "12",
    "東京都": "13",
    "神奈川県": "14",
    "新潟県": "15",
    "富山県": "16",
    "石川県": "17",
    "福井県": "18",
    "山梨県": "19",
    "長野県": "20",
    "岐阜県": "21",
    "静岡県": "22",
    "愛知県": "23",
    "三重県": "24",
    "滋賀県": "25",
    "京都府": "26",
    "大阪府": "27",
    "兵庫県": "28",
    "奈良県": "29",
    "和歌山県": "30",
    "鳥取県": "31",
    "島根県": "32",
    "岡山県": "33",
    "広島県": "34",
    "山口県": "35",
    "徳島県": "36",
    "香川県": "37",
    "愛媛県": "38",
    "高知県": "39",
    "福岡県": "40",
    "佐賀県": "41",
    "長崎県": "42",
    "熊本県": "43",
    "大分県": "44",
    "宮崎県": "45",
    "鹿児島県": "46",
    "沖縄県": "47",
}
PREFECTURE_CODE_BY_ALIAS: dict[str, str] = {
    name[:-1]: code
    for name, code in PREFECTURE_CODE_BY_NAME.items()
    if name.endswith(("都", "府", "県"))
}


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


def normalize_prefecture(prefecture: str | None) -> str | None:
    if prefecture is None:
        return None
    if not isinstance(prefecture, str):
        raise ValueError("prefecture must be a string")

    raw = unicodedata.normalize("NFKC", prefecture).strip()
    if not raw:
        raise ValueError("prefecture must not be empty")

    normalized_parts: list[str] = []
    for part in raw.split(","):
        token = part.strip()
        if not token:
            raise ValueError("prefecture must not contain empty values")
        if token.isdigit():
            if 1 <= len(token) <= 2:
                normalized_parts.append(token.zfill(2))
                continue
            raise ValueError("prefecture code must be 1 or 2 digits")

        code = PREFECTURE_CODE_BY_NAME.get(token) or PREFECTURE_CODE_BY_ALIAS.get(token)
        if code is None:
            raise ValueError(
                "prefecture must be a 1-2 digit code or Japanese prefecture name "
                "(e.g. '13' or '東京都')"
            )
        normalized_parts.append(code)

    return ",".join(normalized_parts)
