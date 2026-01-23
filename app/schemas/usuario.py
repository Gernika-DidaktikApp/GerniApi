from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LoginAppRequest(BaseModel):
    """Credenciales para autenticación de usuario"""

    username: str = Field(..., description="Nombre de usuario", example="usuario123")
    password: str = Field(..., description="Contraseña del usuario", example="password123")

    model_config = {
        "json_schema_extra": {"examples": [{"username": "usuario123", "password": "password123"}]}
    }


class UsuarioCreate(BaseModel):
    """Datos para crear un nuevo usuario"""

    username: str = Field(
        ...,
        min_length=3,
        max_length=45,
        description="Nombre de usuario único",
        example="usuario123",
    )
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=45,
        description="Nombre del usuario",
        example="Juan",
    )
    apellido: str = Field(
        ...,
        min_length=1,
        max_length=45,
        description="Apellido del usuario",
        example="Pérez",
    )
    password: str = Field(
        ...,
        min_length=4,
        max_length=100,
        description="Contraseña (será hasheada con bcrypt)",
        example="password123",
    )
    id_clase: Optional[str] = Field(
        None,
        description="ID de la clase asignada (opcional)",
        example="550e8400-e29b-41d4-a716-446655440000",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "usuario123",
                    "nombre": "Juan",
                    "apellido": "Pérez",
                    "password": "password123",
                    "id_clase": None,
                }
            ]
        }
    }


class UsuarioUpdate(BaseModel):
    """Datos para actualizar un usuario existente (todos los campos son opcionales)"""

    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=45,
        description="Nuevo username",
        example="usuario_nuevo",
    )
    nombre: Optional[str] = Field(
        None, min_length=1, max_length=45, description="Nuevo nombre", example="Pedro"
    )
    apellido: Optional[str] = Field(
        None,
        min_length=1,
        max_length=45,
        description="Nuevo apellido",
        example="García",
    )
    password: Optional[str] = Field(
        None,
        min_length=4,
        max_length=100,
        description="Nueva contraseña",
        example="newpassword123",
    )
    id_clase: Optional[str] = Field(
        None,
        description="Nueva clase asignada",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    top_score: Optional[int] = Field(None, description="Nueva puntuación máxima", example=1500)

    model_config = {"json_schema_extra": {"examples": [{"nombre": "Pedro", "apellido": "García"}]}}


class LoginAppResponse(BaseModel):
    """Respuesta de login con token y datos del usuario"""

    access_token: str = Field(..., description="Token JWT para autenticación")
    token_type: str = Field(default="bearer", description="Tipo de token")
    user_id: str = Field(..., description="ID único del usuario (UUID)")
    username: str = Field(..., description="Nombre de usuario")
    nombre: str = Field(..., description="Nombre del usuario")
    apellido: str = Field(..., description="Apellido del usuario")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "usuario123",
                    "nombre": "Juan",
                    "apellido": "Pérez",
                }
            ]
        }
    }


class UsuarioResponse(BaseModel):
    """Respuesta con los datos del usuario (sin contraseña)"""

    id: str = Field(
        ...,
        description="ID único del usuario (UUID)",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    username: str = Field(..., description="Nombre de usuario", example="usuario123")
    nombre: str = Field(..., description="Nombre", example="Juan")
    apellido: str = Field(..., description="Apellido", example="Pérez")
    id_clase: Optional[str] = Field(
        None,
        description="ID de la clase asignada",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    creation: datetime = Field(
        ..., description="Fecha de creación de la cuenta", example="2024-01-15T10:30:00"
    )
    top_score: int = Field(..., description="Puntuación máxima alcanzada", example=1000)

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "usuario123",
                    "nombre": "Juan",
                    "apellido": "Pérez",
                    "id_clase": None,
                    "creation": "2024-01-15T10:30:00",
                    "top_score": 1000,
                }
            ]
        },
    }
