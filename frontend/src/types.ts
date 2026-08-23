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
  created_at: string;
  updated_at: string;
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
  created_at: string;
}

export interface ModelVersionCreate {
  version_number: number;
  description: string;
}

export interface MLflowVersionSummary {
  name: string;
  version: string;
  run_id: string | null;
  source: string | null;
  status: string | null;
}

export interface MLflowRegisteredModel {
  name: string;
  description: string | null;
  versions: MLflowVersionSummary[];
}

export interface MLflowVersionDetails
  extends MLflowVersionSummary {
  metrics: Record<string, number>;
  params: Record<string, string>;
}

export interface MLflowImportRequest {
  model_name: string;
  version: string;
}

export interface MLflowImportResult {
  version: ModelVersion;
  mlflow: MLflowVersionDetails;
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
  actor_email: string | null;
  created_at: string;
}

export type MetricDirection =
  | "higher_is_better"
  | "lower_is_better";

export type MonitoringStatus =
  | "healthy"
  | "warning"
  | "critical";

export interface MonitoringRecord {
  id: number;
  model_id: number;
  metric_name: string;
  baseline_value: number;
  current_value: number;
  direction: MetricDirection;
  degradation: number;
  status: MonitoringStatus;
  created_at: string;
}

export interface MonitoringCreate {
  metric_name: string;
  baseline_value: number;
  current_value: number;
  direction: MetricDirection;
  warning_threshold: number;
  critical_threshold: number;
}

export type UserRole =
  | "admin"
  | "model_owner"
  | "reviewer";

export interface UserRecord {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
