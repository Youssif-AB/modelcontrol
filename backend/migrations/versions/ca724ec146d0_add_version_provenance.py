"""Add model version provenance

Revision ID: ca724ec146d0
Revises: 7d1f0b2386a4
Create Date: 2026-08-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ca724ec146d0"
down_revision: Union[str, Sequence[str], None] = "7d1f0b2386a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "model_versions",
        sa.Column(
            "source_type",
            sa.String(length=30),
            server_default="manual",
            nullable=False,
        ),
    )
    op.add_column(
        "model_versions",
        sa.Column("registered_model_name", sa.String(255)),
    )
    op.add_column(
        "model_versions",
        sa.Column("external_version", sa.String(50)),
    )
    op.add_column(
        "model_versions",
        sa.Column("run_id", sa.String(255)),
    )
    op.add_column(
        "model_versions",
        sa.Column("artifact_source", sa.Text()),
    )
    op.add_column(
        "model_versions",
        sa.Column("metrics", sa.JSON()),
    )
    op.add_column(
        "model_versions",
        sa.Column("params", sa.JSON()),
    )


def downgrade() -> None:
    for column in (
        "params",
        "metrics",
        "artifact_source",
        "run_id",
        "external_version",
        "registered_model_name",
        "source_type",
    ):
        op.drop_column("model_versions", column)
