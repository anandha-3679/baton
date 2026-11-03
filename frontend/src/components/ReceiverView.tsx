"use client";

import React, { useState } from "react";
import { Claim, ReceiverFilterMetadata } from "../types";
import { AccessBadge, ClaimTypeBadge, EvidenceBadge, ReviewStatusBadge } from "./Badges";

interface ReceiverViewProps {
  claims: Claim[];
  filterMetadata?: ReceiverFilterMetadata | null;
  onSwitchToReviewer?: () => void;
}

export const ReceiverView: React.FC<ReceiverViewProps> = ({
  claims,
  filterMetadata,
  onSwitchToReviewer,
}) => {
  const [acknowledged, setAcknowledged] = useState(false);
  const asOfDate = new Date().toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  const verifiedCount = claims.filter((c) => c.evidence_status === "Verified").length;
  const inferredCount = claims.filter((c) => c.evidence_status === "Inferred").length;
  const missingCount = claims.filter((c) => c.evidence_status === "Missing").length;

  const restrictedHidden = filterMetadata?.restricted_claims_hidden_count ?? 0;
  const unapprovedHidden = filterMetadata?.unapproved_claims_hidden_count ?? 0;
  const restrictedSourcesHidden = filterMetadata?.restricted_sources_hidden_count ?? 0;
  const maxTag = filterMetadata?.max_allowed_tag ?? "Internal";

  return (
    <div
      style={{
        backgroundColor: "var(--bg-surface)",
        border: "1px solid var(--border-color)",
        borderRadius: "10px",
        padding: "24px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "20px", gap: "16px", flexWrap: "wrap" }}>
        <div>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "4px" }}>
            Handover Receiver Portal (Junior Member View)
          </h2>
          <p style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
            Server-filtered handover (&le; {maxTag} access tag, as of {asOfDate}) &middot;{" "}
            <strong style={{ color: "#fca5a5" }}>
              {restrictedHidden} restricted {restrictedHidden === 1 ? "claim" : "claims"} hidden
            </strong>{" "}
            ({restrictedSourcesHidden} restricted {restrictedSourcesHidden === 1 ? "source" : "sources"} blocked,{" "}
            {unapprovedHidden} unapproved {unapprovedHidden === 1 ? "claim" : "claims"} withheld by server).
          </p>
        </div>

        <button
          onClick={() => setAcknowledged(true)}
          disabled={acknowledged}
          style={{
            padding: "8px 18px",
            backgroundColor: acknowledged ? "var(--accent-success)" : "var(--accent-primary)",
            color: "#ffffff",
            border: "none",
            borderRadius: "6px",
            fontWeight: 600,
            fontSize: "0.85rem",
          }}
        >
          {acknowledged ? "✓ Receipt Acknowledged" : "Acknowledge Handover Receipt"}
        </button>
      </div>

      {/* Coverage & Evidence Integrity Panel */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(5, 1fr)",
          gap: "12px",
          padding: "16px",
          backgroundColor: "var(--bg-card)",
          borderRadius: "8px",
          border: "1px solid var(--border-color)",
          marginBottom: "24px",
        }}
      >
        <div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>Approved Items Shown</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{claims.length}</div>
        </div>
        <div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>Verified Facts</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--accent-success)" }}>{verifiedCount}</div>
        </div>
        <div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>Partially Inferred</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--accent-primary)" }}>{inferredCount}</div>
        </div>
        <div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>Unrecorded Tacit Gaps</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--accent-warning)" }}>{missingCount}</div>
        </div>
        <div>
          <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>Restricted Claims Hidden</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--accent-danger)" }}>{restrictedHidden}</div>
        </div>
      </div>

      {claims.length === 0 ? (
        <div style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
          <p style={{ fontWeight: 600, color: "var(--text-main)", marginBottom: "8px" }}>
            No approved handover claims currently available for the receiver role.
          </p>
          <p style={{ fontSize: "0.85rem", marginBottom: "16px" }}>
            Workflow: <strong>1. Load Benchmark &amp; Extract</strong> &rarr; <strong>2. Approve Claims in Reviewer Portal</strong> &rarr; <strong>3. Switch to Receiver View</strong>
          </p>
          {onSwitchToReviewer && (
            <button
              onClick={onSwitchToReviewer}
              style={{
                padding: "8px 16px",
                backgroundColor: "var(--accent-primary)",
                color: "#ffffff",
                border: "none",
                borderRadius: "6px",
                fontWeight: 600,
                fontSize: "0.85rem",
              }}
            >
              Go to Reviewer Portal
            </button>
          )}
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "14px" }}>
          {claims.map((claim) => (
            <div
              key={claim.id}
              style={{
                backgroundColor: "var(--bg-card)",
                border: "1px solid var(--border-color)",
                borderRadius: "8px",
                padding: "16px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px", flexWrap: "wrap", gap: "6px" }}>
                <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                  <ClaimTypeBadge type={claim.type} />
                  <AccessBadge tag={claim.access_tag} />
                </div>
                <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                  <EvidenceBadge status={claim.evidence_status} />
                  <ReviewStatusBadge status={claim.review_status} />
                </div>
              </div>

              <h3 style={{ fontSize: "1.05rem", fontWeight: 600, marginBottom: "6px" }}>{claim.title}</h3>
              <p style={{ fontSize: "0.9rem", color: "var(--text-main)", marginBottom: "12px" }}>{claim.description}</p>

              <div
                style={{
                  backgroundColor: "#030712",
                  padding: "10px 12px",
                  borderRadius: "6px",
                  borderLeft: "3px solid var(--accent-success)",
                  fontSize: "0.82rem",
                  fontFamily: "monospace",
                  color: "#a7f3d0",
                  marginBottom: "10px",
                }}
              >
                Quote: &ldquo;{claim.quote}&rdquo;
              </div>

              <div style={{ display: "flex", gap: "20px", fontSize: "0.8rem", color: "var(--text-muted)" }}>
                <span>Owner: <strong>{claim.owner || "Unassigned"}</strong></span>
                {claim.deadline && <span>Deadline: <strong>{claim.deadline}</strong></span>}
                {claim.status && <span>Task Progress: <strong>{claim.status}</strong></span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
