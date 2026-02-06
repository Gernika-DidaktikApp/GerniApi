from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# Schemas base
class AuditLogBase(BaseModel):
    """Schema base para audit logs."""

    usuario_id: Optional[str] = Field(None, min_length=36, max_length=36)
    profesor_id: Optional[str] = Field(None, min_length=36, max_length=36)
    accion: str = Field(..., min_length=1, max_length=100, description="Acción realizada")
    detalles: Optional[str] = Field(None, description="Detalles adicionales de la acción")


# Schemas para crear logs web
class AuditLogWebCreate(AuditLogBase):
    """Schema para crear un audit log desde la web."""

    ip_address: Optional[str] = Field(None, max_length=45, description="Dirección IP del usuario")
    user_agent: Optional[str] = Field(None, max_length=500, description="User agent del navegador")
    browser: Optional[str] = Field(None, max_length=100, description="Nombre del navegador")


# Schemas para crear logs app
class AuditLogAppCreate(AuditLogBase):
    """Schema para crear un audit log desde la app móvil."""

    device_type: Optional[str] = Field(
        None, max_length=50, description="Tipo de dispositivo (iOS, Android)"
    )
    app_version: Optional[str] = Field(None, max_length=20, description="Versión de la aplicación")
    device_id: Optional[str] = Field(
        None, max_length=100, description="Identificador del dispositivo"
    )


# Schema de respuesta
class AuditLogResponse(BaseModel):
    """Schema de respuesta para audit logs (polimórfico)."""

    id: str
    timestamp: datetime
    usuario_id: Optional[str] = None
    profesor_id: Optional[str] = None
    accion: str
    detalles: Optional[str] = None
    tipo: Literal["web", "app"]

    # Campos opcionales según el tipo
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    browser: Optional[str] = None
    device_type: Optional[str] = None
    app_version: Optional[str] = None
    device_id: Optional[str] = None

    class Config:
        from_attributes = True
