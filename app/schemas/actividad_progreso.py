from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ActividadProgresoCreate(BaseModel):
    id_juego: str = Field(..., min_length=36, max_length=36)
    id_punto: str = Field(..., min_length=36, max_length=36)
    id_actividad: str = Field(..., min_length=36, max_length=36)


class ActividadProgresoUpdate(BaseModel):
    duracion: Optional[int] = None
    fecha_fin: Optional[datetime] = None
    estado: Optional[str] = Field(None, max_length=20)
    puntuacion: Optional[float] = None
    respuesta_contenido: Optional[str] = Field(None, description="Texto largo o URL de imagen del usuario")


class ActividadProgresoCompletar(BaseModel):
    puntuacion: float = Field(..., description="Puntuación obtenida en la actividad")
    device_type: Optional[str] = Field(
        None, max_length=50, description="Tipo de dispositivo (iOS, Android)"
    )
    app_version: Optional[str] = Field(None, max_length=20, description="Versión de la aplicación")


class ActividadProgresoResponse(BaseModel):
    id: str
    id_juego: str
    id_punto: str
    id_actividad: str
    fecha_inicio: datetime
    duracion: Optional[int] = None
    fecha_fin: Optional[datetime] = None
    estado: str
    puntuacion: Optional[float] = None
    respuesta_contenido: Optional[str] = None

    class Config:
        from_attributes = True


class PuntoResumen(BaseModel):
    """Resumen calculado de un punto (desde actividad_progreso)"""

    id_juego: str
    id_punto: str
    nombre_punto: Optional[str] = None
    actividades_totales: int
    actividades_completadas: int
    actividades_en_progreso: int
    puntuacion_total: float
    duracion_total: Optional[int] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    estado: str  # "no_iniciada", "en_progreso", "completada"
