import json
import os
import re
from datetime import date
from typing import Dict, Iterable

import requests
from bs4 import BeautifulSoup

CACHE_FILENAME = "symbol_lookup.json"
SYMBOL_URLS = [
    "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2",
    "https://isin.twse.com.tw/isin/C_public.jsp?strMode=5",
    "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4",
]
FALLBACK_MAPPING: Dict[str, str] = {"2330": "台積電"}


def _cache_path() -> str:
    base = os.path.dirname(__file__)
    return os.path.join(base, CACHE_FILENAME)


def _load_cached_map() -> Dict[str, str]:
    cache_file = _cache_path()
    if not os.path.isfile(cache_file):
        return {}
    try:
        with open(cache_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if payload.get("generated") == date.today().isoformat():
            return payload.get("mapping", {})
    except Exception:  # pragma: no cover
        pass
    return {}


def _save_cache(mapping: Dict[str, str]) -> None:
    cache_file = _cache_path()
    payload = {"generated": date.today().isoformat(), "mapping": mapping}
    with open(cache_file, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def fetch_symbol_mapping(force_refresh: bool = False) -> Dict[str, str]:
    if not force_refresh:
        cached = _load_cached_map()
        if cached:
            return cached

    mapping: Dict[str, str] = {}
    for url in SYMBOL_URLS:
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
            response.raise_for_status()
        except Exception:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        for table in soup.find_all("table", class_="h4"):
            for row in table.find_all("tr"):
                cols = [td.get_text(strip=True) for td in row.find_all("td")]
                if not cols or len(cols) < 2:
                    continue
                raw = cols[0]
                match = re.match(r"(\d{4})\s*(.+)", raw)
                if not match:
                    continue
                code, name = match.group(1), match.group(2).strip()
                mapping.setdefault(code, name)

    if mapping:
        _save_cache(mapping)
    if not mapping:
        return FALLBACK_MAPPING.copy()
    return mapping


def resolve_codes_to_specs(
    codes: Iterable[str], mapping: Dict[str, str]
) -> Dict[str, str]:
    resolved: Dict[str, str] = {}
    for code in codes:
        normalized = code.strip()
        name = mapping.get(normalized)
        if not name:
            raise ValueError(f"找不到股票代碼 {normalized} 的名稱")
        resolved[normalized] = name
    return resolved
