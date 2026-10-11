from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.institution import InstitutionResponse


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


class EducationResponse(BaseModel):
    id: int
    user_id: int
    institution_id: int
    institution: InstitutionResponse
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
