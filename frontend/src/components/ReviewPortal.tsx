"use client";

import React, { useState } from "react";
import { Claim, ReviewStatus, SourceSnapshot } from "../types";
import { API_BASE_URL } from "../config";
import { AccessBadge, ClaimTypeBadge, EvidenceBadge, ReviewStatusBadge } from "./Badges";

function renderHighlightedSource(sourceText: string, quote: string): React.ReactNode {
  if (!quote) return sourceText;
  const idx = sourceText.indexOf(quote);
  if (idx === -1) {
    return sourceText;
  }
  const before = sourceText.slice(0, idx);
  const match = sourceText.slice(idx, idx + quote.length);
  const after = sourceText.slice(idx + quote.length);
  return (
    <>
      <span style={{ color: "#9ca3af" }}>{before}</span>
      <mark
        style={{
          backgroundColor: "rgba(16, 185, 129, 0.28)",
          color: "#a7f3d0",
          padding: "2px 4px",
          borderRadius: "4px",
          border: "1px solid #10b981",
          fontWeight: 600,
        }}
      >
        {match}
      </mark>
      <span style={{ color: "#9ca3af" }}>{after}</span>
    </>
  );
}

interface ReviewPortalProps {
  claims: Claim[];
  snapshots: SourceSnapshot[];
  onClaimReviewed: (updated: Claim) => void;
}

export const ReviewPortal: React.FC<ReviewPortalProps> = ({
  claims,
  snapshots,
  onClaimReviewed,
}) => {
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);
  const [reviewerName, setReviewerName] = useState("Lead Reviewer");
  const [editTitle, setEditTitle] = useState("");
  const [editDesc, setEditDesc] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSelectClaim = (c: Claim) => {
    setSelectedClaim(c);
    setEditTitle(c.title);
    setEditDesc(c.description);
    setErrorMsg(null);
  };

  const handleReviewAction = async (status: ReviewStatus) => {
    if (!selectedClaim) return;
    setErrorMsg(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/claims/${selectedClaim.id}/review`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          review_status: status,
          reviewer: reviewerName,
          edited_title: editTitle !== selectedClaim.title ? editTitle : undefined,
          edited_description: editDesc !== selectedClaim.description ? editDesc : undefined,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        setErrorMsg(err.detail || "Failed to update review status");
        return;
      }

      const updated = await res.json();
      onClaimReviewed(updated);
      setSelectedClaim(updated);
    } catch {
      setErrorMsg("Network error connecting to API");
    }
  };

  // Find quoted snapshots (including multiple snapshots for conflicting claims)
  const matchingSnapshots = selectedClaim
    ? snapshots.filter((s) => selectedClaim.source_ids.includes(s.id))
    : [];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1.15fr 1fr", gap: "20px" }}>
      {/* Left: Claim List */}
      <div
        style={{
          backgroundColor: "var(--bg-surface)",
          border: "1px solid var(--border-color)",
          borderRadius: "10px",
          padding: "20px",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 600 }}>2. Reviewer Decisions ({claims.length} Claims)</h2>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>Reviewer:</span>
            <input
              type="text"
              value={reviewerName}
              onChange={(e) => setReviewerName(e.target.value)}
              style={{ width: "130px", padding: "4px 8px", fontSize: "0.85rem" }}
            />
          </div>
        </div>

        {claims.length === 0 ? (
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>No claims extracted yet. Upload sources and run extraction.</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px", maxHeight: "650px", overflowY: "auto" }}>
            {claims.map((claim) => {
              const isSelected = selectedClaim?.id === claim.id;
              return (
                <div
                  key={claim.id}
                  onClick={() => handleSelectClaim(claim)}
                  style={{
                    padding: "12px 14px",
                    borderRadius: "8px",
                    backgroundColor: isSelected ? "var(--bg-card-hover)" : "var(--bg-card)",
                    border: isSelected ? "1px solid var(--accent-primary)" : "1px solid var(--border-color)",
                    cursor: "pointer",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px", flexWrap: "wrap", gap: "6px" }}>
                    <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                      <ClaimTypeBadge type={claim.type} />
                      <AccessBadge tag={claim.access_tag} />
                    </div>
                    <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                      <EvidenceBadge status={claim.evidence_status} />
                      <ReviewStatusBadge status={claim.review_status} />
                    </div>
                  </div>
                  <h4 style={{ fontSize: "0.95rem", fontWeight: 600, marginBottom: "4px" }}>{claim.title}</h4>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "6px" }}>
                    {claim.description}
                  </p>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", color: "var(--text-dim)" }}>
                    <span>Owner: {claim.owner || "None"}</span>
                    {claim.deadline && <span>Deadline: {claim.deadline}</span>}
                    {claim.status && <span>Task Progress: {claim.status}</span>}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Right: Side-by-Side Quote Inspector & Decision Actions */}
      <div
        style={{
          backgroundColor: "var(--bg-surface)",
          border: "1px solid var(--border-color)",
          borderRadius: "10px",
          padding: "20px",
        }}
      >
        <h2 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "16px" }}>3. Side-by-Side Quote Inspector</h2>

        {selectedClaim ? (
          <div>
            {errorMsg && (
              <div
                style={{
                  padding: "10px 14px",
                  backgroundColor: "rgba(239, 68, 68, 0.2)",
                  border: "1px solid var(--accent-danger)",
                  borderRadius: "6px",
                  color: "#fca5a5",
                  marginBottom: "14px",
                  fontSize: "0.85rem",
                }}
              >
                ⚠️ {errorMsg}
              </div>
            )}

            {selectedClaim.conflict_notes && (
              <div
                style={{
                  padding: "10px 14px",
                  backgroundColor: "rgba(245, 158, 11, 0.15)",
                  border: "1px solid var(--accent-warning)",
                  borderRadius: "6px",
                  color: "#fde68a",
                  marginBottom: "14px",
                  fontSize: "0.85rem",
                }}
              >
                ⚠️ <strong>Conflict Flagged by Code:</strong> {selectedClaim.conflict_notes}
              </div>
            )}

            <div style={{ marginBottom: "12px" }}>
              <label style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
                Claim Title
              </label>
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                style={{ width: "100%" }}
              />
            </div>

            <div style={{ marginBottom: "12px" }}>
              <label style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
                Claim Description
              </label>
              <textarea
                rows={2}
                value={editDesc}
                onChange={(e) => setEditDesc(e.target.value)}
                style={{ width: "100%", resize: "vertical" }}
              />
            </div>

            <div style={{ marginBottom: "12px" }}>
              <label style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
                Extracted Verbatim Quote
              </label>
              <div
                style={{
                  padding: "8px 12px",
                  backgroundColor: "#030712",
                  border: "1px solid #10b981",
                  borderRadius: "6px",
                  fontFamily: "monospace",
                  fontSize: "0.82rem",
                  color: "#a7f3d0",
                  whiteSpace: "pre-wrap",
                }}
              >
                &ldquo;{selectedClaim.quote}&rdquo;
              </div>
            </div>

            {matchingSnapshots.length > 0 && (
              <div style={{ marginBottom: "16px" }}>
                <label style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "block", marginBottom: "6px" }}>
                  Full Source Snapshot Context (Quote Highlighted in Source)
                </label>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px", maxHeight: "260px", overflowY: "auto" }}>
                  {matchingSnapshots.map((snap) => (
                    <div
                      key={snap.id}
                      style={{
                        padding: "10px 12px",
                        backgroundColor: "#030712",
                        border: "1px solid var(--border-color)",
                        borderRadius: "6px",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          marginBottom: "6px",
                          paddingBottom: "6px",
                          borderBottom: "1px solid rgba(255,255,255,0.08)",
                          fontSize: "0.75rem",
                          color: "var(--text-dim)",
                        }}
                      >
                        <span>
                          Source: <code>{snap.filename}</code>
                        </span>
                        <span>SHA-256: {snap.sha256.substring(0, 12)}...</span>
                      </div>
                      <div
                        style={{
                          fontFamily: "monospace",
                          fontSize: "0.8rem",
                          lineHeight: 1.55,
                          whiteSpace: "pre-wrap",
                        }}
                      >
                        {renderHighlightedSource(snap.content, selectedClaim.quote)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div style={{ display: "flex", gap: "10px" }}>
              <button
                onClick={() => handleReviewAction("Approved")}
                style={{
                  flex: 1,
                  padding: "10px",
                  backgroundColor: "var(--accent-success)",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "6px",
                  fontWeight: 600,
                }}
              >
                Approve Claim
              </button>
              <button
                onClick={() => handleReviewAction("Edited")}
                style={{
                  flex: 1,
                  padding: "10px",
                  backgroundColor: "var(--accent-primary)",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "6px",
                  fontWeight: 600,
                }}
              >
                Save Edits
              </button>
              <button
                onClick={() => handleReviewAction("Rejected")}
                style={{
                  flex: 1,
                  padding: "10px",
                  backgroundColor: "var(--accent-danger)",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "6px",
                  fontWeight: 600,
                }}
              >
                Reject
              </button>
            </div>
          </div>
        ) : (
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>Select a claim to review its quote and decide.</p>
        )}
      </div>
    </div>
  );
};
