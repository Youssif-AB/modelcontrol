from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class RiskTier(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class LifecycleStatus(str, Enum):
    draft = "draft"
    under_review = "under_review"
    approved = "approved"
    retired = "retired"

class ModelType(str, Enum):
    classification = "classification"
    regression = "regression"

class ModelCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    purpose: str = Field(min_length = 10, max_length = 500)
    business_area: str = Field(min_length = 2, max_length=100)
    owner_email: EmailStr
    model_type: ModelType
    risk_tier: RiskTier = RiskTier.medium

class ModelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    name:str
    purpose:str
    business_area:str
    owner_email:EmailStr
    model_type:ModelType
    risk_tier: RiskTier
    lifecycle_status: LifecycleStatus

class ModelVersionCreate(BaseModel):
    version_number: int = Field(ge=1)
    description: str = Field(min_length=5, max_length=500)


class ModelVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: int
    version_number: int
    description: str

class LifecycleAction(str, Enum):
    submit_for_review = "submit_for_review"
    approve = "approve"
    reject = "reject"
    retire = "retire"


class LifecycleActionRequest(BaseModel):
    action: LifecycleAction

class FindingSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class FindingStatus(str, Enum):
    open = "open"
    resolved = "resolved"


class FindingCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=10, max_length=1000)
    severity: FindingSeverity


class FindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: int
    title: str
    description: str
    severity: FindingSeverity
    status: FindingStatus
    resolution_notes: str | None


class FindingResolveRequest(BaseModel):
    resolution_notes: str = Field(min_length=5, max_length=1000)

class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: int
    event_type: str
    description: str
    created_at: datetime

class MetricDirection(str, Enum):
    higher_is_better = "higher_is_better"
    lower_is_better = "lower_is_better"


class MonitoringStatus(str, Enum):
    healthy = "healthy"
    warning = "warning"
    critical = "critical"


class MonitoringCreate(BaseModel):
    metric_name: str = Field(min_length=2, max_length=100)
    baseline_value: float = Field(gt=0)
    current_value: float = Field(ge=0)
    direction: MetricDirection
    warning_threshold: float = Field(default=0.05, gt=0)
    critical_threshold: float = Field(default=0.10, gt=0)


class MonitoringRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: int
    metric_name: str
    baseline_value: float
    current_value: float
    direction: MetricDirection
    degradation: float
    status: MonitoringStatus
    created_at: datetime