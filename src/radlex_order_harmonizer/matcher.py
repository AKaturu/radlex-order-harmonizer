from __future__ import annotations

from rapidfuzz import fuzz

from .models import (
    CandidateMatch,
    MatchResult,
    MatchStrategy,
    RadLexEntry,
)
from .normalizer import normalize_name, normalize_procedure


def _exact_match(local_norm: str, entry: RadLexEntry) -> CandidateMatch | None:
    for name in entry.all_names:
        entry_norm = normalize_name(name)
        if local_norm == entry_norm:
            return CandidateMatch(entry=entry, score=1.0, strategy=MatchStrategy.EXACT)
    return None


def _token_overlap(local_tokens: set[str], entry: RadLexEntry) -> float | None:
    entry_tokens: set[str] = set()
    for name in entry.all_names:
        entry_tokens.update(normalize_name(name).split())
    if not local_tokens or not entry_tokens:
        return None
    intersection = local_tokens & entry_tokens
    union = local_tokens | entry_tokens
    return len(intersection) / len(union)


def _fuzzy_score(normalized_name: str, entry: RadLexEntry) -> float | None:
    best = 0.0
    for name in entry.all_names:
        entry_norm = normalize_name(name)
        score = fuzz.token_set_ratio(normalized_name, entry_norm) / 100.0
        if score > best:
            best = score
    return best if best > 0 else None


def find_matches(
    local_name: str,
    entries: list[RadLexEntry],
    max_candidates: int = 5,
    min_score: float = 0.3,
) -> MatchResult:
    normalized = normalize_procedure(local_name)
    result = MatchResult(local_name=local_name, normalized=normalized)

    candidates: list[CandidateMatch] = []

    for entry in entries:
        exact = _exact_match(normalized.normalized, entry)
        if exact:
            candidates.append(exact)
            continue

        token_j = _token_overlap(set(normalized.tokens), entry)
        fuzzy = _fuzzy_score(normalized.normalized, entry)

        scores: list[tuple[float, MatchStrategy]] = []
        if token_j is not None:
            scores.append((token_j, MatchStrategy.TOKEN))
        if fuzzy is not None:
            scores.append((fuzzy, MatchStrategy.FUZZY))

        best_score = max(s[0] for s in scores) if scores else 0.0
        best_strategy = max(scores, key=lambda x: x[0])[1] if scores else MatchStrategy.FUZZY

        if best_score >= min_score:
            candidates.append(
                CandidateMatch(entry=entry, score=best_score, strategy=best_strategy)
            )

    candidates.sort(key=lambda c: c.score, reverse=True)
    result.candidates = candidates[:max_candidates]

    if candidates:
        best = candidates[0]
        result.selected = best.entry
        result.selected_rpid = best.entry.rpid
        result.selected_score = best.score
        result.selected_strategy = best.strategy.value

    return result


def batch_match(
    local_names: list[str],
    entries: list[RadLexEntry],
    max_candidates: int = 5,
    min_score: float = 0.3,
) -> list[MatchResult]:
    return [
        find_matches(name, entries, max_candidates, min_score) for name in local_names
    ]
