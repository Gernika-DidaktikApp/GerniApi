from typing import Optional

from pydantic import BaseModel, Field


class ActividadCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)


class ActividadUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)


class ActividadResponse(BaseModel):
    id: str
    nombre: str

    class Config:
        from_attributes = True
