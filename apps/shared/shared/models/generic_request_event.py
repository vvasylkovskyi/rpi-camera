from typing import Optional
from pydantic import BaseModel

class GenericRequestEvent(BaseModel):
    request_id: Optional[str] = None