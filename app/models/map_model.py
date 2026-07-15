from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TourismInfo(Base):
    __tablename__ = "tourism_info"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    content_id: Mapped[int] = mapped_column(
        "contentId",
        Integer,
        nullable=False,
        index=True
    )

    content_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True
    )

    map_x: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    map_y: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )