export type ModelType = "classification" | "regression";

export type RiskTier = "low" | "medium" | "high";

export type LifecycleStatus =
  | "draft"
  | "under_review"
  | "approved"
  | "retired";

export interface ModelRecord {
  id: number;
  name: string;
  purpose: string;
  business_area: string;
  owner_email: string;
  model_type: ModelType;
  risk_tier: RiskTier;
  lifecycle_status: LifecycleStatus;
}

export interface ModelCreate {
  name: string;
  purpose: string;
  business_area: string;
  owner_email: string;
  model_type: ModelType;
  risk_tier: RiskTier;
}

export interface ModelVersion {
  id: number;
  model_id: number;
  version_number: number;
  description: string;
}

export interface ModelVersionCreate {
  version_number: number;
  description: string;
}

export type LifecycleAction =
  | "submit_for_review"
  | "approve"
  | "reject"
  | "retire";

export type FindingSeverity =
  | "low"
  | "medium"
  | "high"
  | "critical";

export type FindingStatus =
  | "open"
  | "resolved";

export interface Finding {
  id: number;
  model_id: number;
  title: string;
  description: string;
  severity: FindingSeverity;
  status: FindingStatus;
  resolution_notes: string | null;
}

export interface FindingCreate {
  title: string;
  description: string;
  severity: FindingSeverity;
}

export interface AuditEvent {
  id: number;
  model_id: number;
  event_type: string;
  description: string;
  created_at: string;
}