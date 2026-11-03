# Scratchpad: Baton Implementation Roadmap & Order of Build

Based on [README.md](file:///c:/Users/Anandha%20Lakshmi/baton/README.md) requirements, architecture, judge walkthrough, and Round 2 commitments.

---

## 1. Golden Architectural Principles (Non-Negotiable)
1. **Plain code enforces trust**: The LLM *only* extracts raw JSON candidates with quotes. Verification, quote checking, deduplication, conflict detection, access tag propagation, and evidence statuses (`Verified`, `Inferred`, `Conflicting`, `Missing`, `Stated by leaver`) must be executed strictly in deterministic Python code.
2. **Privacy first**: Redact secrets (`detect-secrets`) and PII *before* any text reaches an LLM prompt.
3. **Immutable snapshots**: SHA-256 hash source content upon ingest; claims must quote exact substrings in that snapshot.
4. **Access tags & role filtering**: A claim inherits the strictest access tag among its sources. The Receiver view must never leak restricted source content.

---

## 2. Recommended Order of Build

```
Phase 0: Workspace & Scaffolding
   ↓
Phase 1: Domain Core & Code-Only Trust Engine (Deterministic Unit Tests)
   ↓
Phase 2: Ingestion & Privacy Redaction Pipeline
   ↓
Phase 3: LLM Extraction Layer (Structured Output / JSON Schema)
   ↓
Phase 4: FastAPI REST API & Storage Layer
   ↓
Phase 5: Next.js Frontend (Reviewer & Receiver Portals)
   ↓
Phase 6: Synthetic Benchmark Dataset & Automated Evaluation
```

---

### Phase 0: Workspace & Directory Scaffolding (COMPLETED)
- [x] Set up monorepo directory layout:
  - `backend/` (FastAPI, Pydantic v2, Ruff, Pytest in `.venv`)
  - `frontend/` (Next.js App Router, TypeScript, ESLint)
  - `data/synthetic_demo/` (Setup with `README.md` specification)
- [x] Establish environment configuration (`.env.example`).
- [x] Baseline lint and test commands verified (`pytest -q`, `npm --prefix frontend run lint`).

---

### Phase 1: Core Domain Schemas & Deterministic Verification Rules (Python) (COMPLETED)
- [x] **Pydantic Models** (`backend/models.py`):
  - `SourceSnapshot`: `id`, `filename`, `content`, `sha256`, `access_tag` (`Public`, `Internal`, `Restricted`), `created_at`.
  - `RawClaimCandidate` & `Claim`: `id`, `type`, `title`, `description`, `quote`, `source_ids`, `owner`, `deadline`, `status`, `evidence_status`, `access_tag`, `review_status`, `risk_score`.
- [x] **Deterministic Rules Engine** (`backend/verification.py`):
  - `verify_quote_in_snapshot`: Exact and normalized substring match. Rejects ungrounded or fabricated quotes.
  - `verify_contact_in_source`: Ensures names appear in source; otherwise defaults to `"No contact found"`.
  - `merge_access_tags`: Strictness hierarchy (`Restricted` > `Internal` > `Public`).
  - `evaluate_raw_candidate`: Deterministically sets evidence status (`Verified` vs `Missing`) and rejects invalid citations.
  - `detect_and_mark_conflicts`: Detects structured contradictions across owners, statuses, and deadlines; sets `Conflicting` status and strictly propagates access tags.
  - `filter_claims_for_receiver`: Ensures no unapproved or restricted claims leak to the receiver view.
- [x] **Unit Test Suite & Linting**:
  - `backend/tests/test_verification.py`: 6/6 tests passing via `pytest -q`.
  - `ruff check backend`: Clean.

---

### Phase 2: Ingestion & Redaction Pipeline (COMPLETED)
- [x] **Secret & PII Redactor** (`backend/redaction.py`):
  - Sanitization of high-risk secrets (API keys, GitHub tokens, Google API keys, passwords) and PII (emails, phone numbers) before any prompt injection.
  - Verified with test cases ensuring secrets never leak into LLM prompts.
- [x] **Snapshot Storage & Chunking** (`backend/redaction.py`):
  - Deterministic SHA-256 computation (`compute_sha256`) for immutable snapshot verification.
  - Semantic section and boundary chunking (`chunk_document`) with chunk-level SHA-256 hashes.
- [x] **Unit Test Suite**:
  - `backend/tests/test_redaction.py`: 3/3 tests passing (9/9 total tests passing via `pytest -q`).
  - `ruff check backend`: Clean.

---

### Phase 3: LLM Extraction Layer (COMPLETED)
- [x] **JSON Schema Prompt Engine** (`backend/extractor.py`):
  - System prompt enforcing pure JSON array of claims (`Decision`, `Open task`, `Risk`, `Dependency`, `Contact`).
  - Strict isolation: raw source texts isolated within `<source_data>` tags to prevent prompt injection attacks.
  - Strict verbatim quote enforcement.
  - LLM client with fallback to deterministic heuristic extractor when offline or without API key.
- [x] **Pipeline Glue** (`backend/extractor.py`):
  - `run_extraction_pipeline`: Ingest snapshots → Redact secrets/PII → Extract claims → Deterministic code verification → Detect & mark conflicts → Inherit strict access tags.
- [x] **Unit Tests & Linting**:
  - `backend/tests/test_extractor.py`: Schema parsing, heuristic extraction, and end-to-end extraction pipeline glue tests.
  - `pytest -q`: 12/12 tests passing.
  - `ruff check backend`: Clean.

---

### Phase 4: Backend REST API (FastAPI) (COMPLETED)
- [x] `POST /api/sources`: Upload sources with consent validation, SHA-256 snapshotting, and access tagging.
- [x] `GET /api/sources`: List immutable snapshots.
- [x] `POST /api/extract`: Trigger end-to-end extraction and code verification pipeline.
- [x] `GET /api/claims`: Query claims with access tag and review status filters.
- [x] `PATCH /api/claims/{id}/review`: Reviewer approval, edits, and rejection. Enforces rule: leaver cannot approve own claim.
- [x] `GET /api/receiver/handover`: Secure receiver endpoint (role/tag filtered, approved-only).
- [x] `DELETE /api/project/wipe`: One-click DPDP Act compliance wipe.
- [x] **Unit & Integration Tests**:
  - `backend/tests/test_api.py`: Full API upload, extraction, review, receiver protection, and wipe flow.
  - `pytest -q`: 14/14 tests passing.
  - `ruff check backend`: Clean.

---

### Phase 5: Next.js Frontend (COMPLETED)
- [x] **Shared Layout & Design System**:
  - Curated tokens and variables in `frontend/src/app/globals.css`.
  - Accessible badges for Evidence Status, Access Tags, and Claim Types (`frontend/src/components/Badges.tsx`).
- [x] **Lead Review Portal** (`frontend/src/components/ReviewPortal.tsx` & `SourceUploader.tsx`):
  - Ingestion & consent widget with access tag selector and preloaded synthetic benchmark.
  - Side-by-side quote inspector comparing claim details directly with verbatim quoted sources.
  - Conflict warning banner showing contradictory claims flagged by deterministic code.
  - One-click approve/edit/reject workflow with leaver self-approval rejection feedback.
- [x] **Receiver Portal** (`frontend/src/components/ReceiverView.tsx`):
  - Filtered by role; only approved items with access tags &le; Internal visible (zero restricted leaks).
  - Coverage panel detailing verified facts, partially inferred claims, and unrecorded tacit gaps.
  - Handover receipt acknowledgment button.
- [x] **Production Verification**:
  - TypeScript compilation and Next.js Turbopack build passed cleanly (`npm run build`).
  - ESLint verified.

---

### Phase 6: Synthetic Demo Data & Automated Evaluation Suite (COMPLETED)
- [x] Populate `data/synthetic_demo/`:
  - `slack_archive.txt`: Planted contradiction (database migration owned by Alice by May 10), prompt injection attack attempt, and vague task.
  - `meeting_minutes.md`: Planted contradiction (database migration owned by Bob by May 25), and vague performance task.
  - `leaver_notes.md`: Unassigned tacit tasks with missing owners/deadlines, plus unrecorded risk.
  - `secret_keys.env`: Restricted document with API keys and root admin password.
- [x] Automated Evaluation Suite (`backend/tests/test_benchmark.py`):
  - 100% Citation validity verified against immutable snapshot text.
  - Planted contradictions and gaps caught: 100% (6/6 anomalies caught).
  - Restricted content shown to receiver: 0 cases leaked.
  - Injected instructions obeyed: 0 cases (passive data isolation).
- [x] Recorded measured test outcomes directly in `README.md` (Table 7).
- [x] Verification: `pytest -q` passing 15/15 tests, Ruff checks clean.

---

### Phase 7: Judge Usability & Audit Refinements (COMPLETED)
- [x] **1. Empty receiver view**: Pre-loaded the synthetic demo with baseline approved claims on server startup (`ProjectStore(preload_demo=True)` & `POST /api/project/seed`) and added a clear “Judge Quick Guide” banner + empty-state workflow guide.
- [x] **2. “Zero restricted sources leaked” must be computed**: Replaced hardcoded text with live server-computed counts (`restricted_claims_hidden_count`, `restricted_sources_hidden_count`, `unapproved_claims_hidden_count`) in `ReceiverHandoverResponse`.
- [x] **3. Filtering must be server-side**: `GET /api/receiver/handover` filters strictly by `role` and `max_allowed_tag` on the server before responding and returns `ReceiverFilterMetadata`.
- [x] **4. Evidence status vs approval status**: Updated badges to explicitly display `Evidence: Verified` and `Review: Pending` (`ReviewStatusBadge`), and labeled task progress separately as `Task Progress`.
- [x] **5. Quote inspector**: Updated `ReviewPortal.tsx` to display the full source snapshot(s) with the verbatim quote highlighted (`<mark>`) inside the surrounding source text.
