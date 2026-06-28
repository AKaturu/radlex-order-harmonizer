# radlex-order-harmonizer

[![CI](https://github.com/AKaturu/radlex-order-harmonizer/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/AKaturu/radlex-order-harmonizer/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Map local radiology procedure names to standardized RadLex Playbook identifiers.**

`radlex-order-harmonizer` downloads the latest RadLex Playbook from RSNA and matches your local procedure names using exact, token-overlap, and fuzzy string matching with confidence scoring.

## Quick Start

```bash
pip install radlex-order-harmonizer
radlex-harmonize demo
radlex-harmonize serve
```

## What It Does

- Downloads RadLex Playbook CSV automatically from RSNA's public API (cached locally)
- Normalizes procedure names: expands abbreviations (Abd → Abdomen, w/ → with), detects modality, body part, contrast status, laterality
- Three-tier matching: exact match → token overlap (Jaccard) → fuzzy (RapidFuzz token set ratio)
- Ranks candidates by confidence score, supports human adjudication
- Generates synthetic local procedure names with realistic variations for testing
- Exports match results, audit trails, and adjudicated mappings to CSV
- Interactive Streamlit dashboard for visual adjudication

## CLI Commands

| Command | Description |
|---|---|
| `radlex-harmonize demo` | Generate synthetic procedures and run matching |
| `radlex-harmonize match --csv <file>` | Match local procedure names against RadLex |
| `radlex-harmonize adjudicate --csv <file>` | Apply human adjudication from a CSV |
| `radlex-harmonize serve` | Launch the Streamlit dashboard |

## Input CSV Format

```csv
local_name
CT Abdomen w/ Contrast
XR Chest 2 Views
MR Brain wo IV Contrast
```

## Output Fields

- `local_name` — original procedure name
- `normalized` — cleaned and expanded name
- `detected_modality`, `detected_body_parts`, `detected_contrast`, `detected_laterality`
- `selected_rpid` — best matching RadLex RPID code
- `selected_score` — confidence score (0–1)
- `selected_strategy` — exact, token, or fuzzy
- `candidate_rpids` — alternative candidates with scores
- `adjudication` — pending/accepted/rejected
- `audit_notes` — optional free-text notes

## Data Source

RadLex Playbook is provided by the [Radiological Society of North America (RSNA)](https://www.rsna.org/practice-tools/data-tools-and-standards/radlex-radiology-lexicon). This tool downloads the complete Playbook CSV from `https://api3.rsna.org/radlex/v1/createCsv?csvType=new`. The data is freely available under the [RadLex License](http://www.rsna.org/uploadedFiles/RSNA/Content/Informatics/RadLex_License_Agreement_and_Terms_of_Use_V2_Final.pdf).
