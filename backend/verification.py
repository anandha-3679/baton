import uuid
from typing import Dict, List, Optional

try:
    from backend.models import (
        AccessTag,
        Claim,
        ClaimType,
        EvidenceStatus,
        RawClaimCandidate,
        ReviewStatus,
        SourceSnapshot,
        merge_access_tags,
    )
except ModuleNotFoundError:
    from models import (
        AccessTag,
        Claim,
        ClaimType,
        EvidenceStatus,
        RawClaimCandidate,
        ReviewStatus,
        SourceSnapshot,
        merge_access_tags,
    )


def verify_quote_in_snapshot(quote: str, snapshot_content: str) -> bool:
    """Check if the extracted quote is an exact or normalized non-empty substring of source content."""
    if not quote or not quote.strip():
        return False
    # Check exact match
    if quote in snapshot_content:
        return True
    # Normalize extra whitespace
    normalized_quote = " ".join(quote.split())
    normalized_content = " ".join(snapshot_content.split())
    return normalized_quote in normalized_content


def verify_contact_in_source(contact_name: Optional[str], snapshot_content: str) -> str:
    """Enforce rule: Names and contacts must appear in the source, otherwise 'No contact found'."""
    if not contact_name or not contact_name.strip():
        return "No contact found"
    clean_name = contact_name.strip()
    if clean_name.lower() in snapshot_content.lower():
        return clean_name
    return "No contact found"


def evaluate_raw_candidate(
    candidate: RawClaimCandidate,
    snapshots: Dict[str, SourceSnapshot],
) -> Optional[Claim]:
    """
    Process raw candidate claim against snapshots.
    Rejects claims with no valid citation / invalid source id.
    Sets evidence status and inherits access tags deterministically.
    """
    snapshot = snapshots.get(candidate.source_id)
    if not snapshot:
        # Rejection: invalid source ID
        return None

    quote_valid = verify_quote_in_snapshot(candidate.quote, snapshot.content)
    if not quote_valid:
        # Rejection: cite does not exist in immutable snapshot
        return None

    # Contact enforcement
    resolved_owner = candidate.owner
    if candidate.type == ClaimType.CONTACT or candidate.owner:
        if candidate.owner:
            resolved_owner = verify_contact_in_source(candidate.owner, snapshot.content)

    # Missing evidence check (e.g. Open tasks missing deadline or owner)
    is_missing_field = False
    if candidate.type == ClaimType.OPEN_TASK:
        if not resolved_owner or resolved_owner == "No contact found" or not candidate.deadline:
            is_missing_field = True

    evidence_status = EvidenceStatus.MISSING if is_missing_field else EvidenceStatus.VERIFIED

    # Risk calculation
    risk_score = 0
    if candidate.type == ClaimType.RISK:
        risk_score += 40
    if is_missing_field:
        risk_score += 30

    return Claim(
        id=str(uuid.uuid4()),
        type=candidate.type,
        title=candidate.title.strip(),
        description=candidate.description.strip(),
        quote=candidate.quote.strip(),
        source_ids=[snapshot.id],
        owner=resolved_owner,
        deadline=candidate.deadline,
        status=candidate.status,
        evidence_status=evidence_status,
        access_tag=snapshot.access_tag,
        review_status=ReviewStatus.PENDING,
        risk_score=min(risk_score, 100),
    )


def detect_and_mark_conflicts(claims: List[Claim], snapshots: Dict[str, SourceSnapshot]) -> List[Claim]:
    """
    Flag claims that disagree on owner, status, or deadline on structured fields.
    Updates evidence status to CONFLICTING and aggregates sources & access tags.
    """
    # Group claims by normalized title & type
    grouped: Dict[str, List[Claim]] = {}
    for c in claims:
        key = f"{c.type.value}:{c.title.strip().lower()}"
        grouped.setdefault(key, []).append(c)

    for key, items in grouped.items():
        if len(items) <= 1:
            continue

        # Check for discrepancies in structured fields
        owners = {c.owner for c in items if c.owner and c.owner != "No contact found"}
        statuses = {c.status.lower() for c in items if c.status}
        deadlines = {c.deadline for c in items if c.deadline}

        has_conflict = len(owners) > 1 or len(statuses) > 1 or len(deadlines) > 1

        if has_conflict:
            conflict_details = []
            if len(owners) > 1:
                conflict_details.append(f"Conflicting owners: {', '.join(sorted(owners))}")
            if len(statuses) > 1:
                conflict_details.append(f"Conflicting statuses: {', '.join(sorted(statuses))}")
            if len(deadlines) > 1:
                conflict_details.append(f"Conflicting deadlines: {', '.join(sorted(deadlines))}")

            conflict_msg = "; ".join(conflict_details)

            # All source tags across conflicting items
            all_source_ids = []
            for item in items:
                all_source_ids.extend(item.source_ids)
            all_source_ids = list(set(all_source_ids))

            source_tags = [snapshots[sid].access_tag for sid in all_source_ids if sid in snapshots]
            strictest_tag = merge_access_tags(source_tags)

            for item in items:
                item.evidence_status = EvidenceStatus.CONFLICTING
                item.conflict_notes = conflict_msg
                item.source_ids = all_source_ids
                item.access_tag = strictest_tag
                item.risk_score = min(item.risk_score + 50, 100)

    return claims


def filter_claims_for_receiver(claims: List[Claim], max_allowed_tag: AccessTag = AccessTag.INTERNAL) -> List[Claim]:
    """
    Receiver view filters:
    1. Must be APPROVED by lead reviewer.
    2. Must respect access tag permissions (never leak Restricted sources).
    """
    allowed_levels = {
        AccessTag.PUBLIC: [AccessTag.PUBLIC],
        AccessTag.INTERNAL: [AccessTag.PUBLIC, AccessTag.INTERNAL],
        AccessTag.RESTRICTED: [AccessTag.PUBLIC, AccessTag.INTERNAL, AccessTag.RESTRICTED],
    }[max_allowed_tag]

    return [
        c for c in claims
        if c.review_status == ReviewStatus.APPROVED and c.access_tag in allowed_levels
    ]
