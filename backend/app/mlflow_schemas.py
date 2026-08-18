from pydantic import (
    BaseModel,
    Field,
)

from app.schemas import ModelVersionRead


class MLflowVersionSummary(
    BaseModel
):
    name: str
    version: str
    run_id: str | None = None
    source: str | None = None
    status: str | None = None


class MLflowRegisteredModelRead(
    BaseModel
):
    name: str
    description: str | None = None

    versions: list[
        MLflowVersionSummary
    ] = Field(
        default_factory=list
    )


class MLflowVersionDetails(
    MLflowVersionSummary
):
    metrics: dict[str, float] = Field(
        default_factory=dict
    )

    params: dict[str, str] = Field(
        default_factory=dict
    )


class MLflowImportRequest(
    BaseModel
):
    model_name: str = Field(
        min_length=1,
        max_length=255,
    )

    version: str = Field(
        min_length=1,
        max_length=50,
    )


class MLflowImportResult(
    BaseModel
):
    version: ModelVersionRead
    mlflow: MLflowVersionDetails