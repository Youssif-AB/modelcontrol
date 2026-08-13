from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class ModelRecord(Base):
    __tablename__ = "models"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    purpose: Mapped[str] = mapped_column(Text)
    business_area: Mapped[str] = mapped_column(String(100))
    owner_email: Mapped[str] = mapped_column(String(320))
    model_type: Mapped[str] = mapped_column(String(30))
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

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(primary_key=True)

    model_id: Mapped[int] = mapped_column(
        ForeignKey("models.id", ondelete="CASCADE"),
        nullable=False,
    )

    version_number: Mapped[int] = mapped_column(nullable=False)

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

class ModelFinding(Base):
    __tablename__ = "model_findings"

    id: Mapped[int] = mapped_column(primary_key=True)

    model_id: Mapped[int] = mapped_column(
        ForeignKey("models.id", ondelete="CASCADE"),
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