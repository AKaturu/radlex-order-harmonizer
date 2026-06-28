from __future__ import annotations

import random

import pandas as pd

from .models import RadLexEntry

_MODALITY_SHORT: dict[str, list[str]] = {
    "CT": ["CT", "Cat Scan"],
    "MR": ["MR", "MRI", "Magnetic Resonance"],
    "XR": ["XR", "X-Ray", "Radiograph"],
    "US": ["US", "Ultrasound", "Sonogram"],
    "NM": ["NM", "Nuclear Medicine", "Nuclear Scan"],
    "MAMMOGRAPHY": ["Mammogram", "Mammography"],
    "XA": ["XA", "Angiogram"],
}

_CONTRAST_VARIANTS = [
    ("without", "wo", "without"),
    ("with", "w/", "with"),
    ("with and without", "w/wo", "with and without"),
    ("without", "", ""),
    ("with", "", ""),
]

_LATERALITY = ["left", "right", "bilateral", ""]

_MODIFIERS = ["", "limited", "high resolution", "low dose", "screening", "diagnostic"]


def generate_synthetic_names(
    entries: list[RadLexEntry],
    n: int = 100,
    seed: int = 42,
    noise_rate: float = 0.2,
) -> list[dict]:
    rng = random.Random(seed)
    valid_entries = [
        e for e in entries
        if e.playbook_type == "RADIOLOGY ORDERABLE"
        and (e.short_name or e.long_name)
    ]
    if not valid_entries:
        valid_entries = [e for e in entries if e.short_name or e.long_name]
    if not valid_entries:
        return []

    names: list[dict] = []

    for _ in range(n):
        entry = rng.choice(valid_entries)
        has_short = bool(entry.short_name)
        has_long = bool(entry.long_name)

        weights = []
        variants = []
        if has_short:
            weights.append(3)
            variants.append("short_name")
            weights.append(2)
            variants.append("abbreviated")
        if has_long:
            weights.append(3)
            variants.append("long_name")
            weights.append(1)
            variants.append("reordered")

        if not variants:
            continue

        variant_type = rng.choices(variants, weights=weights, k=1)[0]

        if variant_type == "short_name":
            local_name = entry.short_name
        elif variant_type == "long_name":
            local_name = entry.long_name
        elif variant_type == "abbreviated":
            local_name = _make_abbreviation(entry.short_name, rng)
        else:
            local_name = _reorder_name(entry.long_name, rng)

        if noise_rate > 0 and rng.random() < noise_rate:
            local_name = _add_noise(local_name, rng)

        names.append(
            {
                "local_name": local_name,
                "true_rpid": entry.rpid,
                "true_short_name": entry.short_name,
                "true_modality": entry.modality,
                "true_body_region": entry.body_region,
            }
        )

    return names


def _make_abbreviation(name: str, rng: random.Random) -> str:
    replacements = {
        "with": rng.choice(["w/", "w"]),
        "without": rng.choice(["wo", "w/o"]),
        "and": "&",
        "abdomen": "Abd",
        " Abdomen": " Abd",
        " Chest": " Cht",
        "pelvis": "Pelv",
        "extremity": "Ext",
        "cervical": "C",
        "thoracic": "T",
        "lumbar": "L",
        "spine": "Sp",
    }
    result = name
    for full, abbr in replacements.items():
        result = result.replace(full, abbr)
    return result


def _reorder_name(name: str, rng: random.Random) -> str:
    parts = name.split()
    if len(parts) <= 3:
        return name
    idx = rng.randint(1, len(parts) - 2)
    parts[idx], parts[idx + 1] = parts[idx + 1], parts[idx]
    return " ".join(parts)


def _add_noise(name: str, rng: random.Random) -> str:
    if not name.strip():
        return name
    noise_type = rng.choice(["typo", "extra_word", "missing_word"])
    if noise_type == "typo":
        chars = list(name)
        if chars:
            i = rng.randint(0, len(chars) - 1)
            chars[i] = rng.choice("abcdefghijklmnopqrstuvwxyz")
        return "".join(chars)
    elif noise_type == "extra_word":
        extras = ["STAT", "URGENT", "ROUTINE", "OUTPATIENT", "INPATIENT"]
        return name + " " + rng.choice(extras)
    else:
        words = name.split()
        if len(words) > 2:
            del words[rng.randint(0, len(words) - 1)]
        return " ".join(words) if words else name


def write_synthetic_csv(
    entries: list[RadLexEntry],
    output_path: str,
    n: int = 100,
    seed: int = 42,
    noise_rate: float = 0.2,
) -> pd.DataFrame:
    names = generate_synthetic_names(entries, n, seed, noise_rate)
    df = pd.DataFrame(names)
    df.to_csv(output_path, index=False)
    return df
