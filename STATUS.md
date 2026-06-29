# Status

## Current Release
**v0.1.0** (2026-06-28) — MVP release.

## Implemented Features
- RadLex Playbook CSV download from RSNA with local caching
- Local procedure-name normalization (abbreviation expansion, modality/anatomy/contrast/laterality detection)
- Three-tier matching: exact, token-overlap, and fuzzy (rapidfuzz)
- Confidence scoring and ranked candidate export
- Synthetic local procedure name generator for demos and regression tests
- CLI commands: demo, match, adjudicate, serve
- Streamlit dashboard for interactive mapping review
- Human adjudication import (accept/reject candidate mappings)
- Native desktop release packaging (Windows, macOS, Linux)

## Validation Status
- **Unit tests**: Pass (data loader, normalizer, matcher, reporter, synthetic data)
- **Synthetic end-to-end test**: Complete (demo generates synthetic procedures, downloads RadLex, runs matching, produces report)
- **Public-data evaluation**: Not completed
- **Expert review**: Not completed
- **Institutional validation**: Not completed
- **Prospective clinical validation**: Not completed

## Planned Work
- Validate matching against institution-specific order dictionaries with adjudicated ground truth
- Configurable synonym dictionaries for local naming conventions
- Export templates for common enterprise mapping-review workflows
- Published versioned releases and PyPI package
