from __future__ import annotations

from radlex_order_harmonizer.matcher import batch_match, find_matches
from radlex_order_harmonizer.models import (
    MatchStrategy,
    RadLexEntry,
)


def _make_entry(
    rpid: str = "RPID1",
    short_name: str = "CT Abd w/wo",
    long_name: str = "CT Abdomen w and wo IV Contrast",
    modality: str = "CT",
    body_region: str = "ABDOMEN",
    pharmaceutical: str = "WITHOUT THEN WITH IV CONTRAST",
) -> RadLexEntry:
    return RadLexEntry(
        rpid=rpid,
        letter_code="",
        short_name=short_name,
        long_name=long_name,
        modality=modality,
        playbook_type="RADIOLOGY ORDERABLE",
        population=" ",
        body_region=body_region,
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
        pharmaceutical=pharmaceutical,
        pharmaceutical_2="",
        view="",
        view_2="",
        view_3="",
        view_4="",
        rids="",
    )


def test_exact_match_short_name():
    entries = [_make_entry(rpid="RPID1", short_name="CT Abd w/wo")]
    result = find_matches("CT Abd w/wo", entries)
    assert result.best_candidate is not None
    assert result.best_candidate.score == 1.0
    assert result.best_candidate.strategy == MatchStrategy.EXACT
    assert result.selected_rpid == "RPID1"


def test_exact_match_long_name():
    entries = [_make_entry(long_name="CT Abdomen w and wo IV Contrast")]
    result = find_matches("CT Abdomen w and wo IV Contrast", entries)
    assert result.best_candidate is not None
    assert result.best_candidate.strategy == MatchStrategy.EXACT


def test_case_insensitive_match():
    entries = [_make_entry(short_name="CT Abd w/wo")]
    result = find_matches("ct abd w/wo", entries)
    assert result.best_candidate is not None
    assert result.best_candidate.score >= 0.5


def test_token_match():
    entries = [_make_entry(rpid="RPID1", short_name="CT Abd w/wo")]
    result = find_matches("CT Abdomen with and without", entries)
    assert result.best_candidate is not None
    assert result.best_candidate.score >= 0.3


def test_fuzzy_match():
    entries = [_make_entry(rpid="RPID1", short_name="CT Abd w/wo")]
    result = find_matches("Cat Scan Abdomen with contrast", entries)
    assert result.best_candidate is not None
    assert result.best_candidate.score >= 0.3


def test_no_match():
    entries = [_make_entry(short_name="CT Abd w/wo")]
    result = find_matches("XR Chest 2 Views", entries, min_score=0.9)
    assert result.best_candidate is None
    assert result.selected is None


def test_multiple_candidates():
    entries = [
        _make_entry(rpid="RPID2", short_name="CT Abd w", long_name="CT Abdomen w IV Contrast"),
        _make_entry(rpid="RPID3", short_name="CT Abd wo", long_name="CT Abdomen wo IV Contrast"),
    ]
    result = find_matches("CT Abdomen with contrast", entries, max_candidates=2)
    assert len(result.candidates) <= 2
    assert result.selected_rpid == "RPID2"


def test_candidates_ordered_by_score():
    entries = [
        _make_entry(rpid="RPID2", short_name="CT Abd w", long_name="CT Abdomen w IV Contrast"),
        _make_entry(rpid="RPID3", short_name="CT Abd wo", long_name="CT Abdomen wo IV Contrast"),
    ]
    result = find_matches("CT Abdomen with contrast", entries, max_candidates=5)
    scores = [c.score for c in result.candidates]
    assert scores == sorted(scores, reverse=True)


def test_batch_match():
    entries = [_make_entry(short_name="CT Abd w/wo")]
    names = ["CT Abd w/wo", "CT Abdomen w/wo", "XR Chest"]
    results = batch_match(names, entries, max_candidates=2, min_score=0.1)
    assert len(results) == 3
    assert results[0].best_candidate is not None


def test_min_score_filters():
    entries = [_make_entry(short_name="CT Abd w/wo")]
    result = find_matches("XR Chest", entries, min_score=1.0)
    assert result.best_candidate is None
