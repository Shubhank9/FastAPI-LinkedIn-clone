from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EducationCreate(BaseModel):
    institution_id: int
    degree: Optional[str] = Field(
        default=None,
        max_length=255
    )
    field_of_study: Optional[str] = Field(
        default=None,
        max_length=255
    )
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class EducationUpdate(BaseModel):
    institution_id: Optional[int] = None
    degree: Optional[str] = Field(
        default=None,
        max_length=255
    )
    field_of_study: Optional[str] = Field(
        default=None,
        max_length=255
    )
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

    # institution_id may be left out of a PATCH, but if it is sent it can't be null
    @field_validator("institution_id")
    @classmethod
    def institution_id_not_null(cls, value):
        if value is None:
            raise ValueError("institution_id cannot be null")
        return value


class EducationResponse(BaseModel):
    id: int
    user_id: int
    institution_id: int
    degree: Optional[str]
    field_of_study: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
