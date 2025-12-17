"""
Transliteration from non-Latin scripts to Latin.

Provides transliteration from Greek, Georgian, and Cyrillic scripts to Latin
for comparison and display purposes. Uses the transliterate library for
deterministic, reversible transliteration.
"""

from transliterate import get_available_language_codes, translit  # type: ignore[import-untyped]

from .enums import Script
from .errors import UnsupportedScriptError


def transliterate_to_latin(text: str, source_script: Script, profile: str = "default_v1") -> str:
    """
    Transliterate non-Latin text to Latin script.

    Uses the transliterate library with language-specific packs for Greek,
    Georgian, and Cyrillic. Returns original text for Latin or unsupported scripts.

    Args:
        text: Input text to transliterate
        source_script: Script of the input text
        profile: Transliteration profile (currently only "default_v1" supported)

    Returns:
        Transliterated Latin text, or original text if script is Latin/unsupported

    Raises:
        UnsupportedScript: If script cannot be transliterated (informational only)

    Example:
        >>> transliterate_to_latin("Παπαδοπούλου", Script.GREEK)
        'Papadopoulou'
        >>> transliterate_to_latin("ბერიძე", Script.GEORGIAN)
        'Beridze'
    """
    if not text or not text.strip():
        return text

    # Latin text doesn't need transliteration
    if source_script == Script.LATIN:
        return text

    # Map scripts to transliterate language codes
    script_to_lang = {
        Script.GREEK: "el",  # Greek
        Script.GEORGIAN: "ka",  # Georgian (Kartuli)
        Script.CYRILLIC: "ru",  # Russian (for Cyrillic)
    }

    # Check if script is supported
    if source_script not in script_to_lang:
        # Raise exception for MIXED and UNKNOWN scripts
        if source_script in (Script.MIXED, Script.UNKNOWN):
            raise UnsupportedScriptError(text, source_script)
        # For other unsupported scripts, return original text
        return text

    lang_code = script_to_lang[source_script]

    # Verify language pack is available
    available_langs = get_available_language_codes()
    if lang_code not in available_langs:
        # Graceful fallback: return original text
        return text

    try:
        # Transliterate to Latin (reversed=True means from source script to Latin)
        result = translit(text, lang_code, reversed=True)
        return result if result else text
    except Exception:
        # If transliteration fails for any reason, return original text
        # This ensures the library never crashes on unexpected input
        return text
