from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


class ModelRecord(Base):
    __tablename__ = "models"

    __table_args__ = (
        CheckConstraint(
            "risk_tier IN ('low', 'medium', 'high')",
            name="ck_models_risk_tier",
        ),
        CheckConstraint(
            (
                "lifecycle_status IN "
                "('draft', 'under_review', 'approved', 'retired')"
            ),
            name="ck_models_lifecycle_status",
        ),
        Index(
            "ix_models_owner_email",
            "owner_email",
        ),
        Index(
            "ix_models_lifecycle_status",
            "lifecycle_status",
        ),
        Index(
            "ix_models_risk_tier",
            "risk_tier",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    purpose: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    business_area: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    owner_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    model_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    risk_tier: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="medium",
    )

    lifecycle_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="draft",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    versions: Mapped[list["ModelVersion"]] = relationship(
        back_populates="model",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    findings: Mapped[list["ModelFinding"]] = relationship(
        back_populates="model",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    audit_events: Mapped[list["AuditEvent"]] = relationship(
        back_populates="model",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    monitoring_records: Mapped[
        list["MonitoringRecord"]
    ] = relationship(
        back_populates="model",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ModelVersion(Base):
    __tablename__ = "model_versions"

    __table_args__ = (
        UniqueConstraint(
            "model_id",
            "version_number",
            name=(
                "uq_model_versions_"
                "model_id_version_number"
            ),
        ),
        CheckConstraint(
            "version_number >= 1",
            name="ck_model_versions_version_number",
        ),
        Index(
            "ix_model_versions_model_id",
            "model_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    model_id: Mapped[int] = mapped_column(
        ForeignKey(
            "models.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    version_number: Mapped[int] = mapped_column(
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    model: Mapped["ModelRecord"] = relationship(
        back_populates="versions",
    )


class ModelFinding(Base):
    __tablename__ = "model_findings"

    __table_args__ = (
        CheckConstraint(
            (
                "severity IN "
                "('low', 'medium', 'high', 'critical')"
            ),
            name="ck_model_findings_severity",
        ),
        CheckConstraint(
            "status IN ('open', 'resolved')",
            name="ck_model_findings_status",
        ),
        Index(
            "ix_model_findings_model_id",
            "model_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    model_id: Mapped[int] = mapped_column(
        ForeignKey(
            "models.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="open",
    )

    resolution_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    model: Mapped["ModelRecord"] = relationship(
        back_populates="findings",
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    __table_args__ = (
        Index(
            "ix_audit_events_model_id_created_at",
            "model_id",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    model_id: Mapped[int] = mapped_column(
        ForeignKey(
            "models.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    model: Mapped["ModelRecord"] = relationship(
        back_populates="audit_events",
    )


class MonitoringRecord(Base):
    __tablename__ = "monitoring_records"

    __table_args__ = (
        CheckConstraint(
            "baseline_value > 0",
            name="ck_monitoring_baseline_positive",
        ),
        CheckConstraint(
            "current_value >= 0",
            name="ck_monitoring_current_nonnegative",
        ),
        CheckConstraint(
            (
                "direction IN "
                "('higher_is_better', 'lower_is_better')"
            ),
            name="ck_monitoring_direction",
        ),
        CheckConstraint(
            (
                "status IN "
                "('healthy', 'warning', 'critical')"
            ),
            name="ck_monitoring_status",
        ),
        Index(
            "ix_monitoring_model_id_created_at",
            "model_id",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    model_id: Mapped[int] = mapped_column(
        ForeignKey(
            "models.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    baseline_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    current_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    direction: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    degradation: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    model: Mapped["ModelRecord"] = relationship(
        back_populates="monitoring_records",
    )


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            (
                "role IN "
                "('admin', 'model_owner', 'reviewer')"
            ),
            name="ck_users_role",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )