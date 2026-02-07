from datetime import datetime

from pydantic import BaseModel, Field


class ActividadProgresoCreate(BaseModel):
    id_juego: str = Field(..., min_length=36, max_length=36)
    id_punto: str = Field(..., min_length=36, max_length=36)
    id_actividad: str = Field(..., min_length=36, max_length=36)


class ActividadProgresoUpdate(BaseModel):
    duracion: int | None = None
    fecha_fin: datetime | None = None
    estado: str | None = Field(None, max_length=20)
    puntuacion: float | None = None
    respuesta_contenido: str | None = Field(
        None, description="Texto largo o URL de imagen del usuario"
    )


class ActividadProgresoCompletar(BaseModel):
    puntuacion: float = Field(..., description="Puntuación obtenida en la actividad")
    respuesta_contenido: str | None = Field(
        None, description="Respuesta del usuario (texto o URL de imagen)"
    )
    device_type: str | None = Field(
        None, max_length=50, description="Tipo de dispositivo (iOS, Android)"
    )
    app_version: str | None = Field(None, max_length=20, description="Versión de la aplicación")


class ActividadProgresoResponse(BaseModel):
    id: str
    id_juego: str
    id_punto: str
    id_actividad: str
    fecha_inicio: datetime
    duracion: int | None = None
    fecha_fin: datetime | None = None
    estado: str
    puntuacion: float | None = None
    respuesta_contenido: str | None = None

    class Config:
        from_attributes = True


class PuntoResumen(BaseModel):
    """Resumen calculado de un punto (desde actividad_progreso)"""

    id_juego: str
    id_punto: str
    nombre_punto: str | None = None
    actividades_totales: int
    actividades_completadas: int
    actividades_en_progreso: int
    puntuacion_total: float
    duracion_total: int | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    estado: str  # "no_iniciada", "en_progreso", "completada"
