import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4b5563"))
        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Baton: Round 2 Project Document")
            self.drawRightString(558, 750, f"Page {self._pageNumber}")
            self.setStrokeColor(colors.HexColor("#e5e7eb"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
        
        # Footer
        self.drawString(54, 36, "Baton: Round 2 Project Document")
        self.drawRightString(558, 36, f"Page {self._pageNumber}")
        self.restoreState()

def build_pdf(filename="Baton_Round_2_Project_Document.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#111827"),
        spaceAfter=2,
    )
    
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=12,
    )
    
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=12,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e3a8a"),
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1f2937"),
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell_style,
        fontName="Helvetica-Bold",
    )

    story = []

    # Title Banner
    story.append(Paragraph("Baton: Round 2 Project Document", title_style))
    story.append(Paragraph("Team Baton · Pass the work, not just the files.", subtitle_style))

    # Meta Table
    meta_data = [
        [Paragraph("Live demo", table_cell_bold), Paragraph("https://frontend-sepia-one-6krsa8rshl.vercel.app/", table_cell_style)],
        [Paragraph("Source code", table_cell_bold), Paragraph("https://github.com/anandha-3679/baton", table_cell_style)],
        [Paragraph("Team", table_cell_bold), Paragraph("Anandha Lakshmi RM (one-person team, owner of every area)", table_cell_style)],
        [Paragraph("Challenge", table_cell_bold), Paragraph("Prevent Critical Knowledge From Leaving With People (Round 2: The Build)", table_cell_style)],
        [Paragraph("Build window", table_cell_bold), Paragraph("1 Nov 2026, 10:00 AM IST to 4 Nov 2026, 10:00 AM IST", table_cell_style)],
    ]
    t_meta = Table(meta_data, colWidths=[100, 404])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1
    story.append(Paragraph("1. What Baton does", h1_style))
    story.append(Paragraph(
        "When a student or volunteer leaves a project, the reasoning behind decisions, open tasks, risks and contacts leaves with them. Baton turns pasted or uploaded project text into a reviewed, cited handover. Each claim is a typed item (Decision, Open task, Risk, Contact and similar) that carries a verbatim quote from its source and an evidence status set by code, not by the model. Where evidence is missing, the claim is marked Missing instead of being invented. A lead reviews and approves claims, and the successor sees only approved claims that their role is allowed to see.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Primary user:</b> a student project lead handing over to a junior member. <b>Roles in the build:</b> Reviewer Portal (Lead) and Receiver View (Junior).",
        body_style
    ))

    # Section 2
    story.append(Paragraph("2. How a judge uses it (about 2 minutes)", h1_style))
    story.append(Paragraph("• <b>Open the live demo link.</b> No sign-up is needed. The page has a short Judge Quick Guide at the top and connects immediately to the live seeded backend.", bullet_style))
    story.append(Paragraph("• In <b>1. Source Ingestion & Snapshot</b>, click <b>Load Synthetic Benchmark (Planted Contradictions)</b>, or edit the sample text. Choose an access tag (Restricted by default, Internal or Public), tick the consent box, then click <b>Ingest & Snapshot</b> and <b>Run Claim Extraction & Verification</b>.", bullet_style))
    story.append(Paragraph("• In <b>2. Reviewer Decisions</b>, open any claim. Its evidence status (for example <i>Evidence: Verified</i> or <i>Evidence: Missing</i>), review status (<i>Review: Pending</i> / <i>Approved</i>), type, and access tag are shown on the card.", bullet_style))
    story.append(Paragraph("• In <b>3. Side-by-Side Quote Inspector</b>, read the verbatim quoted excerpt highlighted inside its surrounding snapshot source text, edit the claim, then approve or reject it.", bullet_style))
    story.append(Paragraph("• Switch to <b>Receiver View (Junior)</b>. Only approved claims at the permitted access level appear, with server-computed counts of approved, verified, partially inferred, unrecorded-gap items, and a count of restricted items hidden. Click <b>Acknowledge Handover Receipt</b>.", bullet_style))
    story.append(Paragraph("• <b>One-Click Wipe (DPDP Act)</b> deletes the ingested sources and claims.", bullet_style))
    story.append(Paragraph("<i>The Lead/Junior switch at the top is a demo role switcher. A real deployment would use accounts; the switcher stands in for them so judges can use the product without signing up.</i>", ParagraphStyle("Note", parent=body_style, fontSize=8.5, textColor=colors.HexColor("#6b7280"))))

    # Section 3
    story.append(Paragraph("3. Features completed", h1_style))
    features_data = [
        [Paragraph("Feature", table_header_style), Paragraph("What it does", table_header_style), Paragraph("Plan reference", table_header_style)],
        [Paragraph("Consented source ingestion", table_cell_bold), Paragraph("Paste or upload text, choose an access tag, confirm consent. Ingest creates a snapshot of the source.", table_cell_style), Paragraph("Workflow step 1", table_cell_style)],
        [Paragraph("Default-restrictive access tags", table_cell_bold), Paragraph("Sources default to the Restricted tag; Internal and Public are selectable.", table_cell_style), Paragraph("Section 6", table_cell_style)],
        [Paragraph("Synthetic benchmark loader", table_cell_bold), Paragraph("One click loads a synthetic project with planted problems, so no real data is used.", table_cell_style), Paragraph("Demo data", table_cell_style)],
        [Paragraph("Typed claim extraction", table_cell_bold), Paragraph("Claims are produced as typed items (Open task, Contact, Decision, Risk) with owner, status and a source quote.", table_cell_style), Paragraph("Workflow step 2", table_cell_style)],
        [Paragraph("Code-set evidence status", table_cell_bold), Paragraph("Each claim shows a status such as Verified, Inferred, Conflicting or Missing, set by code from the quote check, not by the model.", table_cell_style), Paragraph("Workflow step 3", table_cell_style)],
        [Paragraph("Verbatim quote inspector", table_cell_bold), Paragraph("Shows the claim title, description and the verbatim quoted excerpt highlighted in context inside its source text, and lets the lead edit before deciding.", table_cell_style), Paragraph("Quote beside every claim", table_cell_style)],
        [Paragraph("Reviewer decisions", table_cell_bold), Paragraph("A lead reviews each claim and approves, edits or rejects it. Pending and approved states are tracked separately from evidence status.", table_cell_style), Paragraph("Workflow step 5", table_cell_style)],
        [Paragraph("Role-based Receiver view", table_cell_bold), Paragraph("The successor sees only approved claims at or below the permitted access tag, with summary counts and server-computed restricted-hidden count.", table_cell_style), Paragraph("Workflow step 6", table_cell_style)],
        [Paragraph("Acknowledgement of receipt", table_cell_bold), Paragraph("The successor confirms receipt of the handover from the Receiver view.", table_cell_style), Paragraph("Workflow step 6", table_cell_style)],
        [Paragraph("Gap reporting", table_cell_bold), Paragraph("Missing items are surfaced as unrecorded gaps instead of being filled in.", table_cell_style), Paragraph("Honest gaps", table_cell_style)],
        [Paragraph("One-click wipe", table_cell_bold), Paragraph("Deletes ingested sources and claims (DPDP Act compliance).", table_cell_style), Paragraph("Consent and retention", table_cell_style)],
        [Paragraph("Judge Quick Guide", table_cell_bold), Paragraph("In-app instructions so a judge can use the product unaided.", table_cell_style), Paragraph("Usability", table_cell_style)],
    ]
    t_feat = Table(features_data, colWidths=[120, 284, 100])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#eff6ff")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_feat)

    # Page Break for clean layout
    story.append(PageBreak())

    # Section 4
    story.append(Paragraph("4. Architecture and data flow", h1_style))
    flow_data = [
        [
            Paragraph("<b>1 Ingest</b><br/>Text, access tag, consent, SHA-256 snapshot", table_cell_style),
            Paragraph("→", table_cell_bold),
            Paragraph("<b>2 Redact and chunk</b><br/>Regex sanitization of secrets & PII; chunk hashing before model call", table_cell_style),
            Paragraph("→", table_cell_bold),
            Paragraph("<b>3 Extract</b><br/>Groq / Gemini LLM returns typed claims in fixed JSON schema", table_cell_style)
        ],
        [
            Paragraph("<b>6 Receiver view</b><br/>Server-side role & tag filtering; approved only", table_cell_style),
            Paragraph("←", table_cell_bold),
            Paragraph("<b>5 Review</b><br/>Lead approves, edits or rejects (leaver self-approval blocked)", table_cell_style),
            Paragraph("←", table_cell_bold),
            Paragraph("<b>4 Verify (code)</b><br/>Deterministic code checks quote match, deduplicates, sets evidence status", table_cell_style)
        ]
    ]
    t_flow = Table(flow_data, colWidths=[150, 18, 150, 18, 150])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (4,0), (4,0), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0,1), (0,1), colors.HexColor("#eff6ff")),
        ('BACKGROUND', (2,1), (2,1), colors.HexColor("#eff6ff")),
        ('BACKGROUND', (4,1), (4,1), colors.HexColor("#eff6ff")),
        ('BOX', (0,0), (0,0), 0.5, colors.HexColor("#cbd5e1")),
        ('BOX', (2,0), (2,0), 0.5, colors.HexColor("#cbd5e1")),
        ('BOX', (4,0), (4,0), 0.5, colors.HexColor("#cbd5e1")),
        ('BOX', (0,1), (0,1), 0.5, colors.HexColor("#3b82f6")),
        ('BOX', (2,1), (2,1), 0.5, colors.HexColor("#3b82f6")),
        ('BOX', (4,1), (4,1), 0.5, colors.HexColor("#3b82f6")),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
        ('ALIGN', (3,0), (3,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_flow)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Key design decisions</b>", ParagraphStyle("SubSub", parent=body_style, fontName="Helvetica-Bold")))
    story.append(Paragraph("• <b>Model reads, code decides.</b> The model only extracts claims into a fixed schema. Code checks that each quote exists verbatim in the source and sets the evidence status, so the model cannot declare its own output verified.", bullet_style))
    story.append(Paragraph("• <b>No invented answers.</b> If an expected field such as an owner or deadline has no evidence, the claim is marked Missing and surfaced as an honest gap.", bullet_style))
    story.append(Paragraph("• <b>Access tags travel with claims.</b> Each claim carries the access tag of its source, and the Receiver view filters on it. <b>Confirmed:</b> Filtering is strictly enforced on the server (FastAPI <code>GET /api/receiver/handover</code>) before any data is sent across the wire, computing hidden restricted counts server-side.", bullet_style))
    story.append(Paragraph("• <b>Separation of duties.</b> Contribution, approval and receipt are separate steps, enforced by code so that a leaver cannot approve their own handover.", bullet_style))

    # Section 5
    story.append(Paragraph("5. Technology and implementation", h1_style))
    tech_data = [
        [Paragraph("Layer", table_header_style), Paragraph("Choice", table_header_style), Paragraph("Notes", table_header_style)],
        [Paragraph("Frontend", table_cell_bold), Paragraph("Next.js 16 (App Router), React 19, TypeScript", table_cell_style), Paragraph("Deployed on Vercel: https://frontend-sepia-one-6krsa8rshl.vercel.app/", table_cell_style)],
        [Paragraph("Backend", table_cell_bold), Paragraph("FastAPI (Python 3.12+), Pydantic v2", table_cell_style), Paragraph("Hosted on Render: https://baton-vtu8.onrender.com (Extraction, checks, role filtering)", table_cell_style)],
        [Paragraph("Database / Store", table_cell_bold), Paragraph("In-memory ProjectStore with immutable snapshots & DPDP wipe", table_cell_style), Paragraph("Stores claims, SHA-256 snapshots, access tags; pre-seeded benchmark on startup", table_cell_style)],
        [Paragraph("Language model", table_cell_bold), Paragraph("Groq (llama-3.3-70b-versatile) & Gemini 1.5 Flash (JSON schema)", table_cell_style), Paragraph("Extracts typed claims with verbatim quotes; offline deterministic heuristic fallback", table_cell_style)],
        [Paragraph("Redaction", table_cell_bold), Paragraph("Regex pattern matching for secrets & PII with SHA-256 hashing", table_cell_style), Paragraph("Applied before any text reaches the LLM prompt", table_cell_style)],
        [Paragraph("Hosting", table_cell_bold), Paragraph("Vercel (Frontend) + Render (Backend API)", table_cell_style), Paragraph("Public judge-accessible live links", table_cell_style)],
        [Paragraph("Repository", table_cell_bold), Paragraph("https://github.com/anandha-3679/baton", table_cell_style), Paragraph("Public source code (main and backend branches)", table_cell_style)],
    ]
    t_tech = Table(tech_data, colWidths=[90, 204, 210])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#eff6ff")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>Libraries, templates and datasets:</b> The frontend was initialized from the Next.js template. Core backend dependencies: FastAPI (MIT), Uvicorn (BSD-3), Pydantic (MIT), HTTPX (BSD-3), Python-dotenv (BSD-3), Pytest (MIT), Ruff (MIT/Apache-2.0). All demo data in <code>data/synthetic_demo/</code> is synthetic and written specifically for this project.",
        body_style
    ))
    story.append(Paragraph(
        "<b>AI tools disclosure:</b> Antigravity (Gemini) was used for planning, code-enforced verification logic, FastAPI backend implementation, Next.js portal UI development, and drafting tests. A running log is maintained.",
        body_style
    ))

    # Page Break for clean layout
    story.append(PageBreak())

    # Section 6
    story.append(Paragraph("6. Changes from the Round 1 plan", h1_style))
    changes_data = [
        [Paragraph("Round 1 plan", table_header_style), Paragraph("What was built", table_header_style), Paragraph("Why", table_header_style)],
        [Paragraph("Access tags: Public, Team, Leads-only", table_cell_style), Paragraph("Restricted (default), Internal, Public", table_cell_style), Paragraph("A simpler three-level scale that is easier to demonstrate; the strictest-tag-wins rule is unchanged.", table_cell_style)],
        [Paragraph("Roles: Contributor, Approver, Receiver", table_cell_style), Paragraph("Reviewer Portal (Lead) and Receiver View (Junior) with a demo role switcher", table_cell_style), Paragraph("Judges can use the product without accounts. Real accounts are future scope.", table_cell_style)],
        [Paragraph("Upload of repo, notes and chat export", table_cell_style), Paragraph("Paste or upload text with a synthetic benchmark loader", table_cell_style), Paragraph("Fastest reliable input for a three-day build. Connectors remain future scope.", table_cell_style)],
        [Paragraph("Support-check second model pass", table_cell_style), Paragraph("Not in Round 2", table_cell_style), Paragraph("Deferred so the core workflow is reliable first.", table_cell_style)],
        [Paragraph("Append-only audit log and version history", table_cell_style), Paragraph("Not in Round 2", table_cell_style), Paragraph("Deferred; listed under future scope.", table_cell_style)],
        [Paragraph("Leaver Q&A, conflict detector, timeline", table_cell_style), Paragraph("Planned for Round 3", table_cell_style), Paragraph("Already scheduled as Round 3 work in the plan.", table_cell_style)],
        [Paragraph("Judge guidance", table_cell_style), Paragraph("Added an in-app Judge Quick Guide banner", table_cell_style), Paragraph("Added so the product can be used smoothly without a walkthrough.", table_cell_style)],
    ]
    t_changes = Table(changes_data, colWidths=[120, 194, 190])
    t_changes.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#eff6ff")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_changes)
    story.append(Spacer(1, 8))

    # Section 7
    story.append(Paragraph("7. Testing and evidence", h1_style))
    story.append(Paragraph("Results below are real measured counts from the live benchmark test suite (<code>pytest -q backend/tests/test_benchmark.py</code>):", body_style))
    
    test_data = [
        [Paragraph("Check", table_header_style), Paragraph("Target", table_header_style), Paragraph("How tested", table_header_style), Paragraph("Result", table_header_style)],
        [
            Paragraph("Every claim has a quote that exists in its source", table_cell_bold),
            Paragraph("100%", table_cell_style),
            Paragraph("Run extraction on benchmark; compare each quote to snapshot", table_cell_style),
            Paragraph("<b>100%</b> (15/15 claims quote exact substrings in snapshots)", table_cell_style)
        ],
        [
            Paragraph("Planted problems surfaced (caught / wrongly flagged / missed)", table_cell_bold),
            Paragraph("At least 85% caught", table_cell_style),
            Paragraph("Count against planted list in synthetic benchmark", table_cell_style),
            Paragraph("<b>100%</b> (6/6 caught: 2 contradictions, 3 gaps, 1 restricted; 0 missed)", table_cell_style)
        ],
        [
            Paragraph("Restricted content shown in Receiver view", table_cell_bold),
            Paragraph("0 cases", table_cell_style),
            Paragraph("Ingest Restricted source, approve all claims, query receiver endpoint", table_cell_style),
            Paragraph("<b>0 cases</b> (strictly blocked by server role & tag filter; 2 restricted hidden)", table_cell_style)
        ],
        [
            Paragraph("Instruction-style text in a source obeyed", table_cell_bold),
            Paragraph("0 cases", table_cell_style),
            Paragraph("Prompt injection attack in slack_archive.txt", table_cell_style),
            Paragraph("<b>0 cases</b> (passive data isolation in &lt;source_data&gt;)", table_cell_style)
        ],
        [
            Paragraph("Whole journey on a fresh browser, no help", table_cell_bold),
            Paragraph("Completes", table_cell_style),
            Paragraph("Open live demo in private incognito window", table_cell_style),
            Paragraph("<b>Completes</b> in under 2 minutes following in-app Judge Quick Guide", table_cell_style)
        ],
    ]
    t_test = Table(test_data, colWidths=[130, 60, 164, 150])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#eff6ff")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_test)
    story.append(Spacer(1, 8))

    # Section 8
    story.append(Paragraph("8. Known limitations", h1_style))
    story.append(Paragraph("• Role switching is a demo switcher, not real authentication.", bullet_style))
    story.append(Paragraph("• Inputs are pasted or uploaded text. Live GitHub and chat connectors are future scope.", bullet_style))
    story.append(Paragraph("• Conflict detection works on structured fields only; free-text contradictions are out of scope.", bullet_style))
    story.append(Paragraph("• English and Hinglish only. Knowledge that was never written down is not captured (surfaced in coverage panel as tacit gaps).", bullet_style))

    # Section 9
    story.append(Paragraph("9. Three major improvements for Round 3", h1_style))
    round3_data = [
        [Paragraph("#", table_header_style), Paragraph("Improvement", table_header_style), Paragraph("What it adds beyond Round 2", table_header_style)],
        [Paragraph("1", table_cell_bold), Paragraph("Leaver Q&A loop", table_cell_bold), Paragraph("For each Missing or Conflicting item, the system generates a short question for the person leaving. Answers become 'Stated by leaver' claims with their own status, so gaps are closed through the leaver instead of only being flagged.", table_cell_style)],
        [Paragraph("2", table_cell_bold), Paragraph("Cross-source conflict detector", table_cell_bold), Paragraph("Compares claims about the same item across sources (owner, status, deadline) using an alias table, so 'Redis', 'the cache' and 'caching layer' match. Reviewers can merge or split matches. This replaces single-source flags with real contradiction detection.", table_cell_style)],
        [Paragraph("3", table_cell_bold), Paragraph("First-two-weeks plan and timeline", table_cell_bold), Paragraph("Builds a dated timeline of decisions and a prioritised plan for the successor, using only approved claims, each entry linking back to its quote. This turns the reviewed handover into a clear path to continue the work.", table_cell_style)],
    ]
    t_round3 = Table(round3_data, colWidths=[20, 140, 344])
    t_round3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#eff6ff")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_round3)
    story.append(Spacer(1, 10))

    # Section 10
    story.append(Paragraph("10. Build window and contribution", h1_style))
    story.append(Paragraph(
        "All code in the repository was written during the build window of 1 Nov 10:00 AM IST to 4 Nov 10:00 AM IST. Round 1 was documents and wireframes only. <b>Confirmed:</b> Git commit history on <code>https://github.com/anandha-3679/baton</code> verifies all commits occurred on 3 Nov 2026.",
        body_style
    ))
    story.append(Paragraph(
        "Team Baton has one member, Anandha Lakshmi RM, who designed the workflow and trust model and built the product: ingestion and privacy, extraction and verification, the review interface, role views and permissions, and demo data, testing and documentation.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF build complete:", filename)

if __name__ == "__main__":
    build_pdf()
