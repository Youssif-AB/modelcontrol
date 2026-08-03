from enum import Enum

from pydantic import BaseModel, Field, EmailStr

class ModelType(str, Enum):
    classification = "classification"
    regression = "regression"

class ModelCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    purpose: str = Field(min_length = 10, max_length = 500)
    business_area: str = Field(min_length = 2, max_length=100)
    owner_email: EmailStr
    model_type: ModelType