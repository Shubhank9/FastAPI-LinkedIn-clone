from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Education(Base):
    __tablename__ = "educations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    institution: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    degree: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    field_of_study: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    start_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )

    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )