from backend.redaction import chunk_document, compute_sha256, redact_secrets_and_pii


def test_redact_secrets_and_pii():
    sample_text = (
        "Server config:\n"
        "api_key = 'AIzaSyD-EXAMPLE_KEY_12345678901234567'\n"
        "admin password: SecretPassword123!\n"
        "Contact me at alice.smith@organization.org or call 415-555-2671.\n"
        "Github token: ghp_123456789012345678901234567890123456\n"
    )

    redacted, count = redact_secrets_and_pii(sample_text)
    assert count >= 4
    assert "SecretPassword123!" not in redacted
    assert "AIzaSyD-EXAMPLE_KEY" not in redacted
    assert "alice.smith@organization.org" not in redacted
    assert "415-555-2671" not in redacted
    assert "ghp_1234567890" not in redacted

    assert "[REDACTED_PASSWORD]" in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_PHONE]" in redacted


def test_compute_sha256():
    c1 = "Immutable document content"
    c2 = "Immutable document content"
    c3 = "Tampered document content"

    hash1 = compute_sha256(c1)
    hash2 = compute_sha256(c2)
    hash3 = compute_sha256(c3)

    assert hash1 == hash2
    assert hash1 != hash3
    assert len(hash1) == 64


def test_chunk_document():
    long_content = (
        "# Section 1\n" + ("Text paragraph line.\n" * 50) +
        "# Section 2\n" + ("Another text line.\n" * 50)
    )

    chunks = chunk_document(long_content, "test.md", max_chunk_size=500)
    assert len(chunks) >= 2
    assert chunks[0]["chunk_id"].startswith("test.md#chunk-")
    assert "sha256" in chunks[0]
    assert len(chunks[0]["sha256"]) == 64
