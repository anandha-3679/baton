"use client";

import React, { useState } from "react";
import { AccessTag, SourceSnapshot } from "../types";
import { API_BASE_URL } from "../config";

interface SourceUploaderProps {
  onUploaded: (snapshot: SourceSnapshot) => void;
  onExtractionTriggered: () => void;
  onWipeTriggered: () => void;
  onBenchmarkReloaded?: () => void;
}

export const SourceUploader: React.FC<SourceUploaderProps> = ({
  onUploaded,
  onExtractionTriggered,
  onWipeTriggered,
  onBenchmarkReloaded,
}) => {
  const [filename, setFilename] = useState("handover_doc.md");
  const [content, setContent] = useState(
    "DECISION: Standardize on FastAPI and Next.js App Router.\n" +
    "TODO: Deploy Postgres database by next Friday (assigned to: Alice).\n" +
    "RISK: Dependency on deprecated auth microservice.\n" +
    "CONTACT: Alice Smith (Lead Engineer)"
  );
  const [accessTag, setAccessTag] = useState<AccessTag>("Internal");
  const [consent, setConsent] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!content.trim() || !consent) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/sources`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename,
          content,
          access_tag: accessTag,
          consent_confirmed: consent,
        }),
      });
      if (res.ok) {
        const snap = await res.json();
        onUploaded(snap);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSyntheticBenchmark = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/project/seed`, { method: "POST" });
      if (res.ok && onBenchmarkReloaded) {
        onBenchmarkReloaded();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        backgroundColor: "var(--bg-surface)",
        border: "1px solid var(--border-color)",
        borderRadius: "10px",
        padding: "20px",
        marginBottom: "24px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <h2 style={{ fontSize: "1.1rem", fontWeight: 600 }}>1. Source Ingestion & Snapshot</h2>
        <div style={{ display: "flex", gap: "10px" }}>
          <button
            onClick={handleLoadSyntheticBenchmark}
            style={{
              padding: "6px 14px",
              backgroundColor: "rgba(99, 102, 241, 0.2)",
              color: "#a5b4fc",
              border: "1px solid var(--accent-primary)",
              borderRadius: "6px",
              fontWeight: 500,
              fontSize: "0.85rem",
            }}
          >
            Load Synthetic Benchmark (Planted Contradictions)
          </button>
          <button
            onClick={onWipeTriggered}
            style={{
              padding: "6px 14px",
              backgroundColor: "rgba(239, 68, 68, 0.15)",
              color: "#fca5a5",
              border: "1px solid var(--accent-danger)",
              borderRadius: "6px",
              fontWeight: 500,
              fontSize: "0.85rem",
            }}
          >
            One-Click Wipe (DPDP Act)
          </button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 200px", gap: "12px", marginBottom: "12px" }}>
        <input
          type="text"
          value={filename}
          onChange={(e) => setFilename(e.target.value)}
          placeholder="Filename (e.g., handover_doc.md)"
        />
        <select
          value={accessTag}
          onChange={(e) => setAccessTag(e.target.value as AccessTag)}
        >
          <option value="Restricted">Tag: Restricted (Default)</option>
          <option value="Internal">Tag: Internal</option>
          <option value="Public">Tag: Public</option>
        </select>
      </div>

      <textarea
        rows={4}
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Paste text notes, markdown handover, or chat export..."
        style={{ width: "100%", marginBottom: "12px", resize: "vertical" }}
      />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "0.85rem", color: "var(--text-muted)" }}>
          <input
            type="checkbox"
            checked={consent}
            onChange={(e) => setConsent(e.target.checked)}
          />
          I confirm consent to ingest and redact this handover source.
        </label>

        <div style={{ display: "flex", gap: "10px" }}>
          <button
            onClick={handleUpload}
            disabled={loading || !consent}
            style={{
              padding: "8px 16px",
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--border-color)",
              color: "var(--text-main)",
              borderRadius: "6px",
            }}
          >
            Ingest & Snapshot
          </button>
          <button
            onClick={onExtractionTriggered}
            style={{
              padding: "8px 20px",
              backgroundColor: "var(--accent-primary)",
              color: "#ffffff",
              border: "none",
              borderRadius: "6px",
              fontWeight: 600,
            }}
          >
            Run Claim Extraction & Verification
          </button>
        </div>
      </div>
    </div>
  );
};
