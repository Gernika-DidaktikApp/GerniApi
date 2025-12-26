from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models.alumno import Alumno
from app.schemas.alumno import LoginRequest, Token, AlumnoResponse
from app.utils.security import create_access_token
from app.config import settings
from app.logging import logger, log_with_context

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    # Log de intento de inicio de sesión
    log_with_context(
        "info",
        "Intento de inicio de sesión",
        nombre=login_data.nombre,
        client_ip=request.client.host if request.client else "unknown"
    )

    # Buscar alumno por nombre
    logger.debug(f"Buscando alumno en base de datos: {login_data.nombre}")
    alumno = db.query(Alumno).filter(Alumno.nombre == login_data.nombre).first()

    # Verificar que existe y la contraseña coincide
    if not alumno or alumno.contrasenya != login_data.contrasenya:
        # Log de fallo de autenticación
        log_with_context(
            "warning",
            "Intento de login fallido",
            nombre=login_data.nombre,
            reason="Credenciales inválidas",
            client_ip=request.client.host if request.client else "unknown"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token
    logger.debug(f"Generando token de acceso para: {alumno.nombre}")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": alumno.nombre},
        expires_delta=access_token_expires
    )

    # Log de autenticación exitosa
    log_with_context(
        "info",
        "Usuario autenticado correctamente",
        usuario=alumno.usuario,
        nombre=alumno.nombre,
        client_ip=request.client.host if request.client else "unknown"
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=AlumnoResponse)
def get_current_alumno(
    alumno: Alumno = Depends(lambda: __import__('app.utils.dependencies', fromlist=['get_current_user']).get_current_user)
):
    # Log de consulta de información del usuario
    logger.debug(f"Consultando información del usuario: {alumno.nombre}")

    log_with_context(
        "info",
        "Usuario consultó su información",
        usuario=alumno.usuario,
        nombre=alumno.nombre
    )

    return alumno
