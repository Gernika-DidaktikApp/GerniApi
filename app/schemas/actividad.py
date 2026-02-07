from pydantic import BaseModel, Field


class ActividadCreate(BaseModel):
    id_punto: str = Field(..., min_length=36, max_length=36)
    nombre: str = Field(..., min_length=1, max_length=100)


class ActividadUpdate(BaseModel):
    id_punto: str | None = Field(None, min_length=36, max_length=36)
    nombre: str | None = Field(None, min_length=1, max_length=100)


class ActividadResponse(BaseModel):
    id: str
    id_punto: str
    nombre: str

    class Config:
        from_attributes = True
