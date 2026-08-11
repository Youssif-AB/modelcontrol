from sqlalchemy import String, Text
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