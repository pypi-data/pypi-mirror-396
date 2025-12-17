"""
Script detection for text strings.

Detects the writing system (script) of text fields to determine if
transliteration is needed before comparison.
"""

import unicodedata

from .enums import Script


def detect_script(text: str) -> Script:
    """
    Detect the primary script used in text.

    Analyzes Unicode character properties to determine the writing system.
    Returns MIXED if multiple scripts are present, UNKNOWN if cannot determine.

    Args:
        text: Input text to analyze

    Returns:
        Script enum value (LATIN, GREEK, GEORGIAN, CYRILLIC, MIXED, UNKNOWN)

    Example:
        >>> detect_script("Maria")
        <Script.LATIN: 'LATIN'>
        >>> detect_script("Μαρία")
        <Script.GREEK: 'GREEK'>
        >>> detect_script("Maria Μαρία")
        <Script.MIXED: 'MIXED'>
    """
    if not text or not text.strip():
        return Script.UNKNOWN

    # Count characters by script
    script_counts: dict[Script, int] = {
        Script.LATIN: 0,
        Script.GREEK: 0,
        Script.GEORGIAN: 0,
        Script.CYRILLIC: 0,
    }

    total_alphabetic = 0

    for char in text:
        # Only consider alphabetic characters for script detection
        if not char.isalpha():
            continue

        total_alphabetic += 1
        char_name = unicodedata.name(char, "")

        # Detect script based on Unicode character name
        if "LATIN" in char_name:
            script_counts[Script.LATIN] += 1
        elif "GREEK" in char_name:
            script_counts[Script.GREEK] += 1
        elif "GEORGIAN" in char_name:
            script_counts[Script.GEORGIAN] += 1
        elif "CYRILLIC" in char_name:
            script_counts[Script.CYRILLIC] += 1

    # No alphabetic characters found
    if total_alphabetic == 0:
        return Script.UNKNOWN

    # Find dominant script
    max_count = max(script_counts.values())
    if max_count == 0:
        return Script.UNKNOWN

    # Count how many scripts have characters
    scripts_present = [s for s, count in script_counts.items() if count > 0]

    # If multiple scripts present, return MIXED
    if len(scripts_present) > 1:
        return Script.MIXED

    # Return the single script present
    for script, count in script_counts.items():
        if count == max_count:
            return script

    return Script.UNKNOWN
