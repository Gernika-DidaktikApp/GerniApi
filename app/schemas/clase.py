from pydantic import BaseModel, Field


class ClaseCreate(BaseModel):
    id_profesor: str = Field(..., min_length=36, max_length=36)
    nombre: str = Field(..., min_length=1, max_length=100)


class ClaseUpdate(BaseModel):
    id_profesor: str | None = Field(None, min_length=36, max_length=36)
    nombre: str | None = Field(None, min_length=1, max_length=100)


class ClaseResponse(BaseModel):
    id: str
    id_profesor: str
    nombre: str

    class Config:
        from_attributes = True
