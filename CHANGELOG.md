# Changelog

## 0.1.0 - 2026-06-28

### Added
- RadLex Playbook CSV download from RSNA with local caching
- Local procedure-name normalization (abbreviation expansion, modality/anatomy/contrast/laterality detection)
- Three-tier matching: exact, token-overlap, and fuzzy (rapidfuzz)
- Confidence scoring and ranked candidate export
- Synthetic local procedure name generator for demos and regression tests
- CLI commands (demo, match, adjudicate, serve)
- Streamlit dashboard for interactive mapping review
- Human adjudication import (accept/reject candidate mappings)
- Native desktop release packaging (Windows, macOS, Linux)
- GitHub Actions CI (lint, type check, test, demo smoke)
- Full test suite (data loader, normalizer, matcher, reporter, synthetic data)
- Reproducible README demo media generation
