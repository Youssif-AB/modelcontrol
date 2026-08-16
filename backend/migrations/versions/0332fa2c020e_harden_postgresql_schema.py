"""Harden PostgreSQL schema

Revision ID: 0332fa2c020e
Revises: 4ca951288ecb
Create Date: 2026-08-16 16:46:49.226928
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0332fa2c020e"
down_revision: Union[str, Sequence[str], None] = "4ca951288ecb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Audit events
    op.create_index(
        "ix_audit_events_model_id_created_at",
        "audit_events",
        ["model_id", "created_at"],
        unique=False,
    )

    # Findings
    op.add_column(
        "model_findings",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.add_column(
        "model_findings",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_model_findings_model_id",
        "model_findings",
        ["model_id"],
        unique=False,
    )

    op.create_check_constraint(
        "ck_model_findings_severity",
        "model_findings",
        "severity IN ('low', 'medium', 'high', 'critical')",
    )

    op.create_check_constraint(
        "ck_model_findings_status",
        "model_findings",
        "status IN ('open', 'resolved')",
    )

    # Model versions
    op.add_column(
        "model_versions",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_model_versions_model_id",
        "model_versions",
        ["model_id"],
        unique=False,
    )

    op.create_unique_constraint(
        "uq_model_versions_model_id_version_number",
        "model_versions",
        ["model_id", "version_number"],
    )

    op.create_check_constraint(
        "ck_model_versions_version_number",
        "model_versions",
        "version_number >= 1",
    )

    # Models
    op.add_column(
        "models",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.add_column(
        "models",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.alter_column(
        "models",
        "name",
        existing_type=sa.VARCHAR(length=100),
        type_=sa.String(length=150),
        existing_nullable=False,
    )

    op.alter_column(
        "models",
        "owner_email",
        existing_type=sa.VARCHAR(length=320),
        type_=sa.String(length=255),
        existing_nullable=False,
    )

    op.alter_column(
        "models",
        "model_type",
        existing_type=sa.VARCHAR(length=30),
        type_=sa.String(length=50),
        existing_nullable=False,
    )

    op.create_index(
        "ix_models_lifecycle_status",
        "models",
        ["lifecycle_status"],
        unique=False,
    )

    op.create_index(
        "ix_models_owner_email",
        "models",
        ["owner_email"],
        unique=False,
    )

    op.create_index(
        "ix_models_risk_tier",
        "models",
        ["risk_tier"],
        unique=False,
    )

    op.create_check_constraint(
        "ck_models_risk_tier",
        "models",
        "risk_tier IN ('low', 'medium', 'high')",
    )

    op.create_check_constraint(
        "ck_models_lifecycle_status",
        "models",
        (
            "lifecycle_status IN "
            "('draft', 'under_review', 'approved', 'retired')"
        ),
    )

    # Monitoring
    op.create_index(
        "ix_monitoring_model_id_created_at",
        "monitoring_records",
        ["model_id", "created_at"],
        unique=False,
    )

    op.create_check_constraint(
        "ck_monitoring_baseline_positive",
        "monitoring_records",
        "baseline_value > 0",
    )

    op.create_check_constraint(
        "ck_monitoring_current_nonnegative",
        "monitoring_records",
        "current_value >= 0",
    )

    op.create_check_constraint(
        "ck_monitoring_direction",
        "monitoring_records",
        (
            "direction IN "
            "('higher_is_better', 'lower_is_better')"
        ),
    )

    op.create_check_constraint(
        "ck_monitoring_status",
        "monitoring_records",
        "status IN ('healthy', 'warning', 'critical')",
    )

    # Users
    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role IN ('admin', 'model_owner', 'reviewer')",
    )


def downgrade() -> None:
    # Users
    op.drop_constraint(
        "ck_users_role",
        "users",
        type_="check",
    )

    op.drop_column(
        "users",
        "created_at",
    )

    # Monitoring
    op.drop_constraint(
        "ck_monitoring_status",
        "monitoring_records",
        type_="check",
    )

    op.drop_constraint(
        "ck_monitoring_direction",
        "monitoring_records",
        type_="check",
    )

    op.drop_constraint(
        "ck_monitoring_current_nonnegative",
        "monitoring_records",
        type_="check",
    )

    op.drop_constraint(
        "ck_monitoring_baseline_positive",
        "monitoring_records",
        type_="check",
    )

    op.drop_index(
        "ix_monitoring_model_id_created_at",
        table_name="monitoring_records",
    )

    # Models
    op.drop_constraint(
        "ck_models_lifecycle_status",
        "models",
        type_="check",
    )

    op.drop_constraint(
        "ck_models_risk_tier",
        "models",
        type_="check",
    )

    op.drop_index(
        "ix_models_risk_tier",
        table_name="models",
    )

    op.drop_index(
        "ix_models_owner_email",
        table_name="models",
    )

    op.drop_index(
        "ix_models_lifecycle_status",
        table_name="models",
    )

    op.alter_column(
        "models",
        "model_type",
        existing_type=sa.String(length=50),
        type_=sa.VARCHAR(length=30),
        existing_nullable=False,
    )

    op.alter_column(
        "models",
        "owner_email",
        existing_type=sa.String(length=255),
        type_=sa.VARCHAR(length=320),
        existing_nullable=False,
    )

    op.alter_column(
        "models",
        "name",
        existing_type=sa.String(length=150),
        type_=sa.VARCHAR(length=100),
        existing_nullable=False,
    )

    op.drop_column(
        "models",
        "updated_at",
    )

    op.drop_column(
        "models",
        "created_at",
    )

    # Model versions
    op.drop_constraint(
        "ck_model_versions_version_number",
        "model_versions",
        type_="check",
    )

    op.drop_constraint(
        "uq_model_versions_model_id_version_number",
        "model_versions",
        type_="unique",
    )

    op.drop_index(
        "ix_model_versions_model_id",
        table_name="model_versions",
    )

    op.drop_column(
        "model_versions",
        "created_at",
    )

    # Findings
    op.drop_constraint(
        "ck_model_findings_status",
        "model_findings",
        type_="check",
    )

    op.drop_constraint(
        "ck_model_findings_severity",
        "model_findings",
        type_="check",
    )

    op.drop_index(
        "ix_model_findings_model_id",
        table_name="model_findings",
    )

    op.drop_column(
        "model_findings",
        "updated_at",
    )

    op.drop_column(
        "model_findings",
        "created_at",
    )

    # Audit
    op.drop_index(
        "ix_audit_events_model_id_created_at",
        table_name="audit_events",
    )