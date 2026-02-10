"""Schemas Pydantic para gestión de logs de auditoría.

Este módulo define los modelos de validación y serialización para el registro
de acciones de usuarios y profesores, tanto desde web como desde app móvil.

Autor: Gernibide
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# Schemas base
class AuditLogBase(BaseModel):
    """Schema base para audit logs.

    Modelo base abstracto que contiene los campos comunes a todos los tipos
    de logs de auditoría.

    Attributes:
        usuario_id: ID del usuario que realiza la acción (UUID), opcional.
        profesor_id: ID del profesor que realiza la acción (UUID), opcional.
        accion: Descripción de la acción realizada (1-100 caracteres).
        detalles: Información adicional sobre la acción, opcional.
    """

    usuario_id: str | None = Field(None, min_length=36, max_length=36)
    profesor_id: str | None = Field(None, min_length=36, max_length=36)
    accion: str = Field(..., min_length=1, max_length=100, description="Acción realizada")
    detalles: str | None = Field(None, description="Detalles adicionales de la acción")


# Schemas para crear logs web
class AuditLogWebCreate(AuditLogBase):
    """Schema para crear un audit log desde la web.

    Modelo de validación para registrar acciones realizadas desde la interfaz
    web del dashboard de profesores.

    Attributes:
        ip_address: Dirección IP del usuario (máximo 45 caracteres), opcional.
        user_agent: User agent del navegador (máximo 500 caracteres), opcional.
        browser: Nombre del navegador (máximo 100 caracteres), opcional.
    """

    ip_address: str | None = Field(None, max_length=45, description="Dirección IP del usuario")
    user_agent: str | None = Field(None, max_length=500, description="User agent del navegador")
    browser: str | None = Field(None, max_length=100, description="Nombre del navegador")


# Schemas para crear logs app
class AuditLogAppCreate(AuditLogBase):
    """Schema para crear un audit log desde la app móvil.

    Modelo de validación para registrar acciones realizadas desde la aplicación
    móvil de estudiantes.

    Attributes:
        device_type: Tipo de dispositivo móvil (iOS, Android, máximo 50 caracteres), opcional.
        app_version: Versión de la aplicación (máximo 20 caracteres), opcional.
        device_id: Identificador único del dispositivo (máximo 100 caracteres), opcional.
    """

    device_type: str | None = Field(
        None, max_length=50, description="Tipo de dispositivo (iOS, Android)"
    )
    app_version: str | None = Field(None, max_length=20, description="Versión de la aplicación")
    device_id: str | None = Field(None, max_length=100, description="Identificador del dispositivo")


# Schema de respuesta
class AuditLogResponse(BaseModel):
    """Schema de respuesta para audit logs.

    Modelo de respuesta polimórfico que incluye todos los campos posibles tanto
    para logs web como app móvil.

    Attributes:
        id: ID único del log (UUID).
        timestamp: Fecha y hora del registro.
        usuario_id: ID del usuario, puede ser None.
        profesor_id: ID del profesor, puede ser None.
        accion: Descripción de la acción realizada.
        detalles: Información adicional, puede ser None.
        tipo: Tipo de log ("web" o "app").
        ip_address: Dirección IP (solo logs web), puede ser None.
        user_agent: User agent del navegador (solo logs web), puede ser None.
        browser: Nombre del navegador (solo logs web), puede ser None.
        device_type: Tipo de dispositivo (solo logs app), puede ser None.
        app_version: Versión de la app (solo logs app), puede ser None.
        device_id: ID del dispositivo (solo logs app), puede ser None.
    """

    id: str
    timestamp: datetime
    usuario_id: str | None = None
    profesor_id: str | None = None
    accion: str
    detalles: str | None = None
    tipo: Literal["web", "app"]

    # Campos opcionales según el tipo
    ip_address: str | None = None
    user_agent: str | None = None
    browser: str | None = None
    device_type: str | None = None
    app_version: str | None = None
    device_id: str | None = None

    class Config:
        from_attributes = True
