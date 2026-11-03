export type AccessTag = "Public" | "Internal" | "Restricted";

export type ClaimType = "Decision" | "Open task" | "Risk" | "Dependency" | "Contact";

export type EvidenceStatus = "Verified" | "Inferred" | "Conflicting" | "Missing" | "Stated by leaver";

export type ReviewStatus = "Pending" | "Approved" | "Edited" | "Rejected";

export interface SourceSnapshot {
  id: string;
  filename: string;
  content: string;
  sha256: string;
  access_tag: AccessTag;
  created_at: string;
}

export interface Claim {
  id: string;
  type: ClaimType;
  title: string;
  description: string;
  quote: string;
  source_ids: string[];
  owner?: string | null;
  deadline?: string | null;
  status?: string | null;
  evidence_status: EvidenceStatus;
  access_tag: AccessTag;
  review_status: ReviewStatus;
  risk_score: number;
  conflict_notes?: string | null;
  created_at: string;
}

export interface ReceiverFilterMetadata {
  role: string;
  max_allowed_tag: AccessTag;
  total_claims_in_project: number;
  visible_approved_count: number;
  restricted_claims_hidden_count: number;
  unapproved_claims_hidden_count: number;
  restricted_sources_hidden_count: number;
}

export interface ReceiverHandoverResponse {
  claims: Claim[];
  filter_metadata: ReceiverFilterMetadata;
}
