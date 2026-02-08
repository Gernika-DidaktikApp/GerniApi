"""Schemas Pydantic para gestión de clases.

Este módulo define los modelos de validación y serialización para todas las
operaciones relacionadas con clases (grupos de estudiantes).

Autor: Gernibide
"""

from pydantic import BaseModel, Field


class ClaseCreate(BaseModel):
    """Datos para crear una nueva clase.

    Modelo de validación para la creación de clases/grupos de estudiantes.

    Attributes:
        id_profesor: ID del profesor propietario de la clase (UUID, 36 caracteres).
        nombre: Nombre de la clase (1-100 caracteres).
    """

    id_profesor: str = Field(..., min_length=36, max_length=36)
    nombre: str = Field(..., min_length=1, max_length=100)


class ClaseUpdate(BaseModel):
    """Datos para actualizar una clase existente.

    Modelo de validación para actualización parcial de clases. Todos los campos
    son opcionales.

    Attributes:
        id_profesor: Nuevo ID del profesor propietario (UUID, 36 caracteres), opcional.
        nombre: Nuevo nombre de la clase (1-100 caracteres), opcional.
    """

    id_profesor: str | None = Field(None, min_length=36, max_length=36)
    nombre: str | None = Field(None, min_length=1, max_length=100)


class ClaseResponse(BaseModel):
    """Respuesta con los datos de la clase.

    Modelo de respuesta con información completa de la clase.

    Attributes:
        id: ID único de la clase (UUID).
        id_profesor: ID del profesor propietario de la clase (UUID).
        nombre: Nombre de la clase.
    """

    id: str
    id_profesor: str
    nombre: str

    class Config:
        from_attributes = True
