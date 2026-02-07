from datetime import datetime

from pydantic import BaseModel, Field


class PartidaCreate(BaseModel):
    id_usuario: str = Field(..., min_length=36, max_length=36)


class PartidaUpdate(BaseModel):
    fecha_fin: datetime | None = None
    duracion: int | None = None
    estado: str | None = Field(None, max_length=20)


class PartidaResponse(BaseModel):
    id: str
    id_usuario: str
    fecha_inicio: datetime
    fecha_fin: datetime | None = None
    duracion: int | None = None
    estado: str

    class Config:
        from_attributes = True
