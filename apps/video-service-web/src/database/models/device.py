from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String
    
class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(100), nullable=False))
