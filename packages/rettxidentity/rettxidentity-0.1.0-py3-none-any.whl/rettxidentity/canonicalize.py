"""
Identity canonicalization functions.

Provides deterministic canonicalization of verified identities with
normalized names (native and Latin), detected scripts, and versioning.
"""

from .models import CanonicalIdentity, Identity, PersonName, ScriptDetection
from .normalize import normalize_country, normalize_name
from .script import detect_script


def canonicalize_identity(identity: Identity, version: str = "v1") -> CanonicalIdentity:
    """
    Canonicalize an identity to normalized, versioned form.

    Produces a deterministic canonical representation with:
    - Native-normalized names (original script preserved)
    - Latin-normalized names (transliterated + diacritics removed)
    - Detected scripts per name field
    - Normalized country
    - Canonicalization version tag

    Args:
        identity: Input identity to canonicalize
        version: Canonicalization version (default: "v1")

    Returns:
        CanonicalIdentity with normalized fields and detected scripts

    Raises:
        InvalidDateFormat: If date_of_birth is malformed (already validated in Identity)
        MissingRequiredField: If name is completely empty (already validated in Identity)

    Example:
        >>> identity = Identity(
        ...     name=PersonName(given="MARÍA", surname="García"),
        ...     date_of_birth="1985-03-15"
        ... )
        >>> canonical = canonicalize_identity(identity)
        >>> canonical.name_native_normalized
        PersonName(given='maría', surname='garcía')
        >>> canonical.name_latin_normalized
        PersonName(given='maria', surname='garcia')
        >>> canonical.canonicalization_version
        'v1'
    """
    # Detect scripts for given and surname
    given_script = detect_script(identity.name.given) if identity.name.given else detect_script("")
    surname_script = (
        detect_script(identity.name.surname) if identity.name.surname else detect_script("")
    )

    scripts_detected = ScriptDetection(given=given_script, surname=surname_script)

    # Create native-normalized PersonName (preserve script)
    native_given = (
        normalize_name(identity.name.given, preserve_script=True, version=version)
        if identity.name.given
        else None
    )
    native_surname = (
        normalize_name(identity.name.surname, preserve_script=True, version=version)
        if identity.name.surname
        else None
    )
    name_native_normalized = PersonName(given=native_given, surname=native_surname)

    # Create Latin-normalized PersonName (transliterate + remove diacritics)
    latin_given = (
        normalize_name(identity.name.given, preserve_script=False, version=version)
        if identity.name.given
        else None
    )
    latin_surname = (
        normalize_name(identity.name.surname, preserve_script=False, version=version)
        if identity.name.surname
        else None
    )
    name_latin_normalized = PersonName(given=latin_given, surname=latin_surname)

    # Normalize country
    country_normalized = normalize_country(identity.country_of_birth, version=version)

    # date_of_birth and mutation remain unchanged (already validated or None)
    # Identity.__post_init__ validates date format

    return CanonicalIdentity(
        canonicalization_version=version,
        name_native_normalized=name_native_normalized,
        name_latin_normalized=name_latin_normalized,
        date_of_birth=identity.date_of_birth,
        country_of_birth_normalized=country_normalized,
        mutation=identity.mutation,
        scripts_detected=scripts_detected,
        notes=(),  # Empty tuple for now, can be extended later
    )
