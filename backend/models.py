from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class AccessTag(str, Enum):
    PUBLIC = "Public"
    INTERNAL = "Internal"
    RESTRICTED = "Restricted"


# Strictness ordering: Restricted (most restrictive) > Internal > Public
ACCESS_TAG_ORDER = {
    AccessTag.PUBLIC: 1,
    AccessTag.INTERNAL: 2,
    AccessTag.RESTRICTED: 3,
}


def merge_access_tags(tags: List[AccessTag]) -> AccessTag:
    """A claim inherits the strictest access tag among its sources."""
    if not tags:
        return AccessTag.RESTRICTED
    return max(tags, key=lambda tag: ACCESS_TAG_ORDER[tag])


class ClaimType(str, Enum):
    DECISION = "Decision"
    OPEN_TASK = "Open task"
    RISK = "Risk"
    DEPENDENCY = "Dependency"
    CONTACT = "Contact"


class EvidenceStatus(str, Enum):
    VERIFIED = "Verified"
    INFERRED = "Inferred"
    CONFLICTING = "Conflicting"
    MISSING = "Missing"
    STATED_BY_LEAVER = "Stated by leaver"


class ReviewStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    EDITED = "Edited"
    REJECTED = "Rejected"


class SourceSnapshot(BaseModel):
    id: str
    filename: str
    content: str
    sha256: str
    access_tag: AccessTag = AccessTag.RESTRICTED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RawClaimCandidate(BaseModel):
    """Raw claim extracted by LLM before deterministic verification."""
    type: ClaimType
    title: str
    description: str
    quote: str
    source_id: str
    owner: Optional[str] = None
    deadline: Optional[str] = None
    status: Optional[str] = None


class Claim(BaseModel):
    id: str
    type: ClaimType
    title: str
    description: str
    quote: str
    source_ids: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    deadline: Optional[str] = None
    status: Optional[str] = None
    evidence_status: EvidenceStatus
    access_tag: AccessTag
    review_status: ReviewStatus = ReviewStatus.PENDING
    risk_score: int = Field(default=0, ge=0, le=100)
    conflict_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReceiverFilterMetadata(BaseModel):
    role: str = "junior_member"
    max_allowed_tag: AccessTag = AccessTag.INTERNAL
    total_claims_in_project: int = 0
    visible_approved_count: int = 0
    restricted_claims_hidden_count: int = 0
    unapproved_claims_hidden_count: int = 0
    restricted_sources_hidden_count: int = 0


class ReceiverHandoverResponse(BaseModel):
    claims: List[Claim]
    filter_metadata: ReceiverFilterMetadata
