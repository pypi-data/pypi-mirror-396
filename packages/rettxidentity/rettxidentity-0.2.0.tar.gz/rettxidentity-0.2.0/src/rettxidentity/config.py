"""
Configuration types for identity matching.

Includes MatchOptions and MatchThresholds dataclasses.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MatchThresholds:
    """Similarity thresholds for matching decisions."""

    pass_given_name: float = 0.85  # Minimum similarity for given name PASS
    pass_surname: float = 0.90  # Minimum similarity for surname PASS
    pass_overall: float = 0.88  # Minimum overall similarity for PASS
    borderline_min: float = 0.70  # Below this → FAIL


@dataclass(frozen=True)
class MatchOptions:
    """Configuration for identity matching behavior."""

    canonicalization_version: str = "v1"
    transliteration_profile: str = "default_v1"
    require_dob_exact_match: bool = True
    allow_pass_without_dob: bool = False
    enable_order_swap_detection: bool = True
    emit_debug_trace: bool = False
    thresholds: MatchThresholds = field(default_factory=MatchThresholds)
