import React from "react";
import { AccessTag, ClaimType, EvidenceStatus, ReviewStatus } from "../types";

export const EvidenceBadge: React.FC<{ status: EvidenceStatus }> = ({ status }) => {
  const getBadgeStyle = () => {
    switch (status) {
      case "Verified":
        return { bg: "rgba(16, 185, 129, 0.15)", border: "#10b981", icon: "✓" };
      case "Conflicting":
        return { bg: "rgba(239, 68, 68, 0.2)", border: "#ef4444", icon: "⚠️" };
      case "Missing":
        return { bg: "rgba(245, 158, 11, 0.2)", border: "#f59e0b", icon: "❓" };
      case "Inferred":
        return { bg: "rgba(99, 102, 241, 0.2)", border: "#6366f1", icon: "🔍" };
      case "Stated by leaver":
        return { bg: "rgba(6, 182, 212, 0.2)", border: "#06b6d4", icon: "🗣️" };
      default:
        return { bg: "#374151", border: "#6b7280", icon: "•" };
    }
  };

  const { bg, border, icon } = getBadgeStyle();

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "5px",
        padding: "3px 9px",
        borderRadius: "9999px",
        backgroundColor: bg,
        border: `1px solid ${border}`,
        fontSize: "0.78rem",
        fontWeight: 600,
      }}
    >
      <span>{icon}</span>
      <span>Evidence: {status}</span>
    </span>
  );
};

export const ReviewStatusBadge: React.FC<{ status: ReviewStatus }> = ({ status }) => {
  const getStyle = () => {
    switch (status) {
      case "Approved":
        return { bg: "rgba(16, 185, 129, 0.15)", border: "#10b981", color: "#a7f3d0", icon: "✓" };
      case "Edited":
        return { bg: "rgba(99, 102, 241, 0.15)", border: "#6366f1", color: "#c7d2fe", icon: "✎" };
      case "Rejected":
        return { bg: "rgba(239, 68, 68, 0.15)", border: "#ef4444", color: "#fca5a5", icon: "✕" };
      default:
        return { bg: "rgba(156, 163, 175, 0.12)", border: "#6b7280", color: "#d1d5db", icon: "⏳" };
    }
  };

  const { bg, border, color, icon } = getStyle();

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "4px",
        padding: "3px 9px",
        borderRadius: "9999px",
        backgroundColor: bg,
        border: `1px solid ${border}`,
        color,
        fontSize: "0.76rem",
        fontWeight: 600,
      }}
    >
      <span>{icon}</span>
      <span>Review: {status}</span>
    </span>
  );
};

export const AccessBadge: React.FC<{ tag: AccessTag }> = ({ tag }) => {
  const getColors = () => {
    switch (tag) {
      case "Public":
        return { bg: "rgba(16, 185, 129, 0.15)", border: "#10b981" };
      case "Internal":
        return { bg: "rgba(99, 102, 241, 0.15)", border: "#6366f1" };
      case "Restricted":
        return { bg: "rgba(239, 68, 68, 0.15)", border: "#ef4444" };
    }
  };

  const { bg, border } = getColors();

  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 8px",
        borderRadius: "4px",
        backgroundColor: bg,
        border: `1px solid ${border}`,
        fontSize: "0.75rem",
        fontWeight: 500,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
      }}
    >
      {tag}
    </span>
  );
};

export const ClaimTypeBadge: React.FC<{ type: ClaimType }> = ({ type }) => {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 8px",
        borderRadius: "4px",
        backgroundColor: "rgba(255, 255, 255, 0.08)",
        border: "1px solid rgba(255, 255, 255, 0.15)",
        fontSize: "0.75rem",
        color: "#d1d5db",
      }}
    >
      {type}
    </span>
  );
};
