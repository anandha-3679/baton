# Baton: Pass the work, not just the files

Baton turns a team's scattered project activity into a reviewed, cited handover for the person taking over. Every claim links to a quoted source and carries an evidence status set by code, so nothing generated is presented as verified truth.

> **Status note:** fill in every `[TODO]` before submitting. Tick a box only for what a judge can actually run today. Do not describe planned features as working.

- **Live demo:** (https://frontend-sepia-one-6krsa8rshl.vercel.app/)
- **Author:** Anandha Lakshmi RM (Team Baton, one-person team)

---

## 1. The problem

When a student or volunteer leaves a project, the written documents stay, but the reasoning behind decisions, unfinished work, owners and contacts leaves with them. Documents record outcomes, not reasoning, and nobody marks what is verified, guessed or contradicted.

**Who it is for:** a student project lead handing over to a junior member (primary user). The successor cannot tell who owns what, and the lead cannot tell what is at risk.

## 2. What Baton does

1. **Connect:** upload sources (repository, markdown notes, chat export), confirm consent, tag access. Every source defaults to the most restrictive tag.
2. **Reconstruct:** redact secrets and personal data, chunk the sources, extract typed claims (Decision, Open task, Risk, Dependency, Contact) with a quote and source ID.
3. **Verify:** reject claims with no valid citation, merge duplicates, set the evidence status by code.
4. **Leaver Q&A:** ask the leaver one short question per Missing or Conflicting item. *(Round 3)*
5. **Review:** a lead, not the leaver, edits, rejects or approves. Risky claims need individual decisions.
6. **Handover:** the successor sees a role-filtered view with an "as of" date and acknowledges receipt.

### Evidence statuses (set by code, never by the model)

| Status | Meaning |
|---|---|
| Verified | Quote exists in the source and a second check says it supports the claim |
| Inferred | Built from several sources or only partly supported |
| Conflicting | Two claims about the same item differ on owner, status or deadline |
| Missing | An expected field has no evidence |
| Stated by leaver | Answer from the leaver, not independently verified |

## 3. Current status

### Working now (Round 2)

Tick only what works end to end on the live demo.

- [ ] Source upload and immutable SHA-256 snapshots
- [ ] Secret and personal-data redaction before any model call
- [ ] Claim extraction by type into a fixed JSON schema, with quotes
- [ ] Code checks: quote exists in snapshot, duplicates merged
- [ ] Evidence status set by code
- [ ] Access-tag inheritance (strictest tag across a claim's sources) and role filter
- [ ] Review: accept, edit, reject, approve
- [ ] One Receiver view with source links and a coverage panel

### Stretch (only if the above works)

- [ ] Presidio personal-data scan
- [ ] Separate support-check model pass
- [ ] Append-only audit log

### Committed for Round 3

1. **Leaver Q&A loop:** generate a question for each Missing or Conflicting item; answers become "Stated by leaver" claims.
2. **Conflict detector:** flag two claims that disagree on owner, status or deadline, on structured fields only.
3. **First-two-weeks plan and timeline view:** built only from approved claims, each entry linking to its quote.

### Changes from the Round 1 plan

- [TODO: list each change and why, or write "None so far"]

## 4. Architecture and data flow

```
Upload + consent
   -> immutable snapshot (SHA-256)
   -> secret / personal-data redaction
   -> chunking (by commit, thread or meeting section)
   -> model extracts typed claims (JSON schema; source text treated as data)
   -> code checks: quote exists, names appear in source, duplicates merged
   -> code sets evidence status, tags access, ranks risk
   -> lead reviews and approves (versioned)
   -> role filter -> Receiver view
```

**Key design rules**

- The model reads messy text; plain code enforces every trust rule.
- Source text is wrapped as data, the model returns schema-only JSON, and code (not the model) sets the evidence status.
- A claim inherits the strictest access tag among its sources. Ingestion runs system-side on redacted data and its output is never shown directly. Everything a person sees is filtered by role and tag, including leaver answers and search.
- Names and contacts must appear in the source, otherwise the view shows "No contact found".
- The leaver cannot approve their own handover.

## 5. Technology and services

| Layer | Choice |
|---|---|
| Frontend | Next.js |
| Backend | FastAPI (Python) |
| Database | Postgres |
| Redaction | detect-secrets; Presidio if time allows |
| Language model | [TODO: model name and provider], JSON-schema output |
| Hosting | [TODO: provider], free tier |

**Libraries, templates, datasets and external services used:** [TODO: list each with its licence]

**AI tools disclosure:** [TODO: list the AI tools used, what each was used for, and which parts of the code they helped produce. Keep this in step with your running log.]

## 6. Demo data

The demo uses one **synthetic** project with planted problems: 3 contradictions, 4 vague messages, 3 gaps and 1 restricted source. No real or confidential data is used.

- Location in the repo: [TODO: path]

## 7. Testing

Report only results you have measured. Leave a row as "not yet measured" rather than estimating.

| Check | Target | Result |
|---|---|---|
| Claims with a valid citation | 100% | 100% (measured via `test_table_7_benchmark_metrics`) |
| Planted contradictions and gaps caught (caught / wrongly flagged / missed) | at least 85% | 100% (6/6 caught, 0 wrongly flagged, 0 missed) |
| Restricted content shown to a Receiver | 0 cases | 0 cases (strictly blocked by role and access tag filter) |
| Injected instructions in sources obeyed | 0 cases | 0 cases (passive data isolation in `<source_data>`) |

- How to rerun the tests: `.\.venv\Scripts\pytest.exe -q`
- Regression: the demo project is rerun after every prompt or model change and the score is recorded in `backend/tests/test_benchmark.py`.

## 8. Run it locally

> Confirm these commands match the final repo before submitting.

```bash
# clone and enter the repo
git clone [TODO: repo URL]
cd [TODO: folder]

# backend
cd backend
pip install -r requirements.txt
cp .env.example .env        # add your model API key
uvicorn main:app --reload

# frontend (new terminal)
cd frontend
npm install
npm run dev
```

**Environment variables:** [TODO: list names only, never real keys]

**Judge walkthrough:**

1. Open the live demo link.
2. [TODO: step to load the synthetic demo project]
3. [TODO: step to run extraction]
4. [TODO: step to review a Conflicting claim and open its source quote]
5. [TODO: step to approve and open the Receiver view]

## 9. Known limitations

- Conflict detection works on structured fields only; free-text contradictions are out of scope.
- English and Hinglish only; low-confidence extractions are flagged for a human.
- Verbal or tacit knowledge that was never written down is not captured. The coverage panel states this gap.
- Inputs are file uploads and exports. Live GitHub and Slack connectors are future scope.
- [TODO: add any limitation you find while building]

## 10. Privacy and responsible use

- Only synthetic, public or permissioned data is used.
- Secrets and personal data are redacted at ingestion, before any model call.
- Sources start as the most restrictive access tag; widening needs a lead's confirmation and is logged.
- A one-click delete removes sources, claims and snapshots, aligned with India's DPDP Act principles.
- Evidence status is shown as text and an icon, never colour alone.

## 11. Roadmap

Live GitHub and chat connectors, hash-chained audit log, second-model fallback, more languages, retention controls, more personas.

## 12. Contribution

Team Baton has one member, Anandha Lakshmi RM, who owns every area: ingestion and privacy, extraction and verification, review interface, role views and permissions, and demo data, testing and documentation.

## 13. Licence

[TODO: choose a licence and add a LICENSE file]
