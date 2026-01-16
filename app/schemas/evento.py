from pydantic import BaseModel, Field
from typing import Optional

class EventoCreate(BaseModel):
    id_actividad: str = Field(..., min_length=36, max_length=36)
    nombre: str = Field(..., min_length=1, max_length=100)

class EventoUpdate(BaseModel):
    id_actividad: Optional[str] = Field(None, min_length=36, max_length=36)
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)

class EventoResponse(BaseModel):
    id: str
    id_actividad: str
    nombre: str

    class Config:
        from_attributes = True
