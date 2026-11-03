"use client";

import React, { useEffect, useState } from "react";
import { Claim, ReceiverFilterMetadata, ReceiverHandoverResponse, SourceSnapshot } from "@/types";
import { API_BASE_URL } from "@/config";
import { SourceUploader } from "@/components/SourceUploader";
import { ReviewPortal } from "@/components/ReviewPortal";
import { ReceiverView } from "@/components/ReceiverView";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"reviewer" | "receiver">("reviewer");
  const [snapshots, setSnapshots] = useState<SourceSnapshot[]>([]);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [receiverClaims, setReceiverClaims] = useState<Claim[]>([]);
  const [receiverMetadata, setReceiverMetadata] = useState<ReceiverFilterMetadata | null>(null);

  const fetchReceiverClaims = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/receiver/handover?role=junior_member`);
      if (res.ok) {
        const data: ReceiverHandoverResponse = await res.json();
        setReceiverClaims(data.claims);
        setReceiverMetadata(data.filter_metadata);
      }
    } catch {
      // API not up or network error
    }
  };

  useEffect(() => {
    let ignore = false;
    async function loadInitialData() {
      try {
        const [sourcesRes, claimsRes, receiverRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/sources`),
          fetch(`${API_BASE_URL}/api/claims`),
          fetch(`${API_BASE_URL}/api/receiver/handover?role=junior_member`),
        ]);
        if (!ignore && sourcesRes.ok) setSnapshots(await sourcesRes.json());
        if (!ignore && claimsRes.ok) setClaims(await claimsRes.json());
        if (!ignore && receiverRes.ok) {
          const recData: ReceiverHandoverResponse = await receiverRes.json();
          setReceiverClaims(recData.claims);
          setReceiverMetadata(recData.filter_metadata);
        }
      } catch {
        // API offline
      }
    }
    loadInitialData();
    return () => {
      ignore = true;
    };
  }, []);

  const handleSourceUploaded = (snap: SourceSnapshot) => {
    setSnapshots((prev) => [...prev.filter((s) => s.id !== snap.id), snap]);
  };

  const handleRunExtraction = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/extract`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setClaims(data);
        fetchReceiverClaims();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleWipe = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/project/wipe`, { method: "DELETE" });
      if (res.ok) {
        setSnapshots([]);
        setClaims([]);
        setReceiverClaims([]);
        fetchReceiverClaims();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleBenchmarkReloaded = async () => {
    try {
      const [sourcesRes, claimsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/sources`),
        fetch(`${API_BASE_URL}/api/claims`),
      ]);
      if (sourcesRes.ok) setSnapshots(await sourcesRes.json());
      if (claimsRes.ok) setClaims(await claimsRes.json());
      fetchReceiverClaims();
    } catch (e) {
      console.error(e);
    }
  };

  const handleClaimReviewed = (updated: Claim) => {
    setClaims((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
    fetchReceiverClaims();
  };

  return (
    <main style={{ maxWidth: "1280px", margin: "0 auto", padding: "32px 20px" }}>
      {/* Top Banner Header */}
      <header style={{ marginBottom: "28px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <h1 style={{ fontSize: "1.75rem", fontWeight: 800, letterSpacing: "-0.02em" }}>
                Baton
              </h1>
              <span
                style={{
                  fontSize: "0.75rem",
                  padding: "2px 8px",
                  borderRadius: "4px",
                  backgroundColor: "rgba(99, 102, 241, 0.2)",
                  color: "#a5b4fc",
                  border: "1px solid var(--accent-primary)",
                  fontWeight: 600,
                }}
              >
                Code-Enforced Trust
              </span>
            </div>
            <p style={{ fontSize: "0.95rem", color: "var(--text-muted)", marginTop: "4px" }}>
              Pass the work, not just the files. Every claim links to a quoted source with code-verified integrity.
            </p>
          </div>

          {/* Persona Switcher Tabs */}
          <div
            style={{
              display: "flex",
              backgroundColor: "var(--bg-surface)",
              padding: "4px",
              borderRadius: "8px",
              border: "1px solid var(--border-color)",
            }}
          >
            <button
              onClick={() => setActiveTab("reviewer")}
              style={{
                padding: "8px 16px",
                borderRadius: "6px",
                border: "none",
                fontWeight: 600,
                fontSize: "0.85rem",
                backgroundColor: activeTab === "reviewer" ? "var(--accent-primary)" : "transparent",
                color: activeTab === "reviewer" ? "#ffffff" : "var(--text-muted)",
              }}
            >
              Reviewer Portal (Lead)
            </button>
            <button
              onClick={() => {
                setActiveTab("receiver");
                fetchReceiverClaims();
              }}
              style={{
                padding: "8px 16px",
                borderRadius: "6px",
                border: "none",
                fontWeight: 600,
                fontSize: "0.85rem",
                backgroundColor: activeTab === "receiver" ? "var(--accent-primary)" : "transparent",
                color: activeTab === "receiver" ? "#ffffff" : "var(--text-muted)",
              }}
            >
              Receiver View (Junior)
            </button>
          </div>
        </div>
      </header>

      {/* Quick Evaluation Guide Banner */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "10px 16px",
          marginBottom: "20px",
          backgroundColor: "rgba(99, 102, 241, 0.08)",
          border: "1px solid rgba(99, 102, 241, 0.3)",
          borderRadius: "8px",
          fontSize: "0.83rem",
          color: "var(--text-main)",
          flexWrap: "wrap",
          gap: "10px",
        }}
      >
        <div>
          <strong>Judge Quick Guide:</strong>{" "}
          1. Demo benchmark is pre-loaded with baseline approved claims &rarr;{" "}
          2. Inspect quotes &amp; resolve <em>Conflicting</em> / <em>Missing</em> claims in <strong>Reviewer Portal</strong> &rarr;{" "}
          3. Switch to <strong>Receiver View</strong> to verify server-side role &amp; restricted-tag filtering.
        </div>
        <span style={{ color: "#a5b4fc", fontWeight: 600 }}>
          {receiverClaims.length} Approved for Receiver &middot; {receiverMetadata?.restricted_claims_hidden_count ?? 0} Restricted Hidden
        </span>
      </div>

      {/* Main Persona Workspaces */}
      {activeTab === "reviewer" ? (
        <div>
          <SourceUploader
            onUploaded={handleSourceUploaded}
            onExtractionTriggered={handleRunExtraction}
            onWipeTriggered={handleWipe}
            onBenchmarkReloaded={handleBenchmarkReloaded}
          />
          <ReviewPortal
            claims={claims}
            snapshots={snapshots}
            onClaimReviewed={handleClaimReviewed}
          />
        </div>
      ) : (
        <div>
          <ReceiverView
            claims={receiverClaims}
            filterMetadata={receiverMetadata}
            onSwitchToReviewer={() => setActiveTab("reviewer")}
          />
        </div>
      )}
    </main>
  );
}
