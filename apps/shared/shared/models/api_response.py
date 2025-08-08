from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")

class APIResponse(GenericModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
