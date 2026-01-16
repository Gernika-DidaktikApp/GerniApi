from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProfesorCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=45)
    nombre: str = Field(..., min_length=1, max_length=45)
    apellido: str = Field(..., min_length=1, max_length=45)
    password: str = Field(..., min_length=4, max_length=100)

class ProfesorUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=45)
    nombre: Optional[str] = Field(None, min_length=1, max_length=45)
    apellido: Optional[str] = Field(None, min_length=1, max_length=45)
    password: Optional[str] = Field(None, min_length=4, max_length=100)

class ProfesorResponse(BaseModel):
    id: str
    username: str
    nombre: str
    apellido: str
    created: datetime

    class Config:
        from_attributes = True
