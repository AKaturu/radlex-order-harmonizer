from __future__ import annotations

import re

from .models import (
    KNOWN_MODALITIES,
    LATERALITY_TERMS,
    NormalizedProcedure,
)

ABBREVIATIONS: dict[str, str] = {
    r"\bw/wo": "with and without",
    r"\bw/o": "without",
    r"\bwo\b": "without",
    r"\bw/": "with",
    r"\bw\s+iv\b": "with iv contrast",
    r"\bwo\s+iv\b": "without iv contrast",
    r"\bw/o\s+iv\b": "without iv contrast",
    r"\biv\s+contrast\b": "",
    r"\biv\b": "intravenous",
    r"\bthr\b": "through",
    r"\bvs\b": "versus",
    r"\bdx\b": "diagnostic",
    r"\brx\b": "treatment",
    r"\bhx\b": "history",
    r"\bpt\b(?!\s*ct)": "patient",
    r"\bw\b(?!\s*(?:iv|o|/|contrast))": "with",
    r"\b(?:nuc\s*med)\b": "nuclear medicine",
    r"\babd\b": "abdomen",
    r"\bext\b(?!\s*rem)": "extremity",
    r"\bue\b": "upper extremity",
    r"\ble\b": "lower extremity",
    r"\bc-spine\b": "cervical spine",
    r"\bt-spine\b": "thoracic spine",
    r"\bl-spine\b": "lumbar spine",
    r"\btl-spine\b": "thoracolumbar spine",
    r"\bpelv\b": "pelvis",
    r"\bmaxfax\b": "maxillofacial",
    r"\btmj\b": "temporomandibular joint",
    r"\bangio\b": "angiography",
    r"\bmra\b": "mr angiography",
    r"\bcta\b": "ct angiography",
    r"\bfluoro\b": "fluoroscopy",
    r"\bmammo\b": "mammography",
    r"\bsono\b": "ultrasound",
    r"\bdexa?\b": "dxa",
    r"\bproc\b": "procedure",
    r"\brecon\b": "reconstruction",
    r"\bscreen\b": "screening",
    r"\barthro\b": "arthrography",
    r"\bcholangio\b": "cholangiography",
    r"\bcolonography\b": "colonography",
    r"\bpyelo\b": "pyelography",
    r"\bcisterno\b": "cisternography",
    r"\bdefeco\b": "defecography",
    r"\bdisco\b": "discography",
    r"\benteroclysis\b": "enteroclysis",
    r"\benterography\b": "enterography",
    r"\bfistulo\b": "fistulography",
    r"\bgalacto\b": "galactography",
    r"\bhystero\b": "hysterosalpingography",
    r"\blaryngo\b": "laryngography",
    r"\bmyelo\b": "myelography",
    r"\bnephrosto\b": "nephrostography",
    r"\bpharyngo\b": "pharyngography",
    r"\bpouchography\b": "pouchography",
    r"\bsialo\b": "sialography",
    r"\burethro\b": "urethrography",
    r"\burography\b": "urography",
    r"\bveno\b": "venography",
    r"\b(?:&|and)\b": "and",
}


def normalize_name(name: str) -> str:
    normalized = name.lower().strip()
    for pattern, replacement in ABBREVIATIONS.items():
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def tokenize(name: str) -> list[str]:
    return normalize_name(name).split()


def extract_modality(name: str) -> str | None:
    upper = name.upper()
    tokens = upper.split()
    for t in tokens:
        t_clean = t.strip(".,;:()")
        if t_clean in KNOWN_MODALITIES:
            return t_clean
    return None


KNOWN_BODY_REGIONS: set[str] = {
    "ABDOMEN", "PELVIS", "CHEST", "HEAD", "NECK", "SPINE",
    "CERVICAL SPINE", "THORACIC SPINE", "LUMBAR SPINE",
    "THORACOLUMBAR SPINE", "LUMBOSACRAL SPINE",
    "UPPER EXTREMITY", "LOWER EXTREMITY", "EXTREMITY",
    "BREAST", "FACE", "SKULL", "BODY", "BONE", "WHOLEBODY",
    "EXTREMITIES",
}


def extract_body_parts(name: str) -> list[str]:
    found: list[str] = []
    upper = name.upper()
    for region in KNOWN_BODY_REGIONS:
        if region in upper:
            found.append(region)
    return found


def extract_contrast_status(normalized: str) -> str | None:
    if re.search(r"\bwithout\b", normalized):
        if re.search(r"\bwith\b", normalized):
            return "without then with"
        return "without"
    if re.search(r"\bwith\b", normalized):
        return "with"
    return None


def extract_laterality(name: str) -> str | None:
    upper = name.upper()
    for term, label in LATERALITY_TERMS.items():
        if term.upper() in upper:
            return label
    return None


def normalize_procedure(name: str) -> NormalizedProcedure:
    normalized = normalize_name(name)
    tokens = tokenize(name)
    modality = extract_modality(name)
    body_parts = extract_body_parts(name)
    contrast = extract_contrast_status(normalized)
    laterality = extract_laterality(name)
    return NormalizedProcedure(
        original=name,
        normalized=normalized,
        tokens=tokens,
        modality=modality,
        body_parts=body_parts,
        contrast_status=contrast,
        laterality=laterality,
        anatomic_focus=None,
    )
