"""
Healthcare facility detection using CMS hospital and SNF databases.

Matches against 5,286 hospitals and 12,130 skilled nursing facilities
from official CMS datasets.
"""

import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, FrozenSet, List, Set, Tuple

from .models import Finding


# Generic terms that should not be flagged as specific facilities
GENERIC_FACILITY_TERMS = frozenset({
    "skilled nursing facility", "nursing facility", "rehabilitation facility",
    "long term care facility", "acute care facility", "care facility",
    "outpatient facility", "inpatient facility", "treatment facility",
    "the hospital", "this hospital", "a hospital", "the facility",
    "this facility", "outside hospital", "local hospital",
    "general hospital", "community hospital", "regional hospital",
    "memorial hospital", "university hospital", "county hospital",
    "regional medical center", "community medical center",
})


@lru_cache(maxsize=1)
def _load_facility_names() -> Tuple[FrozenSet[str], Dict[str, str]]:
    """
    Load facility names from bundled data files.

    Returns:
        Tuple of (normalized_names_set, normalized_to_original_dict)
    """
    names: Set[str] = set()
    normalized_to_original: Dict[str, str] = {}

    data_dir = Path(__file__).parent / "data"

    # Load hospitals
    hospitals_file = data_dir / "cms_hospitals.txt"
    if hospitals_file.exists():
        with open(hospitals_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    normalized = _normalize_name(line)
                    if len(normalized) >= 4:  # Skip very short names
                        names.add(normalized)
                        normalized_to_original[normalized] = line

    # Load SNFs
    snf_file = data_dir / "cms_snf.txt"
    if snf_file.exists():
        with open(snf_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    normalized = _normalize_name(line)
                    if len(normalized) >= 4:
                        names.add(normalized)
                        if normalized not in normalized_to_original:
                            normalized_to_original[normalized] = line

    return frozenset(names), normalized_to_original


def _normalize_name(name: str) -> str:
    """Normalize a facility name for matching."""
    # Lowercase
    name = name.lower()
    # Remove punctuation except spaces
    name = re.sub(r'[^\w\s]', '', name)
    # Normalize whitespace
    name = ' '.join(name.split())
    return name


def detect_facilities(text: str) -> List[Finding]:
    """
    Detect healthcare facility names in text.

    Uses exact matching against CMS hospital and SNF databases.

    Args:
        text: Clinical text to analyze

    Returns:
        List of Finding objects for detected facilities
    """
    findings = []
    seen: Set[Tuple[int, int]] = set()

    normalized_names, normalized_to_original = _load_facility_names()
    text_lower = text.lower()

    # For each known facility name, find all occurrences
    for normalized_name in normalized_names:
        # Skip generic facility terms
        if normalized_name in GENERIC_FACILITY_TERMS:
            continue

        # Find all occurrences in text
        start = 0
        while True:
            pos = text_lower.find(normalized_name, start)
            if pos == -1:
                break

            end = pos + len(normalized_name)

            # Check word boundaries
            if _is_word_boundary(text, pos, end):
                if (pos, end) not in seen:
                    # Get the original text from the document
                    matched_text = text[pos:end]

                    # Additional validation
                    if not _is_false_positive(matched_text, text, pos, end):
                        findings.append(Finding(
                            text=matched_text,
                            phi_type="FACILITY",
                            start=pos,
                            end=end,
                            confidence=0.92,
                            source="facilities"
                        ))
                        seen.add((pos, end))

            start = pos + 1

    return findings


def _is_word_boundary(text: str, start: int, end: int) -> bool:
    """Check if the match is at word boundaries."""
    # Check start boundary
    if start > 0 and text[start-1].isalnum():
        return False
    # Check end boundary
    if end < len(text) and text[end].isalnum():
        return False
    return True


# Short words that are often false positives
FP_SHORT_WORDS = frozenset({
    "her", "his", "him", "she", "he", "the", "for", "and", "with", "but",
    "not", "was", "has", "had", "are", "were", "been", "this", "that",
    "ch", "cl", "cr", "h", "l", "n", "th", "pos", "neg",
    "mv", "av", "tv", "pv", "sv", "co", "ci", "ef", "lv", "rv", "la", "ra",
    "ct", "mri", "pet", "ekg", "ecg", "mg", "mcg", "ml", "dl", "ul",
})


def _is_false_positive(matched_text: str, full_text: str, start: int, end: int) -> bool:
    """Check if a detected facility is likely a false positive."""
    text_lower = matched_text.lower().strip()

    # Very short matches are likely false positives
    if len(text_lower) <= 3:
        return True

    # Check against known FP words
    if text_lower in FP_SHORT_WORDS:
        return True

    # If preceded by a digit, likely a lab value
    if start > 0:
        context_before = full_text[max(0, start-10):start]
        if re.search(r'\d\s*$', context_before):
            return True

    return False
