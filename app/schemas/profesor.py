"""Schemas Pydantic para gestión de profesores.

Este módulo define los modelos de validación y serialización para todas las
operaciones relacionadas con profesores (administradores del sistema).

Autor: Gernibide
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ProfesorCreate(BaseModel):
    """Datos para crear un nuevo profesor.

    Modelo de validación para la creación de profesores/administradores.
    Requiere todos los campos obligatorios.

    Attributes:
        username: Nombre de usuario único (3-45 caracteres).
        nombre: Nombre del profesor (1-45 caracteres).
        apellido: Apellido del profesor (1-45 caracteres).
        password: Contraseña en texto plano (4-100 caracteres, será hasheada).
    """

    username: str = Field(..., min_length=3, max_length=45)
    nombre: str = Field(..., min_length=1, max_length=45)
    apellido: str = Field(..., min_length=1, max_length=45)
    password: str = Field(..., min_length=4, max_length=100)


class ProfesorUpdate(BaseModel):
    """Datos para actualizar un profesor existente.

    Modelo de validación para actualización parcial de profesores. Todos los
    campos son opcionales, solo se actualizan los campos proporcionados.

    Attributes:
        username: Nuevo nombre de usuario (3-45 caracteres), opcional.
        nombre: Nuevo nombre (1-45 caracteres), opcional.
        apellido: Nuevo apellido (1-45 caracteres), opcional.
        password: Nueva contraseña (4-100 caracteres, será hasheada), opcional.
    """

    username: str | None = Field(None, min_length=3, max_length=45)
    nombre: str | None = Field(None, min_length=1, max_length=45)
    apellido: str | None = Field(None, min_length=1, max_length=45)
    password: str | None = Field(None, min_length=4, max_length=100)


class ProfesorResponse(BaseModel):
    """Respuesta con los datos del profesor.

    Modelo de respuesta con información del profesor, excluyendo la contraseña
    por seguridad.

    Attributes:
        id: ID único del profesor (UUID).
        username: Nombre de usuario.
        nombre: Nombre del profesor.
        apellido: Apellido del profesor.
        created: Fecha y hora de creación de la cuenta.
    """

    id: str
    username: str
    nombre: str
    apellido: str
    created: datetime

    class Config:
        from_attributes = True
