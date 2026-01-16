from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class EventoEstadoCreate(BaseModel):
    id_juego: str = Field(..., min_length=36, max_length=36)
    id_actividad: str = Field(..., min_length=36, max_length=36)
    estado: Optional[Any] = None

class EventoEstadoUpdate(BaseModel):
    duracion: Optional[int] = None
    fecha_fin: Optional[datetime] = None
    estado: Optional[Any] = None

class EventoEstadoResponse(BaseModel):
    id: str
    id_juego: str
    id_actividad: str
    fecha_inicio: datetime
    duracion: Optional[int] = None
    fecha_fin: Optional[datetime] = None
    estado: Optional[Any] = None

    class Config:
        from_attributes = True
