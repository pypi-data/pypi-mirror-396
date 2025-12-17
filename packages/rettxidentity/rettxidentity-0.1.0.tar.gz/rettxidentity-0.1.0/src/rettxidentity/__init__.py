"""
rettxidentity - Identity Canonicalization and Matching Library

Pure Python library for deterministic identity canonicalization and matching
in the rettX ecosystem. Provides name normalization, script detection,
cross-script transliteration, and identity comparison with explicit match
decisions.
"""

__version__ = "0.1.0"

# Enums
# Canonicalization
from .canonicalize import canonicalize_identity

# Configuration
from .config import MatchOptions, MatchThresholds
from .enums import MatchDecision, ReasonCode, Script

# Errors
from .errors import (
    IdentityError,
    InvalidDateFormat,  # Backward compat
    InvalidDateFormatError,
    MissingRequiredField,  # Backward compat
    MissingRequiredFieldError,
    UnsupportedScript,  # Backward compat
    UnsupportedScriptError,
)

# Matching
from .match import compare_identities

# Models
from .models import (
    CanonicalIdentity,
    Identity,
    MatchResult,
    PersonName,
    ScriptDetection,
    SimilarityScores,
)

# Normalization
from .normalize import normalize_country, normalize_name

# Script detection
from .script import detect_script

# Similarity
from .similarity import calculate_similarity

# Public API
__all__ = [
    "__version__",
    # Enums
    "MatchDecision",
    "ReasonCode",
    "Script",
    # Errors
    "IdentityError",
    "InvalidDateFormatError",
    "MissingRequiredFieldError",
    "UnsupportedScriptError",
    # Backward compatibility aliases
    "InvalidDateFormat",
    "MissingRequiredField",
    "UnsupportedScript",
    # Models
    "Identity",
    "PersonName",
    "CanonicalIdentity",
    "ScriptDetection",
    "SimilarityScores",
    "MatchResult",
    # Configuration
    "MatchOptions",
    "MatchThresholds",
    # Functions
    "detect_script",
    "normalize_name",
    "normalize_country",
    "canonicalize_identity",
    "calculate_similarity",
    "compare_identities",
]
