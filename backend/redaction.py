import hashlib
import re
from typing import Dict, List, Tuple


# Regex patterns for high-risk secrets and PII (API keys, JWT, Passwords, Emails, Phone numbers)
SECRET_PATTERNS = [
    (
        r"(?i)(api[_-]?key|secret[_-]?key|bearer|access[_-]?token)[\s:=]+['\"]?([A-Za-z0-9_\-\.]{16,})['\"]?",
        "[REDACTED_API_KEY]",
    ),
    (r"(?i)(password|passwd|pwd)[\s:=]+['\"]?([^\s'\"]{6,})['\"]?", "[REDACTED_PASSWORD]"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED_EMAIL]"),
    (r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]"),
    (r"ghp_[A-Za-z0-9]{36}", "[REDACTED_GITHUB_TOKEN]"),
    (r"AIza[0-9A-Za-z-_]{35}", "[REDACTED_GOOGLE_API_KEY]"),
]


def redact_secrets_and_pii(text: str) -> Tuple[str, int]:
    """
    Sanitize secrets and personal data before sending to LLM prompt.
    Returns (redacted_text, count_of_redactions).
    """
    redacted_text = text
    total_redactions = 0

    for pattern, replacement in SECRET_PATTERNS:
        matches = list(re.finditer(pattern, redacted_text))
        if matches:
            total_redactions += len(matches)
            redacted_text = re.sub(pattern, replacement, redacted_text)

    return redacted_text, total_redactions


def compute_sha256(content: str) -> str:
    """Compute an immutable SHA-256 hash for snapshot content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def chunk_document(content: str, filename: str, max_chunk_size: int = 1500) -> List[Dict[str, str]]:
    """
    Chunk markdown notes, chats, or code into semantic sections.
    Preserves section headers and logical thread blocks.
    """
    chunks = []
    lines = content.splitlines(keepends=True)
    current_chunk: List[str] = []
    current_length = 0
    chunk_index = 0

    for line in lines:
        line_len = len(line)
        # If markdown header or thread marker is encountered and we have accumulated enough text
        is_boundary = line.strip().startswith(("#", "---", "###", "Thread:", "Date:"))
        if is_boundary and current_length >= max_chunk_size and current_chunk:
            chunk_text = "".join(current_chunk)
            chunks.append({
                "chunk_id": f"{filename}#chunk-{chunk_index}",
                "content": chunk_text,
                "sha256": compute_sha256(chunk_text),
            })
            chunk_index += 1
            current_chunk = []
            current_length = 0

        current_chunk.append(line)
        current_length += line_len

    if current_chunk:
        chunk_text = "".join(current_chunk)
        chunks.append({
            "chunk_id": f"{filename}#chunk-{chunk_index}",
            "content": chunk_text,
            "sha256": compute_sha256(chunk_text),
        })

    return chunks
