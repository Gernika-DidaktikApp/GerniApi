"""Schemas Pydantic para gestión de puntos de interés.

Este módulo define los modelos de validación y serialización para todas las
operaciones relacionadas con puntos de interés geográficos del juego.

Autor: Gernibide
"""

from pydantic import BaseModel, Field


class PuntoCreate(BaseModel):
    """Datos para crear un nuevo punto de interés.

    Modelo de validación para la creación de puntos de interés geográficos
    donde se ubican actividades educativas.

    Attributes:
        nombre: Nombre del punto de interés (1-100 caracteres).
    """

    nombre: str = Field(..., min_length=1, max_length=100)


class PuntoUpdate(BaseModel):
    """Datos para actualizar un punto de interés existente.

    Modelo de validación para actualización parcial de puntos. Todos los campos
    son opcionales.

    Attributes:
        nombre: Nuevo nombre del punto de interés (1-100 caracteres), opcional.
    """

    nombre: str | None = Field(None, min_length=1, max_length=100)


class PuntoResponse(BaseModel):
    """Respuesta con los datos del punto de interés.

    Modelo de respuesta con información completa del punto de interés.

    Attributes:
        id: ID único del punto (UUID).
        nombre: Nombre del punto de interés.
    """

    id: str
    nombre: str

    class Config:
        from_attributes = True
