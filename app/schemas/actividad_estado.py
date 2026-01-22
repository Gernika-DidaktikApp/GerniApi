from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ActividadEstadoCreate(BaseModel):
    id_juego: str = Field(..., min_length=36, max_length=36)
    id_actividad: str = Field(..., min_length=36, max_length=36)


class ActividadEstadoUpdate(BaseModel):
    duracion: Optional[int] = None
    fecha_fin: Optional[datetime] = None
    estado: Optional[str] = Field(None, max_length=20)
    puntuacion_total: Optional[float] = None


class ActividadEstadoResponse(BaseModel):
    id: str
    id_juego: str
    id_actividad: str
    fecha_inicio: datetime
    duracion: Optional[int] = None
    fecha_fin: Optional[datetime] = None
    estado: str
    puntuacion_total: Optional[float] = None

    class Config:
        from_attributes = True
