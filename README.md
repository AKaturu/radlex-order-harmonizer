# radlex-order-harmonizer

[![CI](https://github.com/AKaturu/radlex-order-harmonizer/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/AKaturu/radlex-order-harmonizer/actions/workflows/ci.yml)
[![Desktop/native release](https://github.com/AKaturu/radlex-order-harmonizer/actions/workflows/release.yml/badge.svg)](https://github.com/AKaturu/radlex-order-harmonizer/actions/workflows/release.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Map local radiology procedure names to standardized RadLex Playbook identifiers.**

![radlex-order-harmonizer demo](docs/assets/demo.gif)

`radlex-order-harmonizer` downloads the RadLex Playbook from RSNA, normalizes local radiology order names, and produces reviewable mapping candidates with confidence scores. It is built for order-dictionary cleanup, terminology harmonization, migration prep, and human adjudication workflows.

## Quick Start

Install from source:

```bash
git clone https://github.com/AKaturu/radlex-order-harmonizer.git
cd radlex-order-harmonizer
python -m pip install -e ".[app]"
radlex-harmonize demo --output outputs/demo --n 50 --seed 42
radlex-harmonize serve
```

Prefer a no-Python install? Download a Windows, macOS, or Linux archive from the [Releases](https://github.com/AKaturu/radlex-order-harmonizer/releases) page after a release build is published.

## Why It Exists

Hospitals often have local procedure names that drift from standard terminology. This makes analytics, protocol review, migration, and cross-site reporting harder. This project creates transparent RadLex Playbook candidate mappings that can be reviewed by radiology operations, informatics, and quality teams.

## What It Does

- Downloads and caches the RadLex Playbook CSV from RSNA.
- Normalizes local procedure names by expanding abbreviations and detecting modality, anatomy, contrast, and laterality.
- Uses exact, token-overlap, and fuzzy matching to propose RadLex Playbook identifiers.
- Exports top candidates, scores, strategies, and adjudication fields.
- Generates synthetic local order names for demos and regression tests.
- Provides a Streamlit dashboard for interactive mapping review.

## CLI Commands

| Command | Description |
|---|---|
| `radlex-harmonize demo` | Generate synthetic procedures and run matching. |
| `radlex-harmonize match --csv <file>` | Match local procedure names against RadLex. |
| `radlex-harmonize adjudicate --csv <file>` | Apply human adjudication from a CSV. |
| `radlex-harmonize serve` | Launch the Streamlit dashboard. |

## Input CSV Format

```csv
local_name
CT Abdomen w/ Contrast
XR Chest 2 Views
MR Brain wo IV Contrast
```

## Output Fields

| Field | Meaning |
|---|---|
| `local_name` | Original local procedure name. |
| `normalized` | Cleaned and expanded local name. |
| `detected_modality` | Inferred modality such as CT, MR, US, or XR. |
| `detected_body_parts` | Inferred anatomic terms. |
| `detected_contrast` | Inferred contrast status. |
| `selected_rpid` | Best matching RadLex Playbook identifier. |
| `selected_score` | Confidence score from 0 to 1. |
| `selected_strategy` | Exact, token, or fuzzy matching strategy. |
| `candidate_rpids` | Alternative candidate identifiers and scores. |
| `adjudication` | Pending, accepted, or rejected review status. |
| `audit_notes` | Optional reviewer notes. |

## Repository Guide

| Path | Purpose |
|---|---|
| `src/radlex_order_harmonizer/data_loader.py` | RadLex download, cache, and CSV parsing. |
| `src/radlex_order_harmonizer/normalizer.py` | Procedure-name normalization. |
| `src/radlex_order_harmonizer/matcher.py` | Candidate scoring and ranking. |
| `src/radlex_order_harmonizer/reporter.py` | Result table and summary generation. |
| `src/radlex_order_harmonizer/dashboard.py` | Streamlit dashboard. |
| `scripts/build_native.py` | Native executable packaging helper for GitHub Actions. |
| `scripts/generate_demo_media.py` | Reproducible README media generator. |
| `tests/` | Data loader, matcher, normalizer, reporter, and synthetic data tests. |

## Demo Media

The README animation is generated from a real synthetic CLI demo run:

```bash
python -m pip install -e ".[media]"
python scripts/generate_demo_media.py
```

See [docs/demo-media.md](docs/demo-media.md) for details.

## Releases

The [Desktop/native release](.github/workflows/release.yml) workflow builds downloadable CLI archives for Windows, macOS, and Linux. It can be run manually from GitHub Actions, or by pushing a tag such as `v0.1.0`.

See [docs/release.md](docs/release.md) for release steps.

## Data Source

RadLex Playbook is provided by the [Radiological Society of North America (RSNA)](https://www.rsna.org/practice-tools/data-tools-and-standards/radlex-radiology-lexicon). This tool downloads the complete Playbook CSV from `https://api3.rsna.org/radlex/v1/createCsv?csvType=new`. Review the [RadLex License](http://www.rsna.org/uploadedFiles/RSNA/Content/Informatics/RadLex_License_Agreement_and_Terms_of_Use_V2_Final.pdf) before redistributing derived data.

## Safety And Scope

This tool is intended for terminology review, research, and quality improvement workflows. It does not replace human adjudication and should not automatically overwrite production order dictionaries without institutional review.
