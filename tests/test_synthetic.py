from __future__ import annotations

from radlex_order_harmonizer.models import RadLexEntry
from radlex_order_harmonizer.synthetic_data import (
    generate_synthetic_names,
    write_synthetic_csv,
)


def _make_entry(
    rpid: str = "RPID1",
    short_name: str = "CT Abd w/wo",
    long_name: str = "CT Abdomen w and wo IV Contrast",
    modality: str = "CT",
    body_region: str = "ABDOMEN",
    playbook_type: str = "RADIOLOGY ORDERABLE",
) -> RadLexEntry:
    return RadLexEntry(
        rpid=rpid,
        letter_code="",
        short_name=short_name,
        long_name=long_name,
        modality=modality,
        playbook_type=playbook_type,
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
        pharmaceutical="",
        pharmaceutical_2="",
        view="",
        view_2="",
        view_3="",
        view_4="",
        rids="",
    )


def test_generate_synthetic_names_returns_correct_count():
    entries = [
        _make_entry(rpid="RPID1"),
        _make_entry(rpid="RPID2", short_name="MR Brain wo", long_name="MR Brain wo IV Contrast", modality="MR", body_region="HEAD"),
        _make_entry(rpid="RPID3", short_name="XR Chest", long_name="XR Chest 2 Views", modality="XR", body_region="CHEST"),
    ]
    names = generate_synthetic_names(entries, n=10, seed=42)
    assert len(names) == 10


def test_generate_synthetic_names_has_expected_keys():
    entries = [_make_entry()]
    names = generate_synthetic_names(entries, n=5, seed=1)
    for item in names:
        assert "local_name" in item
        assert "true_rpid" in item
        assert "true_short_name" in item


def test_generate_synthetic_names_preserves_true_rpid():
    entries = [
        _make_entry(rpid="RPID99", short_name="CT Abd w/wo"),
    ]
    names = generate_synthetic_names(entries, n=10, seed=1)
    for item in names:
        assert item["true_rpid"] == "RPID99"


def test_generate_synthetic_names_with_noise():
    entries = [_make_entry(short_name="CT Abd w/wo")]
    names = generate_synthetic_names(entries, n=20, seed=1, noise_rate=1.0)
    noisy = [n for n in names if n["local_name"] != "CT Abd w/wo"]
    assert len(noisy) > 0


def test_write_synthetic_csv_returns_dataframe(tmp_path):
    entries = [_make_entry()]
    output = str(tmp_path / "test_synthetic.csv")
    df = write_synthetic_csv(entries, output, n=5, seed=42)
    assert len(df) == 5
    assert list(df.columns) == ["local_name", "true_rpid", "true_short_name", "true_modality", "true_body_region"]
