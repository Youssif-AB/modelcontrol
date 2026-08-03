from fastapi import FastAPI, UploadFile, Depends, status
from app.schemas import ModelCreate
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ModelRecord
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
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record
