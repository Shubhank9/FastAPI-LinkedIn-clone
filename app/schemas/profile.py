from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProfileCreate(BaseModel):
    headline: Optional[str] = Field(
        default=None,
        max_length=255
    )

    location: Optional[str] = Field(
        default=None,
        max_length=255
    )

    bio: Optional[str] = None


class ProfileUpdate(BaseModel):
    headline: Optional[str] = Field(
        default=None,
        max_length=255
    )

    location: Optional[str] = Field(
        default=None,
        max_length=255
    )

    bio: Optional[str] = None


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    headline: Optional[str]
    location: Optional[str]
    bio: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )