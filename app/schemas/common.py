from typing import Generic, Optional, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    status_code: int
    data: Optional[T] = None