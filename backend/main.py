import os
import sys
from typing import List, Optional

# Ensure project root is in sys.path regardless of whether Root Directory is "." or "backend"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from backend.models import AccessTag, Claim, ReceiverHandoverResponse, ReviewStatus, SourceSnapshot
    from backend.store import store
except ModuleNotFoundError:
    from models import AccessTag, Claim, ReceiverHandoverResponse, ReviewStatus, SourceSnapshot
    from store import store

app = FastAPI(
    title="Baton Handover API",
    description="Evidence-backed project handover platform with code-enforced trust",
    version="1.0.0",
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SourceUploadRequest(BaseModel):
    filename: str
    content: str
    access_tag: AccessTag = AccessTag.RESTRICTED
    consent_confirmed: bool = True


class ClaimReviewRequest(BaseModel):
    review_status: ReviewStatus
    reviewer: str
    edited_title: Optional[str] = None
    edited_description: Optional[str] = None


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Baton Backend"}


@app.post("/api/sources", response_model=SourceSnapshot)
def upload_source(request: SourceUploadRequest):
    if not request.consent_confirmed:
        raise HTTPException(status_code=400, detail="Consent must be confirmed prior to source ingestion.")
    snapshot = store.add_source(
        filename=request.filename,
        content=request.content,
        access_tag=request.access_tag,
    )
    return snapshot


@app.get("/api/sources", response_model=List[SourceSnapshot])
def list_sources():
    return list(store.snapshots.values())


@app.post("/api/extract", response_model=List[Claim])
async def trigger_extraction(api_key: Optional[str] = None):
    claims = await store.run_extraction(api_key=api_key)
    return claims


@app.get("/api/claims", response_model=List[Claim])
def list_claims(access_tag: Optional[AccessTag] = None, review_status: Optional[ReviewStatus] = None):
    results = list(store.claims.values())
    if access_tag:
        results = [c for c in results if c.access_tag == access_tag]
    if review_status:
        results = [c for c in results if c.review_status == review_status]
    return results


@app.patch("/api/claims/{claim_id}/review", response_model=Claim)
def review_claim(claim_id: str, req: ClaimReviewRequest):
    try:
        updated = store.update_claim_review(
            claim_id=claim_id,
            review_status=req.review_status,
            reviewer=req.reviewer,
            edited_title=req.edited_title,
            edited_description=req.edited_description,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Claim not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@app.get("/api/receiver/handover", response_model=ReceiverHandoverResponse)
def get_receiver_view(role: str = Query(default="junior_member")):
    # Server-side role & access-tag filtering:
    # Public viewer only sees PUBLIC; junior_member sees PUBLIC & INTERNAL; only lead/admin could see RESTRICTED.
    role_max_tag = {
        "public_viewer": AccessTag.PUBLIC,
        "junior_member": AccessTag.INTERNAL,
        "lead_reviewer": AccessTag.RESTRICTED,
    }.get(role, AccessTag.INTERNAL)

    return store.get_receiver_handover_response(role=role, max_allowed_tag=role_max_tag)


@app.post("/api/project/seed")
def seed_project():
    """Reload the synthetic demo project with pre-approved baseline claims."""
    store.wipe_all()
    store.seed_synthetic_demo()
    return {"message": "Synthetic benchmark seeded with pre-approved baseline claims."}


@app.delete("/api/project/wipe")
def wipe_project():
    """One-click wipe for India DPDP Act compliance."""
    store.wipe_all()
    return {"message": "All sources, snapshots, and extracted claims permanently wiped."}
