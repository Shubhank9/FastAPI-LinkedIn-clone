from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.institution import Institution


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

    institution_id: Mapped[int] = mapped_column(
        ForeignKey("institutions.id"),
        nullable=False,
        index=True
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

    # many-to-one: each education belongs to exactly one institution
    institution: Mapped[Institution] = relationship()
