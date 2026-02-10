"""Schemas Pydantic para gestión de actividades.

Este módulo define los modelos de validación y serialización para todas las
operaciones relacionadas con actividades educativas del juego.

Autor: Gernibide
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ActividadCreate(BaseModel):
    """Datos para crear una nueva actividad.

    Modelo de validación para la creación de actividades educativas dentro
    de un punto de interés.

    Attributes:
        id_punto: ID del punto al que pertenece la actividad (UUID, 36 caracteres).
        nombre: Nombre de la actividad (1-100 caracteres).
    """

    id_punto: str = Field(..., min_length=36, max_length=36)
    nombre: str = Field(..., min_length=1, max_length=100)


class ActividadUpdate(BaseModel):
    """Datos para actualizar una actividad existente.

    Modelo de validación para actualización parcial de actividades. Todos los
    campos son opcionales.

    Attributes:
        id_punto: Nuevo ID del punto al que pertenece (UUID, 36 caracteres), opcional.
        nombre: Nuevo nombre de la actividad (1-100 caracteres), opcional.
    """

    id_punto: str | None = Field(None, min_length=36, max_length=36)
    nombre: str | None = Field(None, min_length=1, max_length=100)


class ActividadResponse(BaseModel):
    """Respuesta con los datos de la actividad.

    Modelo de respuesta con información completa de la actividad educativa.

    Attributes:
        id: ID único de la actividad (UUID).
        id_punto: ID del punto al que pertenece la actividad (UUID).
        nombre: Nombre de la actividad.
    """

    id: str
    id_punto: str
    nombre: str

    class Config:
        from_attributes = True


class RespuestaPublica(BaseModel):
    """Respuesta pública de un alumno en una actividad.

    Attributes:
        mensaje: Contenido de la respuesta del alumno.
        fecha: Fecha y hora de completado.
        usuario: Nombre del usuario (opcional, puede ser anónimo).
    """

    mensaje: str
    fecha: datetime
    usuario: str | None = None


class RespuestasPublicasResponse(BaseModel):
    """Respuesta con lista de respuestas públicas de una actividad.

    Attributes:
        actividad_id: ID de la actividad consultada.
        actividad_nombre: Nombre de la actividad.
        total_respuestas: Número total de respuestas disponibles.
        respuestas: Lista de respuestas públicas.
    """

    actividad_id: str
    actividad_nombre: str
    total_respuestas: int
    respuestas: list[RespuestaPublica]
