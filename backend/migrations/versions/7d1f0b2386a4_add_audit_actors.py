"""Add audit actors

Revision ID: 7d1f0b2386a4
Revises: 0332fa2c020e
Create Date: 2026-08-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7d1f0b2386a4"
down_revision: Union[str, Sequence[str], None] = "0332fa2c020e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "audit_events",
        sa.Column(
            "actor_email",
            sa.String(length=255),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "audit_events",
        "actor_email",
    )
