from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database import Base


class TourismInfo(Base):
    __tablename__ = "tourism_info"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    content_id: Mapped[str] = mapped_column(
        "contentId",
        String,
        nullable=False,
        unique=True,
    )

    content_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    map_x: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    map_y: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    title: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    addr1: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    addr2: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    firstimage: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )