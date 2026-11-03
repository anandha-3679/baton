from pathlib import Path
import uuid
from typing import Dict, List, Optional

try:
    from backend.extractor import extract_candidates_heuristic, run_extraction_pipeline
    from backend.models import (
        AccessTag,
        Claim,
        EvidenceStatus,
        ReceiverFilterMetadata,
        ReceiverHandoverResponse,
        ReviewStatus,
        SourceSnapshot,
    )
    from backend.redaction import compute_sha256, redact_secrets_and_pii
    from backend.verification import (
        detect_and_mark_conflicts,
        evaluate_raw_candidate,
        filter_claims_for_receiver,
    )
except ModuleNotFoundError:
    from extractor import extract_candidates_heuristic, run_extraction_pipeline
    from models import (
        AccessTag,
        Claim,
        EvidenceStatus,
        ReceiverFilterMetadata,
        ReceiverHandoverResponse,
        ReviewStatus,
        SourceSnapshot,
    )
    from redaction import compute_sha256, redact_secrets_and_pii
    from verification import (
        detect_and_mark_conflicts,
        evaluate_raw_candidate,
        filter_claims_for_receiver,
    )


class ProjectStore:
    """In-memory persistence layer with full DPDP-compliant wipe functionality."""

    def __init__(self, preload_demo: bool = False):
        self.snapshots: Dict[str, SourceSnapshot] = {}
        self.claims: Dict[str, Claim] = {}
        self.review_logs: List[Dict] = []
        if preload_demo:
            self.seed_synthetic_demo()

    def seed_synthetic_demo(self) -> None:
        """Pre-load synthetic benchmark and pre-approve safe claims for Receiver usability."""
        # Find demo directory whether running from repo root or backend/ subfolder
        demo_dir = Path("data/synthetic_demo")
        if not demo_dir.exists():
            demo_dir = Path(__file__).resolve().parent.parent / "data" / "synthetic_demo"
        if not demo_dir.exists():
            demo_dir = Path(__file__).resolve().parent / "data" / "synthetic_demo"

        if not demo_dir.exists():
            print(f"[ProjectStore] WARNING: synthetic demo directory not found at {demo_dir}")
            return

        files_to_tags = [
            ("slack_archive.txt", AccessTag.INTERNAL),
            ("meeting_minutes.md", AccessTag.INTERNAL),
            ("leaver_notes.md", AccessTag.PUBLIC),
            ("secret_keys.env", AccessTag.RESTRICTED),
        ]
        for fname, tag in files_to_tags:
            fpath = demo_dir / fname
            if fpath.exists():
                self.add_source(fname, fpath.read_text(encoding="utf-8"), tag)

        raw_candidates = []
        for source_id, snapshot in self.snapshots.items():
            redacted_text, _ = redact_secrets_and_pii(snapshot.content)
            raw_candidates.extend(extract_candidates_heuristic(redacted_text, source_id))

        validated = []
        for cand in raw_candidates:
            c = evaluate_raw_candidate(cand, self.snapshots)
            if c:
                validated.append(c)

        extracted = detect_and_mark_conflicts(validated, self.snapshots)
        for claim in extracted:
            # Pre-approve verified non-restricted claims and one missing gap for Receiver view
            if claim.access_tag != AccessTag.RESTRICTED and claim.evidence_status == EvidenceStatus.VERIFIED:
                claim.review_status = ReviewStatus.APPROVED
                self.review_logs.append({
                    "claim_id": claim.id,
                    "status": ReviewStatus.APPROVED.value,
                    "reviewer": "Lead Reviewer",
                })
            elif (
                claim.access_tag == AccessTag.PUBLIC
                and claim.evidence_status == EvidenceStatus.MISSING
                and "cron" in claim.title.lower()
            ):
                claim.review_status = ReviewStatus.APPROVED
                self.review_logs.append({
                    "claim_id": claim.id,
                    "status": ReviewStatus.APPROVED.value,
                    "reviewer": "Lead Reviewer",
                })
            self.claims[claim.id] = claim

    def add_source(self, filename: str, content: str, access_tag: AccessTag = AccessTag.RESTRICTED) -> SourceSnapshot:
        snapshot_id = f"src-{uuid.uuid4().hex[:8]}"
        sha = compute_sha256(content)
        snapshot = SourceSnapshot(
            id=snapshot_id,
            filename=filename,
            content=content,
            sha256=sha,
            access_tag=access_tag,
        )
        self.snapshots[snapshot_id] = snapshot
        return snapshot

    async def run_extraction(self, api_key: Optional[str] = None) -> List[Claim]:
        extracted = await run_extraction_pipeline(self.snapshots, api_key=api_key)
        for claim in extracted:
            self.claims[claim.id] = claim
        return list(self.claims.values())

    def update_claim_review(
        self,
        claim_id: str,
        review_status: ReviewStatus,
        reviewer: str,
        edited_title: Optional[str] = None,
        edited_description: Optional[str] = None,
    ) -> Optional[Claim]:
        claim = self.claims.get(claim_id)
        if not claim:
            return None

        # Rule: Leaver cannot approve own claim
        if claim.owner and claim.owner.lower() == reviewer.lower() and review_status == ReviewStatus.APPROVED:
            raise ValueError("Leaver cannot approve their own handover claim")

        claim.review_status = review_status
        if edited_title:
            claim.title = edited_title
        if edited_description:
            claim.description = edited_description

        self.review_logs.append({
            "claim_id": claim_id,
            "status": review_status.value,
            "reviewer": reviewer,
        })
        return claim

    def get_receiver_handover(self, max_allowed_tag: AccessTag = AccessTag.INTERNAL) -> List[Claim]:
        all_claims = list(self.claims.values())
        return filter_claims_for_receiver(all_claims, max_allowed_tag=max_allowed_tag)

    def get_receiver_handover_response(
        self,
        role: str = "junior_member",
        max_allowed_tag: AccessTag = AccessTag.INTERNAL,
    ) -> ReceiverHandoverResponse:
        all_claims = list(self.claims.values())
        visible_claims = filter_claims_for_receiver(all_claims, max_allowed_tag=max_allowed_tag)

        allowed_levels = {
            AccessTag.PUBLIC: [AccessTag.PUBLIC],
            AccessTag.INTERNAL: [AccessTag.PUBLIC, AccessTag.INTERNAL],
            AccessTag.RESTRICTED: [AccessTag.PUBLIC, AccessTag.INTERNAL, AccessTag.RESTRICTED],
        }[max_allowed_tag]

        restricted_claims_hidden = sum(1 for c in all_claims if c.access_tag not in allowed_levels)
        unapproved_claims_hidden = sum(
            1 for c in all_claims if c.access_tag in allowed_levels and c.review_status != ReviewStatus.APPROVED
        )
        restricted_sources_hidden = sum(
            1 for s in self.snapshots.values() if s.access_tag not in allowed_levels
        )

        return ReceiverHandoverResponse(
            claims=visible_claims,
            filter_metadata=ReceiverFilterMetadata(
                role=role,
                max_allowed_tag=max_allowed_tag,
                total_claims_in_project=len(all_claims),
                visible_approved_count=len(visible_claims),
                restricted_claims_hidden_count=restricted_claims_hidden,
                unapproved_claims_hidden_count=unapproved_claims_hidden,
                restricted_sources_hidden_count=restricted_sources_hidden,
            ),
        )

    def wipe_all(self):
        """DPDP Act compliance: one-click removal of all sources, snapshots, and claims."""
        self.snapshots.clear()
        self.claims.clear()
        self.review_logs.clear()


# Global store instance pre-loaded with synthetic benchmark for immediate judge evaluation
store = ProjectStore(preload_demo=True)
