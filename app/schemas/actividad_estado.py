from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ActividadEstadoCreate(BaseModel):
    id_juego: str = Field(..., min_length=36, max_length=36)
    id_actividad: str = Field(..., min_length=36, max_length=36)

class ActividadEstadoUpdate(BaseModel):
    duracion: Optional[int] = None
    fecha_fin: Optional[datetime] = None
    estado: Optional[str] = Field(None, max_length=20)

class ActividadEstadoResponse(BaseModel):
    id: str
    id_juego: str
    id_actividad: str
    fecha_inicio: datetime
    duracion: Optional[int] = None
    fecha_fin: Optional[datetime] = None
    estado: str

    class Config:
        from_attributes = True
