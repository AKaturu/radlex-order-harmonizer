from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class MatchStrategy(StrEnum):
    EXACT = "exact"
    TOKEN = "token"
    FUZZY = "fuzzy"


class AdjudicationStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass
class RadLexEntry:
    rpid: str
    letter_code: str
    short_name: str
    long_name: str
    modality: str
    playbook_type: str
    population: str
    body_region: str
    body_region_2: str
    body_region_3: str
    modality_modifier: str
    modality_modifier_2: str
    procedure_modifier: str
    procedure_modifier_2: str
    anatomic_focus: str
    anatomic_focus_2: str
    laterality: str
    reason_for_exam: str
    technique: str
    pharmaceutical: str
    pharmaceutical_2: str
    view: str
    view_2: str
    view_3: str
    view_4: str
    rids: str

    @property
    def all_names(self) -> list[str]:
        return [n for n in [self.short_name, self.long_name] if n and n.strip()]

    @property
    def body_regions(self) -> list[str]:
        return [
            r
            for r in [
                self.body_region,
                self.body_region_2,
                self.body_region_3,
            ]
            if r and r.strip() and r.strip() != " "
        ]


@dataclass
class CandidateMatch:
    entry: RadLexEntry
    score: float
    strategy: MatchStrategy


@dataclass
class NormalizedProcedure:
    original: str
    normalized: str
    tokens: list[str]
    modality: str | None
    body_parts: list[str]
    contrast_status: str | None
    laterality: str | None
    anatomic_focus: str | None


@dataclass
class MatchResult:
    local_name: str
    normalized: NormalizedProcedure
    candidates: list[CandidateMatch] = field(default_factory=list)
    selected: RadLexEntry | None = None
    adjudication: AdjudicationStatus = AdjudicationStatus.PENDING
    selected_rpid: str | None = None
    selected_score: float | None = None
    selected_strategy: str | None = None
    audit_notes: str | None = None

    @property
    def best_candidate(self) -> CandidateMatch | None:
        return self.candidates[0] if self.candidates else None

    @property
    def is_mapped(self) -> bool:
        return self.adjudication == AdjudicationStatus.ACCEPTED and self.selected is not None


@dataclass
class HarmonizationReport:
    results: list[MatchResult]
    total: int
    mapped: int
    unmapped: int
    pending: int

    @property
    def coverage(self) -> float:
        return self.mapped / self.total if self.total > 0 else 0.0


RADLEX_CSV_URL = "https://api3.rsna.org/radlex/v1/createCsv?csvType=new"

KNOWN_MODALITIES: set[str] = {
    "CT", "MR", "XR", "US", "NM", "PT", "XA", "MAMMOGRAPHY",
    "RADIO-FLUOROSCOPY", "RADIOLOGY PROCEDURE", "OT",
    "NM&CT", "PT&CT", "US&FL", "US&RF", "XR&RF", "CR",
    "RF", "MAMMO", "DXA", "PET",
}

CONTRAST_PATTERNS: dict[str, list[str]] = {
    "without then with": ["w/wo", "w and wo", "with and without", "w /wo", "w/ wo"],
    "with": ["w/", "with", "w iv", "iv contrast"],
    "without": ["wo", "without", "w/o", "w/o iv", "wo iv", "without iv"],
}

LATERALITY_TERMS: dict[str, str] = {
    "left": "left",
    "right": "right",
    "bilateral": "bilateral",
    "bilat": "bilateral",
}
