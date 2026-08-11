from fastapi import FastAPI, UploadFile, Depends, status, HTTPException
from app.schemas import ModelCreate, ModelVersionCreate, ModelVersionRead
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models import ModelRecord, ModelVersion
from app.schemas import ModelCreate, ModelRead


app = FastAPI(title="ModelControl API")

@app.get("/health")
def health_check() -> dict[str,str]:
    return {"status":"ok"}

@app.post("/models/validate")
def validate_model(model: ModelCreate) -> ModelCreate:
    return model


@app.post(
    "/models",
    response_model=ModelRead,
    status_code=status.HTTP_201_CREATED,
)
def create_model(
    model:ModelCreate,
    db:Session = Depends(get_db),
) -> ModelRecord:
    record = ModelRecord(
        name=model.name,
        purpose=model.business_area,
        business_area = model.business_area,
        owner_email = str(model.owner_email),
        model_type = model.model_type.value,
        risk_tier=model.risk_tier.value,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record

@app.get("/models", response_model=list[ModelRead])
def list_models(db : Session = Depends(get_db)):
    statement = select(ModelRecord).order_by(ModelRecord.id)
    models = db.scalars(statement).all()
    return models

@app.get("/models/{model_id}", response_model=ModelRead)
def get_model(
    model_id:int,
    db: Session = Depends(get_db),
) -> ModelRecord:
    model = db.get(ModelRecord, model_id)

    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Model not found"
        )

    return model
@app.post(
    "/models/{model_id}/versions",
    response_model=ModelVersionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_model_version(
    model_id: int,
    version: ModelVersionCreate,
    db: Session = Depends(get_db),
) -> ModelVersion:
    model = db.get(ModelRecord, model_id)

    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    record = ModelVersion(
        model_id=model_id,
        version_number=version.version_number,
        description=version.description,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@app.get(
    "/models/{model_id}/versions",
    response_model=list[ModelVersionRead],
)
def list_model_versions(
    model_id: int,
    db: Session = Depends(get_db),
):
    model = db.get(ModelRecord, model_id)

    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    statement = (
        select(ModelVersion)
        .where(ModelVersion.model_id == model_id)
        .order_by(ModelVersion.version_number)
    )

    return db.scalars(statement).all()