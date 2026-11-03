from fastapi.testclient import TestClient
from backend.main import app
from backend.store import store

client = TestClient(app)


def setup_function():
    store.wipe_all()


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_source_upload_and_extraction_flow():
    # 1. Upload source
    upload_res = client.post(
        "/api/sources",
        json={
            "filename": "handover_notes.md",
            "content": "DECISION: Standardize on FastAPI.\nTODO: Deploy DB by Monday.\nCONTACT: Carol Danvers",
            "access_tag": "Internal",
            "consent_confirmed": True,
        },
    )
    assert upload_res.status_code == 200
    snap = upload_res.json()
    assert snap["filename"] == "handover_notes.md"
    assert "sha256" in snap

    # 2. Trigger extraction
    extract_res = client.post("/api/extract")
    assert extract_res.status_code == 200
    claims = extract_res.json()
    assert len(claims) >= 3

    # 3. Check claims list
    list_res = client.get("/api/claims")
    assert len(list_res.json()) >= 3

    # 4. Receiver view before approval must be empty (and return computed server-side filter metadata)
    receiver_res = client.get("/api/receiver/handover")
    assert receiver_res.status_code == 200
    receiver_payload = receiver_res.json()
    assert len(receiver_payload["claims"]) == 0
    assert receiver_payload["filter_metadata"]["unapproved_claims_hidden_count"] >= 3

    # 5. Lead approves claim
    first_claim = claims[0]
    review_res = client.patch(
        f"/api/claims/{first_claim['id']}/review",
        json={
            "review_status": "Approved",
            "reviewer": "AliceLead",
        },
    )
    assert review_res.status_code == 200
    assert review_res.json()["review_status"] == "Approved"

    # 6. Receiver view now contains the approved claim
    receiver_res_after = client.get("/api/receiver/handover")
    after_payload = receiver_res_after.json()
    assert len(after_payload["claims"]) == 1
    assert after_payload["claims"][0]["id"] == first_claim["id"]
    assert after_payload["filter_metadata"]["visible_approved_count"] == 1

    # 7. Test leaver self-approval rejection rule
    if first_claim.get("owner"):
        owner_name = first_claim["owner"]
        self_approve_res = client.patch(
            f"/api/claims/{first_claim['id']}/review",
            json={
                "review_status": "Approved",
                "reviewer": owner_name,
            },
        )
        assert self_approve_res.status_code == 403

    # 8. Test DPDP one-click wipe
    wipe_res = client.delete("/api/project/wipe")
    assert wipe_res.status_code == 200
    assert len(client.get("/api/sources").json()) == 0
    assert len(client.get("/api/claims").json()) == 0
