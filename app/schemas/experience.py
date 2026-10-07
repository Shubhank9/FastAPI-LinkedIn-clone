from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExperienceCreate(BaseModel):
    company_id: int
    title: str = Field(
        min_length=1,
        max_length=255
    )
    location: Optional[str] = Field(
        default=None,
        max_length=255
    )
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False


class ExperienceUpdate(BaseModel):
    company_id: Optional[int] = None
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255
    )
    location: Optional[str] = Field(
        default=None,
        max_length=255
    )
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None


class ExperienceResponse(BaseModel):
    id: int
    user_id: int
    company_id: int
    title: str
    location: Optional[str]
    description: Optional[str]
    start_date: date
    end_date: Optional[date]
    is_current: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )