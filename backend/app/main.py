from fastapi import FastAPI, UploadFile, Depends, status, HTTPException
from app.schemas import ModelCreate, ModelVersionCreate, ModelVersionRead
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models import ModelRecord, ModelVersion, ModelFinding, AuditEvent
from app.schemas import ModelCreate, ModelRead
from app.schemas import LifecycleAction, LifecycleActionRequest
from app.schemas import FindingCreate, FindingRead, FindingResolveRequest, AuditEventRead


app = FastAPI(title="ModelControl API")

LIFECYCLE_TRANSITIONS = {
    ("draft", "submit_for_review"): "under_review",
    ("under_review", "approve"): "approved",
    ("under_review", "reject"): "draft",
    ("approved", "retire"): "retired",
}

def add_audit_event(
    db: Session,
    model_id: int,
    event_type: str,
    description: str,
) -> None:
    event = AuditEvent(
        model_id=model_id,
        event_type=event_type,
        description=description,
    )

    db.add(event)

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
    db.flush()

    add_audit_event(
        db,
        record.id,
        "model_created",
        f"Model '{record.name}' was registered.",
    )

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

    add_audit_event(
        db,
        model_id,
        "version_created",
        f"Version {version.version_number} was added.",
    )
    
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

@app.patch(
    "/models/{model_id}/lifecycle",
    response_model=ModelRead,
)
def update_model_lifecycle(
    model_id: int,
    request: LifecycleActionRequest,
    db: Session = Depends(get_db),
) -> ModelRecord:
    model = db.get(ModelRecord, model_id)

    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    transition = (
        model.lifecycle_status,
        request.action.value,
    )

    next_status = LIFECYCLE_TRANSITIONS.get(transition)
    previous_status = model.lifecycle_status

    if next_status is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Cannot {request.action.value} model "
                f"from {model.lifecycle_status} status"
            ),
        )

    model.lifecycle_status = next_status

    add_audit_event(
        db,
        model_id,
        "lifecycle_changed",
        f"Lifecycle changed from {previous_status} to {next_status}.",
    )

    db.commit()
    db.refresh(model)

    return model

@app.post(
    "/models/{model_id}/findings",
    response_model=FindingRead,
    status_code=status.HTTP_201_CREATED,
)
def create_finding(
    model_id: int,
    finding: FindingCreate,
    db: Session = Depends(get_db),
) -> ModelFinding:
    model = db.get(ModelRecord, model_id)

    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    record = ModelFinding(
        model_id=model_id,
        title=finding.title,
        description=finding.description,
        severity=finding.severity.value,
    )

    db.add(record)

    add_audit_event(
        db,
        model_id,
        "finding_created",
        f"Finding '{finding.title}' was created with {finding.severity.value} severity.",
    )
    
    db.commit()
    db.refresh(record)

    return record

@app.get(
    "/models/{model_id}/findings",
    response_model=list[FindingRead],
)
def list_findings(
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
        select(ModelFinding)
        .where(ModelFinding.model_id == model_id)
        .order_by(ModelFinding.id)
    )

    return db.scalars(statement).all()

@app.patch(
    "/findings/{finding_id}/resolve",
    response_model=FindingRead,
)
def resolve_finding(
    finding_id: int,
    request: FindingResolveRequest,
    db: Session = Depends(get_db),
) -> ModelFinding:
    finding = db.get(ModelFinding, finding_id)

    if finding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    if finding.status == "resolved":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Finding is already resolved",
        )

    finding.status = "resolved"
    finding.resolution_notes = request.resolution_notes

    add_audit_event(
        db,
        finding.model_id,
        "finding_resolved",
        f"Finding '{finding.title}' was resolved.",
    )
    db.commit()
    db.refresh(finding)

    return finding

@app.get(
    "/models/{model_id}/audit",
    response_model=list[AuditEventRead],
)
def list_audit_events(
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
        select(AuditEvent)
        .where(AuditEvent.model_id == model_id)
        .order_by(AuditEvent.created_at, AuditEvent.id)
    )

    return db.scalars(statement).all()