import pytest
from backend.extractor import (
    extract_candidates_heuristic,
    parse_llm_json_response,
    run_extraction_pipeline,
)
from backend.models import AccessTag, ClaimType, EvidenceStatus, SourceSnapshot


def test_parse_llm_json_response():
    sample_json = """[
        {
            "type": "Decision",
            "title": "Use FastAPI",
            "description": "Selected FastAPI for typed API contracts",
            "quote": "DECISION: Use FastAPI for high performance",
            "owner": null,
            "deadline": null,
            "status": null
        }
    ]"""
    candidates = parse_llm_json_response(sample_json, "src-1")
    assert len(candidates) == 1
    assert candidates[0].type == ClaimType.DECISION
    assert candidates[0].quote == "DECISION: Use FastAPI for high performance"


def test_heuristic_extraction():
    content = (
        "DECISION: Standardize on Next.js App Router for frontend\n"
        "TODO: Complete security audit by Friday\n"
        "RISK: Unmaintained Redis cache connector\n"
        "LEAD: Anandha Lakshmi\n"
    )
    candidates = extract_candidates_heuristic(content, "src-test")
    types = [c.type for c in candidates]
    assert ClaimType.DECISION in types
    assert ClaimType.OPEN_TASK in types
    assert ClaimType.RISK in types
    assert ClaimType.CONTACT in types


@pytest.mark.asyncio
async def test_full_pipeline_glue():
    snap1 = SourceSnapshot(
        id="s1",
        filename="project_notes.md",
        content=(
            "DECISION: Use PostgreSQL database.\n"
            "TODO: Finish user authentication by Friday.\n"
            "CONTACT: Alice Smith\n"
        ),
        sha256="hash-1",
        access_tag=AccessTag.INTERNAL,
    )

    claims = await run_extraction_pipeline({"s1": snap1})
    assert len(claims) >= 3

    # All quotes must be valid substrings in original snapshot
    for claim in claims:
        assert claim.quote in snap1.content
        assert claim.access_tag == AccessTag.INTERNAL
        assert claim.evidence_status in [EvidenceStatus.VERIFIED, EvidenceStatus.MISSING]
