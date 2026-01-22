from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PartidaCreate(BaseModel):
    id_usuario: str = Field(..., min_length=36, max_length=36)

class PartidaUpdate(BaseModel):
    fecha_fin: Optional[datetime] = None
    duracion: Optional[int] = None
    estado: Optional[str] = Field(None, max_length=20)

class PartidaResponse(BaseModel):
    id: str
    id_usuario: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    duracion: Optional[int] = None
    estado: str

    class Config:
        from_attributes = True
