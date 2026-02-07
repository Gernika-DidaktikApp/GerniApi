from pydantic import BaseModel, Field


class PuntoCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)


class PuntoUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=100)


class PuntoResponse(BaseModel):
    id: str
    nombre: str

    class Config:
        from_attributes = True
