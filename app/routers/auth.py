from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models.alumno import Alumno
from app.schemas.alumno import LoginRequest, Token, AlumnoResponse
from app.utils.security import create_access_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    # Buscar alumno por usuario
    alumno = db.query(Alumno).filter(Alumno.usuario == login_data.usuario).first()

    # Verificar que existe y la contraseña coincide
    if not alumno or alumno.contrasenya != login_data.contrasenya:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": alumno.usuario},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=AlumnoResponse)
def get_current_alumno(
    alumno: Alumno = Depends(lambda: __import__('app.utils.dependencies', fromlist=['get_current_user']).get_current_user)
):
    return alumno
