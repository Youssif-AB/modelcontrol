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