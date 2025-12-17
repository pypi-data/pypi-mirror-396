"""
Name and country normalization functions.

Provides Unicode-aware normalization for names and countries, including
whitespace handling, case normalization, diacritics removal, and
script-aware transliteration.
"""

import unicodedata

from .script import detect_script
from .transliterate import transliterate_to_latin


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.

    Trims leading/trailing whitespace and collapses multiple consecutive
    spaces to a single space.

    Args:
        text: Input text

    Returns:
        Text with normalized whitespace

    Example:
        >>> normalize_whitespace("  MARÍA   García  ")
        'MARÍA García'
    """
    return " ".join(text.split())


def remove_diacritics(text: str) -> str:
    """
    Remove diacritics from text for Latin-normalized comparison.

    Uses Unicode NFD decomposition to separate base characters from
    combining marks, then filters out combining marks.

    Args:
        text: Input text with diacritics

    Returns:
        Text with diacritics removed

    Example:
        >>> remove_diacritics("María García")
        'Maria Garcia'
        >>> remove_diacritics("José Müller")
        'Jose Muller'
    """
    # Decompose to base + combining marks
    nfd = unicodedata.normalize("NFD", text)
    # Filter out combining marks (category "M")
    return "".join(c for c in nfd if not unicodedata.combining(c))


def normalize_name(name: str, preserve_script: bool = False, version: str = "v1") -> str:
    """
    Normalize a name string.

    Normalization pipeline:
    1. Unicode NFC normalization
    2. Whitespace normalization (trim, collapse)
    3. Case normalization (casefold)
    4. Script handling:
       - If preserve_script=True: Keep original script
       - If preserve_script=False: Transliterate to Latin + remove diacritics

    Args:
        name: Input name (given or surname)
        preserve_script: If True, keep original script; if False, transliterate to Latin
        version: Normalization version (default: "v1")

    Returns:
        Normalized name string

    Example:
        >>> normalize_name("  MARÍA  ")
        'maria'
        >>> normalize_name("Μαρία")  # Greek
        'maria'
        >>> normalize_name("Μαρία", preserve_script=True)
        'μαρία'
    """
    if not name or not name.strip():
        return ""

    # Step 1: Unicode NFC normalization (composed form)
    normalized = unicodedata.normalize("NFC", name)

    # Step 2: Whitespace normalization
    normalized = normalize_whitespace(normalized)

    # Step 3: Case normalization (casefold)
    normalized = normalized.casefold()

    # Step 4: Script handling
    if not preserve_script:
        # Detect script
        script = detect_script(normalized)

        # Transliterate if non-Latin
        normalized = transliterate_to_latin(normalized, script, profile="default_v1")

        # Remove diacritics for Latin-normalized form
        normalized = remove_diacritics(normalized)

    return normalized


def normalize_country(country: str | None, version: str = "v1") -> str | None:
    """
    Normalize country to standard form.

    Normalizes to lowercase for consistency with name normalization.
    Removes diacritics and collapses whitespace.

    Args:
        country: Country code or name
        version: Normalization version (default: "v1")

    Returns:
        Normalized country string or empty string if input is None/empty

    Example:
        >>> normalize_country("spain")
        'spain'
        >>> normalize_country("ES")
        'es'
        >>> normalize_country("España")
        'espana'
        >>> normalize_country(None)
        ''
    """
    if not country or not country.strip():
        return ""

    # Normalize whitespace, lowercase, remove diacritics
    normalized = normalize_whitespace(country)
    normalized = normalized.casefold()
    normalized = remove_diacritics(normalized)

    return normalized
