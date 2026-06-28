from __future__ import annotations

from pathlib import Path

from radlex_order_harmonizer.models import (
    AdjudicationStatus,
    CandidateMatch,
    MatchResult,
    MatchStrategy,
    RadLexEntry,
)
from radlex_order_harmonizer.normalizer import normalize_procedure
from radlex_order_harmonizer.reporter import (
    build_report,
    export_audit_trail,
    export_csv,
    results_to_dataframe,
)


def _make_entry(rpid: str = "RPID1") -> RadLexEntry:
    return RadLexEntry(
        rpid=rpid,
        letter_code="",
        short_name=f"CT procedure {rpid}",
        long_name="",
        modality="CT",
        playbook_type="RADIOLOGY ORDERABLE",
        population=" ",
        body_region="ABDOMEN",
        body_region_2="",
        body_region_3="",
        modality_modifier="",
        modality_modifier_2="",
        procedure_modifier="",
        procedure_modifier_2="",
        anatomic_focus="",
        anatomic_focus_2="",
        laterality="",
        reason_for_exam="",
        technique="",
        pharmaceutical="",
        pharmaceutical_2="",
        view="",
        view_2="",
        view_3="",
        view_4="",
        rids="",
    )


def test_results_to_dataframe_has_correct_columns():
    entry = _make_entry()
    norm = normalize_procedure("CT Abdomen")
    result = MatchResult(
        local_name="CT Abdomen",
        normalized=norm,
        candidates=[CandidateMatch(entry=entry, score=0.95, strategy=MatchStrategy.FUZZY)],
        selected=entry,
        selected_rpid="RPID1",
        selected_score=0.95,
        selected_strategy="fuzzy",
        adjudication=AdjudicationStatus.PENDING,
    )
    df = results_to_dataframe([result])
    assert "local_name" in df.columns
    assert "selected_rpid" in df.columns
    assert "selected_score" in df.columns
    assert df.iloc[0]["selected_rpid"] == "RPID1"


def test_export_csv_writes_file(tmp_path: Path):
    entry = _make_entry()
    norm = normalize_procedure("CT Abdomen")
    result = MatchResult(
        local_name="CT Abdomen",
        normalized=norm,
        selected=entry,
        selected_rpid="RPID1",
        selected_score=0.95,
        selected_strategy="fuzzy",
        adjudication=AdjudicationStatus.PENDING,
    )
    out = tmp_path / "test.csv"
    result_path = export_csv([result], out)
    assert result_path.exists()


def test_export_audit_trail_only_accepted(tmp_path: Path):
    entry = _make_entry()
    norm_pending = normalize_procedure("CT Pending")
    pending = MatchResult(
        local_name="CT Pending",
        normalized=norm_pending,
        selected=entry,
        selected_rpid="RPID1",
        selected_score=0.9,
        selected_strategy="fuzzy",
        adjudication=AdjudicationStatus.PENDING,
    )
    norm_accepted = normalize_procedure("CT Accepted")
    accepted = MatchResult(
        local_name="CT Accepted",
        normalized=norm_accepted,
        selected=entry,
        selected_rpid="RPID1",
        selected_score=0.95,
        selected_strategy="exact",
        adjudication=AdjudicationStatus.ACCEPTED,
    )
    out = tmp_path / "audit.csv"
    export_audit_trail([pending, accepted], out)
    df = __import__("pandas").read_csv(out)
    assert len(df) == 1
    assert df.iloc[0]["local_name"] == "CT Accepted"


def test_build_report_counts():
    entry = _make_entry()
    norm1 = normalize_procedure("CT Abdomen")
    norm2 = normalize_procedure("XR Chest")
    results = [
        MatchResult(
            local_name="CT Abdomen",
            normalized=norm1,
            selected=entry,
            selected_rpid="RPID1",
            selected_score=0.95,
            adjudication=AdjudicationStatus.ACCEPTED,
        ),
        MatchResult(
            local_name="XR Chest",
            normalized=norm2,
            adjudication=AdjudicationStatus.PENDING,
        ),
    ]
    report = build_report(results)
    assert report.total == 2
    assert report.mapped == 1
    assert report.pending == 1
    assert report.unmapped == 0
    assert report.coverage == 0.5
