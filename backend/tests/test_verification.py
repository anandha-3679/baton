from backend.models import (
    AccessTag,
    ClaimType,
    EvidenceStatus,
    RawClaimCandidate,
    ReviewStatus,
    SourceSnapshot,
    merge_access_tags,
)
from backend.verification import (
    detect_and_mark_conflicts,
    evaluate_raw_candidate,
    filter_claims_for_receiver,
    verify_contact_in_source,
    verify_quote_in_snapshot,
)


def test_quote_verification():
    content = "The authentication service must be migrated to OAuth2 by end of Q2."
    assert verify_quote_in_snapshot("OAuth2 by end of Q2", content)
    assert verify_quote_in_snapshot("  authentication   service  ", content)
    assert not verify_quote_in_snapshot("Fabricated quote not in text", content)
    assert not verify_quote_in_snapshot("", content)


def test_contact_enforcement():
    source = "Project Handover meeting notes. Lead: Alice Smith. Contact: alice@example.com."
    assert verify_contact_in_source("Alice Smith", source) == "Alice Smith"
    assert verify_contact_in_source("Bob Jones", source) == "No contact found"
    assert verify_contact_in_source(None, source) == "No contact found"


def test_evaluate_raw_candidate_rejection():
    snapshot = SourceSnapshot(
        id="src-1",
        filename="notes.md",
        content="Migrate DB to Postgres by Friday.",
        sha256="dummyhash",
        access_tag=AccessTag.INTERNAL,
    )
    snapshots = {snapshot.id: snapshot}

    # Valid candidate
    valid_cand = RawClaimCandidate(
        type=ClaimType.OPEN_TASK,
        title="Migrate DB",
        description="Database migration",
        quote="Migrate DB to Postgres",
        source_id="src-1",
        owner=None,
        deadline="Friday",
    )
    claim = evaluate_raw_candidate(valid_cand, snapshots)
    assert claim is not None
    assert claim.evidence_status == EvidenceStatus.MISSING  # missing owner

    # Fabricated citation candidate -> must be rejected (return None)
    invalid_cand = RawClaimCandidate(
        type=ClaimType.DECISION,
        title="Fake Decision",
        description="Not backed by source",
        quote="This quote does not exist in snapshot",
        source_id="src-1",
    )
    rejected_claim = evaluate_raw_candidate(invalid_cand, snapshots)
    assert rejected_claim is None


def test_access_tag_inheritance():
    tags = [AccessTag.PUBLIC, AccessTag.RESTRICTED, AccessTag.INTERNAL]
    assert merge_access_tags(tags) == AccessTag.RESTRICTED
    assert merge_access_tags([AccessTag.PUBLIC, AccessTag.INTERNAL]) == AccessTag.INTERNAL


def test_detect_and_mark_conflicts():
    snap1 = SourceSnapshot(
        id="s1",
        filename="chat.txt",
        content="Alice owns auth refactoring. Deadline is May 1.",
        sha256="hash1",
        access_tag=AccessTag.INTERNAL,
    )
    snap2 = SourceSnapshot(
        id="s2",
        filename="meeting.md",
        content="Bob owns auth refactoring. Deadline is May 15.",
        sha256="hash2",
        access_tag=AccessTag.RESTRICTED,
    )
    snapshots = {"s1": snap1, "s2": snap2}

    cand1 = RawClaimCandidate(
        type=ClaimType.OPEN_TASK,
        title="Auth refactoring",
        description="Refactor auth",
        quote="Alice owns auth refactoring",
        source_id="s1",
        owner="Alice",
        deadline="May 1",
    )
    cand2 = RawClaimCandidate(
        type=ClaimType.OPEN_TASK,
        title="Auth refactoring",
        description="Refactor auth",
        quote="Bob owns auth refactoring",
        source_id="s2",
        owner="Bob",
        deadline="May 15",
    )

    c1 = evaluate_raw_candidate(cand1, snapshots)
    c2 = evaluate_raw_candidate(cand2, snapshots)
    assert c1 is not None and c2 is not None

    processed = detect_and_mark_conflicts([c1, c2], snapshots)
    assert processed[0].evidence_status == EvidenceStatus.CONFLICTING
    assert processed[1].evidence_status == EvidenceStatus.CONFLICTING
    assert processed[0].access_tag == AccessTag.RESTRICTED
    assert "Conflicting owners" in processed[0].conflict_notes


def test_receiver_view_protection():
    c_approved_pub = evaluate_raw_candidate(
        RawClaimCandidate(
            type=ClaimType.DECISION,
            title="Public Architecture",
            description="Use Next.js",
            quote="Use Next.js",
            source_id="s1",
        ),
        {"s1": SourceSnapshot(id="s1", filename="f1", content="Use Next.js", sha256="h", access_tag=AccessTag.PUBLIC)},
    )
    c_approved_pub.review_status = ReviewStatus.APPROVED

    c_restricted = evaluate_raw_candidate(
        RawClaimCandidate(
            type=ClaimType.DECISION,
            title="Secret Keys",
            description="Keys stored in vault",
            quote="Keys stored in vault",
            source_id="s2",
        ),
        {"s2": SourceSnapshot(
            id="s2",
            filename="f2",
            content="Keys stored in vault",
            sha256="h2",
            access_tag=AccessTag.RESTRICTED,
        )},
    )
    c_restricted.review_status = ReviewStatus.APPROVED

    c_pending = evaluate_raw_candidate(
        RawClaimCandidate(
            type=ClaimType.OPEN_TASK,
            title="Task",
            description="Pending task",
            quote="Pending task",
            source_id="s1",
        ),
        {"s1": SourceSnapshot(id="s1", filename="f1", content="Pending task", sha256="h", access_tag=AccessTag.PUBLIC)},
    )

    filtered = filter_claims_for_receiver([c_approved_pub, c_restricted, c_pending], max_allowed_tag=AccessTag.INTERNAL)
    # Must only include approved items with access tag <= Internal (no restricted content leak, no unapproved content)
    assert len(filtered) == 1
    assert filtered[0].title == "Public Architecture"
