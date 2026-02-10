"""Schemas Pydantic para gestión de progreso de actividades.

Este módulo define los modelos de validación y serialización para el seguimiento
del progreso de los usuarios en actividades educativas durante partidas.

Autor: Gernibide
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ActividadProgresoCreate(BaseModel):
    """Datos para crear un nuevo registro de progreso de actividad.

    Modelo de validación para iniciar el seguimiento de una actividad durante
    una partida. La fecha de inicio se establece automáticamente.

    Attributes:
        id_juego: ID de la partida en curso (UUID, 36 caracteres).
        id_punto: ID del punto de interés donde está la actividad (UUID, 36 caracteres).
        id_actividad: ID de la actividad educativa (UUID, 36 caracteres).
    """

    id_juego: str = Field(..., min_length=36, max_length=36)
    id_punto: str = Field(..., min_length=36, max_length=36)
    id_actividad: str = Field(..., min_length=36, max_length=36)


class ActividadProgresoUpdate(BaseModel):
    """Datos para actualizar el progreso de una actividad.

    Modelo de validación para actualización parcial del progreso. Todos los
    campos son opcionales.

    Attributes:
        duracion: Duración de la actividad en segundos, opcional.
        fecha_fin: Fecha y hora de finalización de la actividad, opcional.
        estado: Estado de la actividad (máximo 20 caracteres), opcional.
        puntuacion: Puntuación obtenida en la actividad, opcional.
        respuesta_contenido: Respuesta del usuario (texto o URL de imagen), opcional.
    """

    duracion: int | None = None
    fecha_fin: datetime | None = None
    estado: str | None = Field(None, max_length=20)
    puntuacion: float | None = None
    respuesta_contenido: str | None = Field(
        None, description="Texto largo o URL de imagen del usuario"
    )


class ActividadProgresoCompletar(BaseModel):
    """Datos para completar una actividad.

    Modelo de validación para marcar una actividad como completada, incluyendo
    puntuación y metadatos opcionales del dispositivo.

    Attributes:
        puntuacion: Puntuación obtenida en la actividad.
        respuesta_contenido: Respuesta del usuario (texto o URL de imagen), opcional.
        device_type: Tipo de dispositivo (iOS, Android, máximo 50 caracteres), opcional.
        app_version: Versión de la aplicación (máximo 20 caracteres), opcional.
    """

    puntuacion: float = Field(..., description="Puntuación obtenida en la actividad")
    respuesta_contenido: str | None = Field(
        None, description="Respuesta del usuario (texto o URL de imagen)"
    )
    device_type: str | None = Field(
        None, max_length=50, description="Tipo de dispositivo (iOS, Android)"
    )
    app_version: str | None = Field(None, max_length=20, description="Versión de la aplicación")


class ActividadProgresoResponse(BaseModel):
    """Respuesta con los datos del progreso de actividad.

    Modelo de respuesta con información completa del progreso de una actividad
    durante una partida.

    Attributes:
        id: ID único del registro de progreso (UUID).
        id_juego: ID de la partida en curso (UUID).
        id_punto: ID del punto de interés (UUID).
        id_actividad: ID de la actividad educativa (UUID).
        fecha_inicio: Fecha y hora de inicio de la actividad.
        duracion: Duración de la actividad en segundos, puede ser None.
        fecha_fin: Fecha y hora de finalización, puede ser None.
        estado: Estado actual de la actividad.
        puntuacion: Puntuación obtenida, puede ser None.
        respuesta_contenido: Respuesta del usuario, puede ser None.
    """

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
    """Resumen calculado del progreso en un punto de interés.

    Modelo de respuesta con estadísticas agregadas del progreso del usuario
    en todas las actividades de un punto específico.

    Attributes:
        id_juego: ID de la partida (UUID).
        id_punto: ID del punto de interés (UUID).
        nombre_punto: Nombre del punto de interés, puede ser None.
        actividades_totales: Número total de actividades en el punto.
        actividades_completadas: Número de actividades completadas.
        actividades_en_progreso: Número de actividades en progreso.
        puntuacion_total: Suma de puntuaciones obtenidas en el punto.
        duracion_total: Duración total en segundos, puede ser None.
        fecha_inicio: Fecha de inicio de la primera actividad, puede ser None.
        fecha_fin: Fecha de fin de la última actividad, puede ser None.
        estado: Estado del punto ("no_iniciada", "en_progreso", "completada").
    """

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
