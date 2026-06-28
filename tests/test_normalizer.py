from __future__ import annotations

from radlex_order_harmonizer.normalizer import (
    extract_body_parts,
    extract_contrast_status,
    extract_laterality,
    extract_modality,
    normalize_name,
    normalize_procedure,
    tokenize,
)


def test_normalize_name_lowercases():
    assert normalize_name("CT Abdomen w/ Contrast") == "ct abdomen with contrast"


def test_normalize_name_expands_abbreviations():
    assert normalize_name("CT Abd w/wo") == "ct abdomen with and without"
    assert normalize_name("MR C-Spine wo IV") == "mr cervical spine without intravenous"
    assert normalize_name("XR Chest w/o") == "xr chest without"


def test_normalize_name_removes_punctuation():
    assert normalize_name("CT Head (routine)") == "ct head routine"


def test_tokenize():
    tokens = tokenize("CT Abdomen w/ Contrast")
    assert "ct" in tokens
    assert "abdomen" in tokens
    assert "with" in tokens


def test_extract_modality_ct():
    assert extract_modality("CT Abdomen w/ Contrast") == "CT"


def test_extract_modality_mr():
    assert extract_modality("MR Brain wo Contrast") == "MR"


def test_extract_modality_xr():
    assert extract_modality("XR Chest 2 Views") == "XR"


def test_extract_modality_none():
    assert extract_modality("Chest X-Ray") is None


def test_extract_body_parts():
    parts = extract_body_parts("CT ABDOMEN and PELVIS w/ Contrast")
    assert "ABDOMEN" in parts
    assert "PELVIS" in parts


def test_extract_body_parts_single():
    assert extract_body_parts("XR CHEST PA") == ["CHEST"]


def test_extract_body_parts_spine():
    parts = extract_body_parts("MR CERVICAL SPINE wo Contrast")
    assert "CERVICAL SPINE" in parts


def test_extract_body_parts_none():
    assert extract_body_parts("CT 3D Post Processing") == []


def test_extract_contrast_with():
    assert extract_contrast_status("ct abdomen with contrast") == "with"


def test_extract_contrast_without():
    assert extract_contrast_status("ct head without contrast") == "without"


def test_extract_contrast_with_and_without():
    result = extract_contrast_status("mr brain with and without contrast")
    assert result == "without then with"


def test_extract_contrast_none():
    assert extract_contrast_status("xr chest 2 views") is None


def test_extract_laterality_left():
    assert extract_laterality("MR Left Knee wo Contrast") == "left"


def test_extract_laterality_right():
    assert extract_laterality("CT Right Hip") == "right"


def test_extract_laterality_bilateral():
    assert extract_laterality("US Bilateral Breasts") == "bilateral"


def test_extract_laterality_none():
    assert extract_laterality("CT Abdomen w/ Contrast") is None


def test_normalize_procedure_full():
    result = normalize_procedure("CT Abdomen w/ Contrast")
    assert result.original == "CT Abdomen w/ Contrast"
    assert result.modality == "CT"
    assert "ABDOMEN" in result.body_parts
    assert result.contrast_status == "with"
    assert result.laterality is None


def test_normalize_procedure_with_laterality():
    result = normalize_procedure("MR Left Knee wo Contrast")
    assert result.modality == "MR"
    assert result.laterality == "left"
    assert result.contrast_status == "without"
