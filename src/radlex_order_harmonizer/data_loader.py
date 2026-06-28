from __future__ import annotations

import csv
from pathlib import Path

import httpx
import pandas as pd

from .models import RADLEX_CSV_URL, RadLexEntry

CACHE_DIR = Path.home() / ".cache" / "radlex-order-harmonizer"
CACHE_FILE = CACHE_DIR / "radlex-playbook-complete.csv"
CACHE_MARKER = CACHE_DIR / ".cache_valid"


def _get_cache_path(url: str = RADLEX_CSV_URL) -> Path:
    return CACHE_DIR / f"radlex-playbook-{hash(url)}.csv"


def download_radlex_csv(
    url: str = RADLEX_CSV_URL,
    cache_dir: Path | None = None,
    force_refresh: bool = False,
    timeout: float = 60.0,
) -> Path:
    cache_dir = cache_dir or CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "radlex-playbook-complete.csv"

    if cache_path.exists() and not force_refresh:
        return cache_path

    print(f"Downloading RadLex Playbook from {url}...")
    response = httpx.get(url, follow_redirects=True, timeout=timeout)
    response.raise_for_status()

    cache_path.write_bytes(response.content)
    print(f"Cached to {cache_path}")
    return cache_path


def parse_radlex_csv(path: Path) -> list[RadLexEntry]:
    entries: list[RadLexEntry] = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = RadLexEntry(
                rpid=row.get("RPID", "").strip(),
                letter_code=row.get("LETTER_CODE", "").strip(),
                short_name=row.get("SHORT_NAME", "").strip(),
                long_name=row.get("LONG_NAME", "").strip(),
                modality=row.get("MODALITY", "").strip(),
                playbook_type=row.get("PLAYBOOK_TYPE", "").strip(),
                population=row.get("POPULATION", "").strip(),
                body_region=row.get("BODY_REGION", "").strip(),
                body_region_2=row.get("BODY_REGION_2", "").strip(),
                body_region_3=row.get("BODY_REGION_3", "").strip(),
                modality_modifier=row.get("MODALITY_MODIFIER", "").strip(),
                modality_modifier_2=row.get("MODALITY_MODIFIER_2", "").strip(),
                procedure_modifier=row.get("PROCEDURE_MODIFIER", "").strip(),
                procedure_modifier_2=row.get("PROCEDURE_MODIFIER_2", "").strip(),
                anatomic_focus=row.get("ANATOMIC_FOCUS", "").strip(),
                anatomic_focus_2=row.get("ANATOMIC_FOCUS_2", "").strip(),
                laterality=row.get("LATERALITY", "").strip(),
                reason_for_exam=row.get("REASON_FOR_EXAM", "").strip(),
                technique=row.get("TECHNIQUE", "").strip(),
                pharmaceutical=row.get("PHARMACEUTICAL", "").strip(),
                pharmaceutical_2=row.get("PHARMACEUTICAL_2", "").strip(),
                view=row.get("VIEW", "").strip(),
                view_2=row.get("VIEW_2", "").strip(),
                view_3=row.get("VIEW_3", "").strip(),
                view_4=row.get("VIEW_4", "").strip(),
                rids=row.get("RIDS", "").strip(),
            )
            entries.append(entry)
    return entries


def load_radlex(
    url: str = RADLEX_CSV_URL,
    cache_dir: Path | None = None,
    force_refresh: bool = False,
) -> list[RadLexEntry]:
    cache_path = download_radlex_csv(url, cache_dir, force_refresh)
    return parse_radlex_csv(cache_path)


def radlex_to_dataframe(entries: list[RadLexEntry]) -> pd.DataFrame:
    rows = []
    for e in entries:
        rows.append(
            {
                "rpid": e.rpid,
                "letter_code": e.letter_code,
                "short_name": e.short_name,
                "long_name": e.long_name,
                "modality": e.modality,
                "body_region": e.body_region,
                "pharmaceutical": e.pharmaceutical,
            }
        )
    return pd.DataFrame(rows)
