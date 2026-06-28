# Contributing

Thanks for helping improve `radlex-order-harmonizer`.

## Local Setup

```bash
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
```

## Pull Requests

- Keep changes focused and documented.
- Add or update tests for matching, normalization, reporting, or CLI behavior.
- Use synthetic examples in issues and tests unless your institution has approved sharing real data.
- Note any RadLex Playbook data-source assumptions in the PR description.

## Development Notes

The project is intended for mapping support and adjudication workflows. It should not silently overwrite production order dictionaries without human review.
