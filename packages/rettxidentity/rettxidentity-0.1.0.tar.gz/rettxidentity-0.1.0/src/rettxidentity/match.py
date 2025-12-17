"""
Identity matching and comparison logic.

Implements the gate system for identity comparison with explicit match decisions.
"""

from .canonicalize import canonicalize_identity
from .config import MatchOptions, MatchThresholds
from .enums import MatchDecision, ReasonCode
from .models import (
    CanonicalIdentity,
    Identity,
    MatchResult,
    SimilarityScores,
)
from .similarity import calculate_similarity


def compare_identities(
    draft: Identity,
    verified: Identity,
    options: MatchOptions | None = None,
) -> MatchResult:
    """
    Compare a draft identity against a verified identity and return match result.

    Implements tiered gate system:
    1. Hard gates (DOB, mutation) - must pass
    2. Soft gates (country, name similarity) - influence score

    Args:
        draft: Identity entered by caregiver (may contain spelling variations)
        verified: Identity from official medical documentation
        options: Matching configuration (uses defaults if None)

    Returns:
        MatchResult with decision (PASS/BORDERLINE/FAIL), confidence score,
        reason codes, and canonical representations of both identities

    Raises:
        InvalidDateFormat: If date_of_birth is malformed in either identity
        MissingRequiredField: If name is completely empty in either identity

    Example:
        >>> draft = Identity(
        ...     name=PersonName(given="Maria", surname="Garcia"),
        ...     date_of_birth="1985-03-15",
        ...     country_of_birth="ES"
        ... )
        >>> verified = Identity(
        ...     name=PersonName(given="María", surname="García López"),
        ...     date_of_birth="1985-03-15",
        ...     country_of_birth="Spain"
        ... )
        >>> result = compare_identities(draft, verified)
        >>> result.decision
        <MatchDecision.PASS: 'PASS'>
    """
    # Use default options if none provided
    if options is None:
        options = MatchOptions()

    debug_trace: list[str] | None = [] if options.emit_debug_trace else None

    # Canonicalize both identities
    draft_canonical = canonicalize_identity(draft, version=options.canonicalization_version)
    verified_canonical = canonicalize_identity(verified, version=options.canonicalization_version)

    if debug_trace is not None:
        debug_trace.append("Canonicalized draft and verified identities")

    reason_codes: list[ReasonCode] = []

    # --- GATE 1: Date of Birth (Hard Gate) ---
    dob_match = _check_dob_match(draft, verified, options, reason_codes, debug_trace)

    if dob_match is False:
        # DOB mismatch is immediate FAIL
        if debug_trace is not None:
            debug_trace.append("FAIL: DOB mismatch (hard gate)")

        # Still need to calculate similarities for reporting
        similarity = _calculate_name_similarity(
            draft_canonical, verified_canonical, options, reason_codes, debug_trace
        )

        return MatchResult(
            decision=MatchDecision.FAIL,
            confidence=0.0,
            reason_codes=tuple(reason_codes),
            similarity=similarity,
            draft_canonical=draft_canonical,
            verified_canonical=verified_canonical,
            requires_admin_review=False,
            debug_trace=tuple(debug_trace) if debug_trace is not None else None,
        )

    # --- GATE 2: Mutation (Conditional Hard Gate) ---
    mutation_match = _check_mutation_match(draft, verified, reason_codes, debug_trace)

    if mutation_match is False:
        # Mutation mismatch (when both present) is immediate FAIL
        if debug_trace is not None:
            debug_trace.append("FAIL: Mutation mismatch (hard gate)")

        similarity = _calculate_name_similarity(
            draft_canonical, verified_canonical, options, reason_codes, debug_trace
        )

        return MatchResult(
            decision=MatchDecision.FAIL,
            confidence=0.0,
            reason_codes=tuple(reason_codes),
            similarity=similarity,
            draft_canonical=draft_canonical,
            verified_canonical=verified_canonical,
            requires_admin_review=False,
            debug_trace=tuple(debug_trace) if debug_trace is not None else None,
        )

    # --- GATE 3: Country (Soft Gate) ---
    country_match = _check_country_match(
        draft_canonical, verified_canonical, reason_codes, debug_trace
    )

    # --- GATE 4: Name Similarity (Soft Gate) ---
    similarity = _calculate_name_similarity(
        draft_canonical, verified_canonical, options, reason_codes, debug_trace
    )

    # --- Calculate Confidence Score ---
    confidence = _calculate_confidence(
        dob_match, mutation_match, country_match, similarity.overall_name, options.thresholds
    )

    # --- Determine Final Decision ---
    decision = _determine_decision(
        similarity.overall_name,
        country_match,
        dob_match,
        mutation_match,
        options.thresholds,
        reason_codes,
        debug_trace,
    )

    requires_admin_review = decision == MatchDecision.BORDERLINE

    return MatchResult(
        decision=decision,
        confidence=confidence,
        reason_codes=tuple(reason_codes),
        similarity=similarity,
        draft_canonical=draft_canonical,
        verified_canonical=verified_canonical,
        requires_admin_review=requires_admin_review,
        debug_trace=tuple(debug_trace) if debug_trace is not None else None,
    )


def _check_dob_match(
    draft: Identity,
    verified: Identity,
    options: MatchOptions,
    reason_codes: list[ReasonCode],
    debug_trace: list[str] | None,
) -> bool | None:
    """Check DOB match. Returns True/False/None (missing)."""
    if draft.date_of_birth and verified.date_of_birth:
        if draft.date_of_birth == verified.date_of_birth:
            reason_codes.append(ReasonCode.DOB_EXACT_MATCH)
            if debug_trace is not None:
                debug_trace.append("DOB: Exact match")
            return True
        else:
            reason_codes.append(ReasonCode.DOB_MISMATCH)
            if debug_trace is not None:
                debug_trace.append("DOB: Mismatch (hard gate failure)")
            return False
    else:
        reason_codes.append(ReasonCode.DOB_MISSING)
        if debug_trace is not None:
            debug_trace.append("DOB: Missing in one or both identities")
        return None


def _check_mutation_match(
    draft: Identity,
    verified: Identity,
    reason_codes: list[ReasonCode],
    debug_trace: list[str] | None,
) -> bool | None:
    """Check mutation match. Returns True/False/None (missing)."""
    if draft.mutation and verified.mutation:
        if draft.mutation == verified.mutation:
            reason_codes.append(ReasonCode.MUTATION_EXACT_MATCH)
            if debug_trace is not None:
                debug_trace.append("Mutation: Exact match")
            return True
        else:
            reason_codes.append(ReasonCode.MUTATION_MISMATCH)
            if debug_trace is not None:
                debug_trace.append("Mutation: Mismatch (hard gate failure)")
            return False
    else:
        reason_codes.append(ReasonCode.MUTATION_MISSING)
        if debug_trace is not None:
            debug_trace.append("Mutation: Missing in one or both identities (allowed)")
        return None


def _check_country_match(
    draft_canonical: CanonicalIdentity,
    verified_canonical: CanonicalIdentity,
    reason_codes: list[ReasonCode],
    debug_trace: list[str] | None,
) -> bool | None:
    """Check country match. Returns True/False/None (missing)."""
    if (
        draft_canonical.country_of_birth_normalized
        and verified_canonical.country_of_birth_normalized
    ):
        if (
            draft_canonical.country_of_birth_normalized
            == verified_canonical.country_of_birth_normalized
        ):
            reason_codes.append(ReasonCode.COUNTRY_EXACT_MATCH)
            if debug_trace is not None:
                debug_trace.append("Country: Exact match")
            return True
        else:
            reason_codes.append(ReasonCode.COUNTRY_MISMATCH)
            if debug_trace is not None:
                debug_trace.append("Country: Mismatch (caps decision at BORDERLINE)")
            return False
    else:
        reason_codes.append(ReasonCode.COUNTRY_MISSING)
        if debug_trace is not None:
            debug_trace.append("Country: Missing in one or both identities")
        return None


def _calculate_name_similarity(
    draft_canonical: CanonicalIdentity,
    verified_canonical: CanonicalIdentity,
    options: MatchOptions,
    reason_codes: list[ReasonCode],
    debug_trace: list[str] | None,
) -> SimilarityScores:
    """Calculate name similarity scores."""
    # Use Latin-normalized forms for comparison
    draft_given = draft_canonical.name_latin_normalized.given or ""
    draft_surname = draft_canonical.name_latin_normalized.surname or ""
    verified_given = verified_canonical.name_latin_normalized.given or ""
    verified_surname = verified_canonical.name_latin_normalized.surname or ""

    # Calculate component similarities
    given_similarity = calculate_similarity(draft_given, verified_given, normalize=False)
    surname_similarity = calculate_similarity(draft_surname, verified_surname, normalize=False)

    if debug_trace is not None:
        debug_trace.append(f"Given name similarity: {given_similarity:.2f}")
        debug_trace.append(f"Surname similarity: {surname_similarity:.2f}")

    # Calculate overall name similarity (weighted average)
    # Give more weight to surname (60%) vs given (40%)
    overall_similarity = (given_similarity * 0.4) + (surname_similarity * 0.6)

    if debug_trace is not None:
        debug_trace.append(f"Overall name similarity: {overall_similarity:.2f}")

    # Add reason codes based on similarity
    if given_similarity >= options.thresholds.pass_given_name:
        if given_similarity == 1.0:
            if ReasonCode.NAME_EXACT_MATCH not in reason_codes:
                reason_codes.append(ReasonCode.NAME_EXACT_MATCH)
        else:
            if ReasonCode.NAME_MATCH_AFTER_NORMALIZATION not in reason_codes:
                reason_codes.append(ReasonCode.NAME_MATCH_AFTER_NORMALIZATION)
    elif given_similarity < options.thresholds.borderline_min:
        reason_codes.append(ReasonCode.NAME_LOW_SIMILARITY_GIVEN)

    if surname_similarity < options.thresholds.borderline_min:
        reason_codes.append(ReasonCode.NAME_LOW_SIMILARITY_SURNAME)

    # Create similarity scores object
    # Note: dob_match, country_match, mutation_match will be filled by caller
    return SimilarityScores(
        given_name=given_similarity,
        surname=surname_similarity,
        overall_name=overall_similarity,
        dob_match=None,  # Will be filled by caller
        country_match=None,  # Will be filled by caller
        mutation_match=None,  # Will be filled by caller
    )


def _calculate_confidence(
    dob_matches: bool | None,
    mutation_matches: bool | None,
    country_matches: bool | None,
    name_similarity: float,
    thresholds: MatchThresholds,
) -> float:
    """
    Calculate overall confidence score.

    Base is name_similarity (0.0-1.0).
    Modifiers applied for other factors.
    """
    confidence = name_similarity

    # DOB bonus/penalty
    if dob_matches is True:
        confidence += 0.05
    elif dob_matches is None:
        confidence -= 0.03  # Missing DOB slight penalty

    # Mutation bonus
    if mutation_matches is True:
        confidence += 0.03
    # Missing mutation: no penalty (clinical diagnosis allowed)

    # Country bonus/penalty
    if country_matches is True:
        confidence += 0.02
    elif country_matches is False:
        confidence -= 0.05  # Mismatch penalty (but not FAIL)

    return min(1.0, max(0.0, confidence))


def _determine_decision(
    overall_name_similarity: float,
    country_match: bool | None,
    dob_match: bool | None,
    mutation_match: bool | None,
    thresholds: MatchThresholds,
    reason_codes: list[ReasonCode],
    debug_trace: list[str] | None,
) -> MatchDecision:
    """Determine final match decision based on all factors."""
    # Country mismatch caps at BORDERLINE
    if country_match is False:
        if debug_trace is not None:
            debug_trace.append("Decision: BORDERLINE (country mismatch)")
        reason_codes.append(ReasonCode.BORDERLINE_REVIEW_REQUIRED)
        return MatchDecision.BORDERLINE

    # Missing DOB or mutation triggers BORDERLINE
    if dob_match is None or mutation_match is None:
        if debug_trace is not None:
            debug_trace.append("Decision: BORDERLINE (missing DOB or mutation)")
        reason_codes.append(ReasonCode.BORDERLINE_REVIEW_REQUIRED)
        return MatchDecision.BORDERLINE

    # Name similarity thresholds
    if overall_name_similarity >= thresholds.pass_overall:
        if debug_trace is not None:
            debug_trace.append("Decision: PASS (all gates passed)")
        return MatchDecision.PASS
    elif overall_name_similarity >= thresholds.borderline_min:
        if debug_trace is not None:
            debug_trace.append("Decision: BORDERLINE (name similarity in borderline range)")
        reason_codes.append(ReasonCode.BORDERLINE_REVIEW_REQUIRED)
        return MatchDecision.BORDERLINE
    else:
        if debug_trace is not None:
            debug_trace.append("Decision: FAIL (name similarity below threshold)")
        return MatchDecision.FAIL
