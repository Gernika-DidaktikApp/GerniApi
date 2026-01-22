from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EventoEstadoCreate(BaseModel):
    id_juego: str = Field(..., min_length=36, max_length=36)
    id_actividad: str = Field(..., min_length=36, max_length=36)
    id_evento: str = Field(..., min_length=36, max_length=36)


class EventoEstadoUpdate(BaseModel):
    duracion: Optional[int] = None
    fecha_fin: Optional[datetime] = None
    estado: Optional[str] = Field(None, max_length=20)
    puntuacion: Optional[float] = None


class EventoEstadoCompletar(BaseModel):
    puntuacion: float = Field(..., description="Puntuación obtenida en el evento")


class EventoEstadoResponse(BaseModel):
    id: str
    id_juego: str
    id_actividad: str
    id_evento: str
    fecha_inicio: datetime
    duracion: Optional[int] = None
    fecha_fin: Optional[datetime] = None
    estado: str
    puntuacion: Optional[float] = None

    class Config:
        from_attributes = True
