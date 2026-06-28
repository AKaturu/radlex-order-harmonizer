from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from .models import AdjudicationStatus, HarmonizationReport, MatchResult


def results_to_dataframe(results: list[MatchResult]) -> pd.DataFrame:
    rows = []
    for r in results:
        rows.append(
            {
                "local_name": r.local_name,
                "normalized": r.normalized.normalized,
                "detected_modality": r.normalized.modality or "",
                "detected_body_parts": "; ".join(r.normalized.body_parts),
                "detected_contrast": r.normalized.contrast_status or "",
                "detected_laterality": r.normalized.laterality or "",
                "selected_rpid": r.selected_rpid or "",
                "selected_rpid_short_name": r.selected.short_name if r.selected else "",
                "selected_rpid_long_name": r.selected.long_name if r.selected else "",
                "selected_score": r.selected_score or 0.0,
                "selected_strategy": r.selected_strategy or "",
                "candidate_rpids": "; ".join(
                    f"{c.entry.rpid}={c.score:.2f}" for c in r.candidates
                ),
                "adjudication": r.adjudication.value,
                "audit_notes": r.audit_notes or "",
            }
        )
    return pd.DataFrame(rows)


def export_csv(
    results: list[MatchResult],
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = results_to_dataframe(results)
    df.to_csv(output_path, index=False)
    return output_path


def export_audit_trail(
    results: list[MatchResult],
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in results:
        if r.adjudication == AdjudicationStatus.ACCEPTED:
            rows.append(
                {
                    "local_name": r.local_name,
                    "mapped_rpid": r.selected_rpid,
                    "mapped_to": r.selected.short_name if r.selected else "",
                    "confidence": r.selected_score,
                    "strategy": r.selected_strategy,
                    "timestamp": datetime.now().isoformat(),
                    "notes": r.audit_notes or "",
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    return output_path


def build_report(results: list[MatchResult]) -> HarmonizationReport:
    total = len(results)
    mapped = sum(
        1 for r in results if r.adjudication == AdjudicationStatus.ACCEPTED
    )
    pending = sum(
        1 for r in results if r.adjudication == AdjudicationStatus.PENDING
    )
    unmapped = total - mapped - pending
    return HarmonizationReport(
        results=results,
        total=total,
        mapped=mapped,
        unmapped=unmapped,
        pending=pending,
    )
