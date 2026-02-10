"""Schemas Pydantic para gestión de partidas.

Este módulo define los modelos de validación y serialización para todas las
operaciones relacionadas con partidas de juego (sesiones de usuario).

Autor: Gernibide
"""

from datetime import datetime

from pydantic import BaseModel, Field


class PartidaCreate(BaseModel):
    """Datos para crear una nueva partida.

    Modelo de validación para iniciar una nueva partida/sesión de juego.
    La fecha de inicio se establece automáticamente.

    Attributes:
        id_usuario: ID del usuario que inicia la partida (UUID, 36 caracteres).
    """

    id_usuario: str = Field(..., min_length=36, max_length=36)


class PartidaUpdate(BaseModel):
    """Datos para actualizar una partida existente.

    Modelo de validación para actualización parcial de partidas. Todos los campos
    son opcionales. La duración se calcula automáticamente al establecer fecha_fin.

    Attributes:
        fecha_fin: Fecha y hora de finalización de la partida, opcional.
        duracion: Duración de la partida en segundos, opcional.
        estado: Estado de la partida (máximo 20 caracteres), opcional.
    """

    fecha_fin: datetime | None = None
    duracion: int | None = None
    estado: str | None = Field(None, max_length=20)


class PartidaResponse(BaseModel):
    """Respuesta con los datos de la partida.

    Modelo de respuesta con información completa de la partida/sesión de juego.

    Attributes:
        id: ID único de la partida (UUID).
        id_usuario: ID del usuario que jugó la partida (UUID).
        fecha_inicio: Fecha y hora de inicio de la partida.
        fecha_fin: Fecha y hora de finalización de la partida, puede ser None.
        duracion: Duración de la partida en segundos, puede ser None.
        estado: Estado actual de la partida.
    """

    id: str
    id_usuario: str
    fecha_inicio: datetime
    fecha_fin: datetime | None = None
    duracion: int | None = None
    estado: str

    class Config:
        from_attributes = True
