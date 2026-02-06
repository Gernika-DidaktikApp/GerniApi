from typing import Optional

from pydantic import BaseModel, Field


class EventoCreate(BaseModel):
    id_actividad: str = Field(..., min_length=36, max_length=36)
    nombre: str = Field(..., min_length=1, max_length=100)
    contenido: Optional[str] = Field(None, description="Texto largo o URL de imagen")


class EventoUpdate(BaseModel):
    id_actividad: Optional[str] = Field(None, min_length=36, max_length=36)
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    contenido: Optional[str] = Field(None, description="Texto largo o URL de imagen")


class EventoResponse(BaseModel):
    id: str
    id_actividad: str
    nombre: str
    contenido: Optional[str] = None

    class Config:
        from_attributes = True
