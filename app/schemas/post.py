from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PostCreate(BaseModel):
    content: str = Field(
        min_length=1
    )


class PostUpdate(BaseModel):
    content: Optional[str] = Field(
        default=None,
        min_length=1
    )


class PostResponse(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )