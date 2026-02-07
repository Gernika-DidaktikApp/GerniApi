from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# Schemas base
class AuditLogBase(BaseModel):
    """Schema base para audit logs."""

    usuario_id: str | None = Field(None, min_length=36, max_length=36)
    profesor_id: str | None = Field(None, min_length=36, max_length=36)
    accion: str = Field(..., min_length=1, max_length=100, description="Acción realizada")
    detalles: str | None = Field(None, description="Detalles adicionales de la acción")


# Schemas para crear logs web
class AuditLogWebCreate(AuditLogBase):
    """Schema para crear un audit log desde la web."""

    ip_address: str | None = Field(None, max_length=45, description="Dirección IP del usuario")
    user_agent: str | None = Field(None, max_length=500, description="User agent del navegador")
    browser: str | None = Field(None, max_length=100, description="Nombre del navegador")


# Schemas para crear logs app
class AuditLogAppCreate(AuditLogBase):
    """Schema para crear un audit log desde la app móvil."""

    device_type: str | None = Field(
        None, max_length=50, description="Tipo de dispositivo (iOS, Android)"
    )
    app_version: str | None = Field(None, max_length=20, description="Versión de la aplicación")
    device_id: str | None = Field(None, max_length=100, description="Identificador del dispositivo")


# Schema de respuesta
class AuditLogResponse(BaseModel):
    """Schema de respuesta para audit logs (polimórfico)."""

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
