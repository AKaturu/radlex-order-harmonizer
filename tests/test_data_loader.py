from __future__ import annotations

from pathlib import Path

import pytest

from radlex_order_harmonizer.data_loader import parse_radlex_csv
from radlex_order_harmonizer.models import RadLexEntry

SAMPLE_CSV = """RPID,LETTER_CODE,SHORT_NAME,LONG_NAME,MODALITY,PLAYBOOK_TYPE,POPULATION,BODY_REGION,BODY_REGION_2,BODY_REGION_3,BODY_REGION_4,BODY_REGION_5,MODALITY_MODIFIER,MODALITY_MODIFIER_2,MODALITY_MODIFIER_3,PROCEDURE_MODIFIER,PROCEDURE_MODIFIER_2,ANATOMIC_FOCUS,ANATOMIC_FOCUS_2,LATERALITY,REASON_FOR_EXAM,REASON_FOR_EXAM_2,REASON_FOR_EXAM_3,TECHNIQUE,PHARMACEUTICAL,PHARMACEUTICAL_2,VIEW,VIEW_2,VIEW_3,VIEW_4,,RIDS
RPID2,CTABCA,"CT Abd Angio w/wo","CT Abdomen Angio w and wo IV Contrast",CT,RADIOLOGY ORDERABLE, ,ABDOMEN, , , , ,ANGIOGRAPHY, , , , , , , , , , , , ,WITHOUT THEN WITH IV CONTRAST, , , , , , ,RID10321|RID13060|0|RID56|0|0|0|0|RID10371|0|0|0|0|0|0|0|0|0|0|0|RID28771|0|0|0|0|0|
RPID16,CTCHU,"CT Chest wo","CT Chest wo IV Contrast",CT,RADIOLOGY ORDERABLE, ,CHEST, , , , , , , , , , , , , , , , , ,WITHOUT IV CONTRAST, , , , , , ,RID10321|RID13060|0|RID1243|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|RID28768|0|0|0|0|0|
RPID479,MRHDU,"MR Head wo","MR Head wo IV Contrast",MR,RADIOLOGY ORDERABLE, ,HEAD, , , , , , , , , , , , , , , , , ,WITHOUT IV CONTRAST, , , , , , ,RID10312|RID13060|0|RID9080|0|0|0|0|0|0|0|0|0|RID6434|0|0|0|0|0|0|RID28768|0|0|0|0|
"""


@pytest.fixture
def sample_csv_path(tmp_path: Path) -> Path:
    p = tmp_path / "test_radlex.csv"
    p.write_text(SAMPLE_CSV, encoding="utf-8")
    return p


def test_parse_radlex_csv_parses_all_rows(sample_csv_path: Path):
    entries = parse_radlex_csv(sample_csv_path)
    assert len(entries) == 3


def test_parse_radlex_csv_rpid(sample_csv_path: Path):
    entries = parse_radlex_csv(sample_csv_path)
    assert entries[0].rpid == "RPID2"
    assert entries[1].rpid == "RPID16"
    assert entries[2].rpid == "RPID479"


def test_parse_radlex_csv_fields(sample_csv_path: Path):
    entries = parse_radlex_csv(sample_csv_path)
    entry = entries[0]
    assert entry.short_name == "CT Abd Angio w/wo"
    assert entry.long_name == "CT Abdomen Angio w and wo IV Contrast"
    assert entry.modality == "CT"
    assert entry.body_region == "ABDOMEN"


def test_parse_radlex_csv_mr_entry(sample_csv_path: Path):
    entries = parse_radlex_csv(sample_csv_path)
    entry = entries[2]
    assert entry.rpid == "RPID479"
    assert entry.modality == "MR"
    assert entry.body_region == "HEAD"


def test_parse_radlex_csv_all_names(sample_csv_path: Path):
    entries = parse_radlex_csv(sample_csv_path)
    entry = entries[0]
    assert "CT Abd Angio w/wo" in entry.all_names
    assert "CT Abdomen Angio w and wo IV Contrast" in entry.all_names


def test_parse_radlex_csv_body_regions(sample_csv_path: Path):
    entries = parse_radlex_csv(sample_csv_path)
    entry = entries[0]
    assert "ABDOMEN" in entry.body_regions


def test_radlex_entry_is_dataclass():
    entry = RadLexEntry(
        rpid="RPID1",
        letter_code="",
        short_name="test",
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
    assert entry.rpid == "RPID1"
    assert entry.modality == "CT"
    assert entry.all_names == ["test"]
