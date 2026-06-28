# PROJECT_STATE

## Project Overview

### Project Name
radlex-order-harmonizer

### Goal
Map local radiology procedure names to standardized RadLex Playbook identifiers with transparent matching, confidence scoring, and human adjudication support.

### Current Status
Phase 1 - MVP complete. Core normalization, RadLex loading, matching, reporting, CLI, dashboard, tests, demo media tooling, and native release automation are implemented.

### 2026-06-28 GitHub Polish And Releases
- Added reproducible README demo media generated from the real synthetic CLI demo.
- Added `scripts/build_native.py` for local and CI PyInstaller builds.
- Added a `Desktop/native release` GitHub Actions workflow for Windows, macOS, and Linux artifacts.
- Added release and demo-media documentation under `docs/`.
- Added `CONTRIBUTING.md` and `SECURITY.md`.
- Refreshed the README with badges, demo media, safer scope language, repository guide, and release instructions.

## Completed Features

- RadLex Playbook CSV download and local cache.
- Local procedure-name normalization with modality, body part, contrast, and laterality detection.
- Exact, token-overlap, and fuzzy candidate matching.
- Confidence scoring and candidate export for review.
- Synthetic procedure-name demo generation.
- CLI commands for demo, matching, adjudication, and dashboard launch.
- Streamlit dashboard for interactive review.
- Test suite covering data loading, normalization, matching, reporting, and synthetic data.

## Remaining Work

- Validate matching against institution-specific order dictionaries with adjudicated ground truth.
- Add configurable synonym dictionaries for local naming conventions.
- Add export templates for common enterprise mapping-review workflows.
- Publish versioned releases and optional PyPI package.
