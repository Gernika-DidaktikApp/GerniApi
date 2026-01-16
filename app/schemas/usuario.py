from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LoginAppRequest(BaseModel):
    username: str
    password: str

class UsuarioCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=45)
    nombre: str = Field(..., min_length=1, max_length=45)
    apellido: str = Field(..., min_length=1, max_length=45)
    password: str = Field(..., min_length=4, max_length=100)
    id_clase: Optional[str] = None

class UsuarioUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=45)
    nombre: Optional[str] = Field(None, min_length=1, max_length=45)
    apellido: Optional[str] = Field(None, min_length=1, max_length=45)
    password: Optional[str] = Field(None, min_length=4, max_length=100)
    id_clase: Optional[str] = None
    top_score: Optional[int] = None

class UsuarioResponse(BaseModel):
    id: str
    username: str
    nombre: str
    apellido: str
    id_clase: Optional[str] = None
    creation: datetime
    top_score: int

    class Config:
        from_attributes = True
