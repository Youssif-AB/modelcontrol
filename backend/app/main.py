from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    status,
)
from fastapi.middleware.cors import (
    CORSMiddleware,
)
from fastapi.middleware.trustedhost import (
    TrustedHostMiddleware,
)
from prometheus_client import (
    make_asgi_app,
)
from slowapi import (
    _rate_limit_exceeded_handler,
)
from slowapi.errors import (
    RateLimitExceeded,
)
from sqlalchemy import (
    func,
    select,
    text,
)
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
)
from sqlalchemy.orm import Session

from app.auth import router as auth_router
from app.config import settings
from app.database import get_db
from app.mlflow_schemas import (
    MLflowImportRequest,
    MLflowImportResult,
    MLflowRegisteredModelRead,
)
from app.mlflow_service import (
    MLflowIntegrationError,
    get_mlflow_version_details,
    list_mlflow_models,
)
from app.models import (
    AuditEvent,
    ModelFinding,
    ModelRecord,
    ModelVersion,
    MonitoringRecord,
    User,
)
from app.observability import (
    observability_middleware,
)
from app.permissions import (
    ensure_lifecycle_permission,
    ensure_model_owner_or_admin,
    require_roles,
)
from app.rate_limit import limiter
from app.schemas import (
    AuditEventRead,
    FindingCreate,
    FindingRead,
    FindingResolveRequest,
    LifecycleActionRequest,
    MetricDirection,
    ModelCreate,
    ModelRead,
    ModelVersionCreate,
    ModelVersionRead,
    MonitoringCreate,
    MonitoringRead,
)
from app.security import (
    get_current_user,
)
from app.security_headers import (
    security_headers_middleware,
)


app = FastAPI(
    title="ModelControl API",
    docs_url=(
        "/docs"
        if settings.docs_enabled
        else None
    ),
    redoc_url=(
        "/redoc"
        if settings.docs_enabled
        else None
    ),
    openapi_url=(
        "/openapi.json"
        if settings.docs_enabled
        else None
    ),
)


app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


app.include_router(auth_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        settings.cors_origin_list
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Request-ID",
    ],
)


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=(
        settings.allowed_host_list
    ),
)


app.middleware("http")(
    security_headers_middleware
)

app.middleware("http")(
    observability_middleware
)


metrics_app = make_asgi_app()

app.mount(
    "/metrics",
    metrics_app,
)


LIFECYCLE_TRANSITIONS = {
    (
        "draft",
        "submit_for_review",
    ): "under_review",

    (
        "under_review",
        "approve",
    ): "approved",

    (
        "under_review",
        "reject",
    ): "draft",

    (
        "approved",
        "retire",
    ): "retired",
}


def calculate_degradation(
    baseline: float,
    current: float,
    direction: MetricDirection,
) -> float:
    if (
        direction
        == MetricDirection.higher_is_better
    ):
        return (
            baseline - current
        ) / baseline

    return (
        current - baseline
    ) / baseline


def determine_monitoring_status(
    degradation: float,
    warning_threshold: float,
    critical_threshold: float,
) -> str:
    if (
        degradation
        >= critical_threshold
    ):
        return "critical"

    if (
        degradation
        >= warning_threshold
    ):
        return "warning"

    return "healthy"


def add_audit_event(
    db: Session,
    model_id: int,
    event_type: str,
    description: str,
    actor_email: str,
) -> None:
    db.add(
        AuditEvent(
            model_id=model_id,
            event_type=event_type,
            description=description,
            actor_email=actor_email,
        )
    )


@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }


@app.get("/ready")
def readiness_check(
    db: Session = Depends(get_db),
):
    try:
        db.execute(
            text("SELECT 1")
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail="Database unavailable",
        ) from None

    return {
        "status": "ready",
    }


@app.get(
    "/integrations/mlflow/models",
    response_model=list[
        MLflowRegisteredModelRead
    ],
)
def get_mlflow_models(
    current_user: User = Depends(
        get_current_user
    ),
):
    try:
        return list_mlflow_models()

    except MLflowIntegrationError:
        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "MLflow tracking server "
                "is unavailable"
            ),
        ) from None


@app.post(
    (
        "/models/{model_id}/"
        "versions/import/mlflow"
    ),
    response_model=MLflowImportResult,
    status_code=(
        status.HTTP_201_CREATED
    ),
)
def import_mlflow_version(
    model_id: int,
    request: MLflowImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    model = db.get(
        ModelRecord,
        model_id,
    )

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    ensure_model_owner_or_admin(
        model,
        current_user,
    )

    try:
        mlflow_version = (
            get_mlflow_version_details(
                request.model_name,
                request.version,
            )
        )

    except MLflowIntegrationError:
        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Unable to retrieve model "
                "version from MLflow"
            ),
        ) from None

    current_max = db.scalar(
        select(
            func.max(
                ModelVersion.version_number
            )
        ).where(
            ModelVersion.model_id
            == model_id
        )
    )

    next_version = (
        current_max or 0
    ) + 1

    description = (
        "Imported from MLflow — "
        f"{mlflow_version.name} "
        f"v{mlflow_version.version}"
    )

    record = ModelVersion(
        model_id=model_id,
        version_number=next_version,
        description=description,
        source_type="mlflow",
        registered_model_name=mlflow_version.name,
        external_version=mlflow_version.version,
        run_id=mlflow_version.run_id,
        artifact_source=mlflow_version.source,
        metrics=mlflow_version.metrics,
        params=mlflow_version.params,
    )

    db.add(record)

    add_audit_event(
        db,
        model_id,
        "mlflow_version_imported",
        (
            "Imported MLflow model "
            f"'{mlflow_version.name}' "
            f"version "
            f"{mlflow_version.version} "
            "as ModelControl version "
            f"{next_version}."
        ),
        current_user.email,
    )

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Unable to allocate a new "
                "model version"
            ),
        ) from None

    db.refresh(record)

    return MLflowImportResult(
        version=record,
        mlflow=mlflow_version,
    )


@app.post(
    "/models/validate",
    dependencies=[
        Depends(get_current_user),
    ],
)
def validate_model(
    model: ModelCreate,
):
    return model


@app.post(
    "/models",
    response_model=ModelRead,
    status_code=status.HTTP_201_CREATED,
)
def create_model(
    model: ModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "admin",
            "model_owner",
        )
    ),
):
    owner_email = str(
        model.owner_email
    )

    if (
        current_user.role
        == "model_owner"
        and owner_email.lower()
        != current_user.email.lower()
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Model owners may only "
                "register models they own"
            ),
        )

    record = ModelRecord(
        name=model.name,
        purpose=model.purpose,
        business_area=(
            model.business_area
        ),
        owner_email=owner_email,
        model_type=(
            model.model_type.value
        ),
        risk_tier=(
            model.risk_tier.value
        ),
    )

    db.add(record)
    db.flush()

    add_audit_event(
        db,
        record.id,
        "model_created",
        (
            f"Model '{record.name}' "
            "was registered."
        ),
        current_user.email,
    )

    db.commit()
    db.refresh(record)

    return record


@app.get(
    "/models",
    response_model=list[ModelRead],
)
def list_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return db.scalars(
        select(ModelRecord)
        .order_by(ModelRecord.id)
    ).all()


@app.get(
    "/models/{model_id}",
    response_model=ModelRead,
)
def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    model = db.get(
        ModelRecord,
        model_id,
    )

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found",
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
    current_user: User = Depends(
        get_current_user
    ),
):
    model = db.get(
        ModelRecord,
        model_id,
    )

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    ensure_model_owner_or_admin(
        model,
        current_user,
    )

    existing_version = db.scalar(
        select(ModelVersion).where(
            ModelVersion.model_id
            == model_id,
            ModelVersion.version_number
            == version.version_number,
        )
    )

    if existing_version is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Version "
                f"{version.version_number} "
                "already exists for this model"
            ),
        )

    record = ModelVersion(
        model_id=model_id,
        version_number=(
            version.version_number
        ),
        description=version.description,
    )

    db.add(record)

    add_audit_event(
        db,
        model_id,
        "version_created",
        (
            f"Version "
            f"{version.version_number} "
            "was added."
        ),
        current_user.email,
    )

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                f"Version "
                f"{version.version_number} "
                "already exists for this model"
            ),
        ) from None

    db.refresh(record)

    return record


@app.get(
    "/models/{model_id}/versions",
    response_model=list[
        ModelVersionRead
    ],
)
def list_model_versions(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    model = db.get(
        ModelRecord,
        model_id,
    )

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    return db.scalars(
        select(ModelVersion)
        .where(
            ModelVersion.model_id
            == model_id
        )
        .order_by(
            ModelVersion.version_number
        )
    ).all()


@app.patch(
    "/models/{model_id}/lifecycle",
    response_model=ModelRead,
)
def update_model_lifecycle(
    model_id: int,
    request: LifecycleActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    model = db.get(
        ModelRecord,
        model_id,
    )

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    ensure_lifecycle_permission(
        model,
        request.action.value,
        current_user,
    )

    transition = (
        model.lifecycle_status,
        request.action.value,
    )

    next_status = (
        LIFECYCLE_TRANSITIONS.get(
            transition
        )
    )

    previous_status = (
        model.lifecycle_status
    )

    if next_status is None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot "
                f"{request.action.value} "
                f"model from "
                f"{model.lifecycle_status} "
                "status"
            ),
        )

    model.lifecycle_status = (
        next_status
    )

    note_text = (
        f" Note: {request.note}"
        if request.note
        else ""
    )

    add_audit_event(
        db,
        model_id,
        "lifecycle_changed",
        (
            "Lifecycle changed from "
            f"{previous_status} "
            f"to {next_status}."
            f"{note_text}"
        ),
        current_user.email,
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
    current_user: User = Depends(
        require_roles(
            "admin",
            "reviewer",
        )
    ),
):
    model = db.get(
        ModelRecord,
        model_id,
    )

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    record = ModelFinding(
        model_id=model_id,
        title=finding.title,
        description=(
            finding.description
        ),
        severity=(
            finding.severity.value
        ),
    )

    db.add(record)

    add_audit_event(
        db,
        model_id,
        "finding_created",
        (
            f"Finding "
            f"'{finding.title}' "
            "was created with "
            f"{finding.severity.value} "
            "severity."
        ),
        current_user.email,
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
    current_user: User = Depends(
        get_current_user
    ),
):
    model = db.get(
        ModelRecord,
        model_id,
    )

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    return db.scalars(
        select(ModelFinding)
        .where(
            ModelFinding.model_id
            == model_id
        )
        .order_by(
            ModelFinding.id
        )
    ).all()


@app.patch(
    "/findings/{finding_id}/resolve",
    response_model=FindingRead,
)
def resolve_finding(
    finding_id: int,
    request: FindingResolveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    finding = db.get(
        ModelFinding,
        finding_id,
    )

    if finding is None:
        raise HTTPException(
            status_code=404,
            detail="Finding not found",
        )

    model = db.get(
        ModelRecord,
        finding.model_id,
    )

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    ensure_model_owner_or_admin(
        model,
        current_user,
    )

    if finding.status == "resolved":
        raise HTTPException(
            status_code=409,
            detail=(
                "Finding is already resolved"
            ),
        )

    finding.status = "resolved"
    finding.resolution_notes = (
        request.resolution_notes
    )

    add_audit_event(
        db,
        finding.model_id,
        "finding_resolved",
        (
            f"Finding "
            f"'{finding.title}' "
            "was resolved."
        ),
        current_user.email,
    )

    db.commit()
    db.refresh(finding)

    return finding


@app.get(
    "/models/{model_id}/audit",
    response_model=list[
        AuditEventRead
    ],
)
def list_audit_events(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    model = db.get(
        ModelRecord,
        model_id,
    )

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    return db.scalars(
        select(AuditEvent)
        .where(
            AuditEvent.model_id
            == model_id
        )
        .order_by(
            AuditEvent.created_at,
            AuditEvent.id,
        )
    ).all()


@app.post(
    "/models/{model_id}/monitoring",
    response_model=MonitoringRead,
    status_code=status.HTTP_201_CREATED,
)
def create_monitoring_record(
    model_id: int,
    monitoring: MonitoringCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    model = db.get(
        ModelRecord,
        model_id,
    )

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    ensure_model_owner_or_admin(
        model,
        current_user,
    )

    if (
        monitoring.critical_threshold
        <= monitoring.warning_threshold
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=(
                "Critical threshold must "
                "be greater than warning "
                "threshold"
            ),
        )

    degradation = (
        calculate_degradation(
            monitoring.baseline_value,
            monitoring.current_value,
            monitoring.direction,
        )
    )

    monitoring_status = (
        determine_monitoring_status(
            degradation,
            monitoring.warning_threshold,
            monitoring.critical_threshold,
        )
    )

    record = MonitoringRecord(
        model_id=model_id,
        metric_name=(
            monitoring.metric_name
        ),
        baseline_value=(
            monitoring.baseline_value
        ),
        current_value=(
            monitoring.current_value
        ),
        direction=(
            monitoring.direction.value
        ),
        degradation=degradation,
        status=monitoring_status,
    )

    db.add(record)

    add_audit_event(
        db,
        model_id,
        "monitoring_recorded",
        (
            f"{monitoring.metric_name} "
            "monitoring status recorded "
            f"as {monitoring_status}."
        ),
        current_user.email,
    )

    db.commit()
    db.refresh(record)

    return record


@app.get(
    "/models/{model_id}/monitoring",
    response_model=list[
        MonitoringRead
    ],
)
def list_monitoring_records(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    model = db.get(
        ModelRecord,
        model_id,
    )

    if model is None:
        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    return db.scalars(
        select(MonitoringRecord)
        .where(
            MonitoringRecord.model_id
            == model_id
        )
        .order_by(
            MonitoringRecord.created_at,
            MonitoringRecord.id,
        )
    ).all()
