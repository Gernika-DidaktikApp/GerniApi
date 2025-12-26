from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    nombre: str
    contrasenya: str

class Token(BaseModel):
    access_token: str
    token_type: str

class AlumnoResponse(BaseModel):
    usuario: str
    nombre: str
    idioma: Optional[str] = None

    class Config:
        from_attributes = True
