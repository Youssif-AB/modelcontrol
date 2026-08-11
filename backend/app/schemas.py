from enum import Enum

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