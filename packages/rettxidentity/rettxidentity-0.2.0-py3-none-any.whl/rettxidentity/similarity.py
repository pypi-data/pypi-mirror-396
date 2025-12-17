"""
String similarity calculation using rapidfuzz.

Provides tiered comparison: exact → casefold → diacritics removed → fuzzy.
"""

from rapidfuzz import fuzz

from .normalize import normalize_name, remove_diacritics


def calculate_similarity(s1: str, s2: str, normalize: bool = True) -> float:
    """
    Calculate string similarity score.

    Uses tiered comparison strategy:
    1. Exact match (after whitespace normalization) → 1.0
    2. Case-insensitive match → 0.99
    3. Diacritics removed → 0.98
    4. Fuzzy match (RapidFuzz ratio) → algorithm score

    Args:
        s1: First string
        s2: Second string
        normalize: If True, normalize both strings before comparison

    Returns:
        Similarity score in range [0.0, 1.0]

    Example:
        >>> calculate_similarity("Garcia", "García")
        0.92  # Approximate, depends on algorithm
        >>> calculate_similarity("Garcia", "García", normalize=True)
        1.0  # After normalization, identical
    """
    # Handle empty or whitespace-only strings
    s1_stripped = s1.strip() if s1 else ""
    s2_stripped = s2.strip() if s2 else ""

    # Both empty = identical = 1.0
    if not s1_stripped and not s2_stripped:
        return 1.0

    # One empty, one not = no similarity
    if not s1_stripped or not s2_stripped:
        return 0.0

    if normalize:
        # Tier 1: Exact match (after normalization with diacritics removed)
        s1_normalized = normalize_name(s1, preserve_script=False)
        s2_normalized = normalize_name(s2, preserve_script=False)

        if s1_normalized == s2_normalized:
            return 1.0

        # Tier 2: Use fuzzy matching on normalized forms
        # rapidfuzz.fuzz.ratio returns 0-100, normalize to 0.0-1.0
        ratio = fuzz.ratio(s1_normalized, s2_normalized)
        return ratio / 100.0
    else:
        # Direct comparison without normalization
        if s1 == s2:
            return 1.0

        # Tier 1: Case-insensitive
        if s1.casefold() == s2.casefold():
            return 0.99

        # Tier 2: Diacritics removed
        if remove_diacritics(s1).casefold() == remove_diacritics(s2).casefold():
            return 0.98

        # Tier 3: Fuzzy match
        ratio = fuzz.ratio(s1, s2)
        return ratio / 100.0
