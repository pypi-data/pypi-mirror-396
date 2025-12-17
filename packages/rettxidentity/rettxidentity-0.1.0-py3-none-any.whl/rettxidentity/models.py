"""
Core data models for rettxidentity library.

All dataclasses are frozen (immutable) for thread-safety and determinism.
"""

from dataclasses import dataclass
from datetime import datetime

from .enums import MatchDecision, ReasonCode, Script
from .errors import InvalidDateFormatError, MissingRequiredFieldError


@dataclass(frozen=True)
class PersonName:
    """
    Immutable person name representation.

    Multiple surnames (e.g., "García López") stored as single string.
    At least one of given or surname must be non-empty.
    """

    given: str | None = None
    surname: str | None = None

    def __post_init__(self) -> None:
        """Validate and normalize whitespace-only strings to None."""
        # Normalize whitespace-only to None
        given_normalized = self.given.strip() if self.given and self.given.strip() else None
        surname_normalized = self.surname.strip() if self.surname and self.surname.strip() else None

        # Update fields using object.__setattr__ (frozen dataclass workaround)
        if given_normalized != self.given:
            object.__setattr__(self, "given", given_normalized)
        if surname_normalized != self.surname:
            object.__setattr__(self, "surname", surname_normalized)

        # Validate at least one component present
        if not self.given and not self.surname:
            raise MissingRequiredFieldError(
                "name", "At least one of given or surname must be provided"
            )


@dataclass(frozen=True)
class Identity:
    """
    Immutable identity representation.

    Identity key (uniqueness): given + surname + date_of_birth + country_of_birth + mutation
    """

    name: PersonName
    date_of_birth: str | None = None
    country_of_birth: str | None = None
    mutation: str | None = None

    def __post_init__(self) -> None:
        """Validate date_of_birth format if provided."""
        if self.date_of_birth:
            # Validate ISO 8601 date format (YYYY-MM-DD)
            try:
                datetime.strptime(self.date_of_birth, "%Y-%m-%d")
            except ValueError as e:
                raise InvalidDateFormatError(
                    self.date_of_birth,
                    f"Invalid date format: {self.date_of_birth}. Expected ISO 8601 (YYYY-MM-DD)",
                ) from e


@dataclass(frozen=True)
class ScriptDetection:
    """Script detection results per name field."""

    given: Script
    surname: Script


@dataclass(frozen=True)
class CanonicalIdentity:
    """
    Immutable canonical identity representation.

    Normalized, versioned representation of a verified identity.
    Same input + version → byte-identical output (deterministic).
    """

    canonicalization_version: str
    name_native_normalized: PersonName
    name_latin_normalized: PersonName
    date_of_birth: str | None
    country_of_birth_normalized: str | None
    mutation: str | None
    scripts_detected: ScriptDetection
    notes: tuple[str, ...] = ()  # Immutable sequence


@dataclass(frozen=True)
class SimilarityScores:
    """Per-field similarity breakdown."""

    given_name: float  # Similarity score for given name (0.0–1.0)
    surname: float  # Similarity score for surname(s) (0.0–1.0)
    overall_name: float  # Combined name similarity
    dob_match: bool | None  # True if DOB matches exactly, None if missing
    country_match: bool | None  # True/False/None (missing)
    mutation_match: bool | None  # True/False/None (missing)


@dataclass(frozen=True)
class MatchResult:
    """
    Immutable match result representation.

    Result of comparing draft and verified identities.
    """

    decision: MatchDecision
    confidence: float  # Overall confidence score (0.0–1.0)
    reason_codes: tuple[ReasonCode, ...]  # Immutable sequence, ≥1 item
    similarity: SimilarityScores
    draft_canonical: CanonicalIdentity
    verified_canonical: CanonicalIdentity
    requires_admin_review: bool
    debug_trace: tuple[str, ...] | None = None
