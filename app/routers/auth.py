"""Router de autenticación para usuarios y profesores.

Este módulo maneja los endpoints de login para usuarios de la app móvil
y profesores de la interfaz web, generando tokens JWT para autenticación.

Autor: Gernibide
"""

import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.logging import log_auth, log_debug
from app.models.audit_log import AuditLogWeb
from app.models.profesor import Profesor

# from app.models.alumno import Alumno  # Comentado - modelo no existe
from app.models.usuario import Usuario

# from app.schemas.alumno import LoginRequest, Token, AlumnoResponse  # Comentado
from app.schemas.usuario import LoginAppRequest, LoginAppResponse
from app.utils.security import create_access_token, verify_password


# Schema temporal para Token
class Token(BaseModel):
    """Schema para respuesta de token JWT.

    Attributes:
        access_token: Token JWT generado.
        token_type: Tipo de token (siempre "bearer").
    """

    access_token: str
    token_type: str


# Schema para respuesta de login profesor
class LoginProfesorResponse(BaseModel):
    """Schema para respuesta de login de profesor.

    Attributes:
        access_token: Token JWT generado.
        token_type: Tipo de token (siempre "bearer").
        profesor_id: ID único del profesor.
        username: Nombre de usuario del profesor.
        nombre: Nombre del profesor.
        apellido: Apellido del profesor.
    """

    access_token: str
    token_type: str
    profesor_id: str
    username: str
    nombre: str
    apellido: str


router = APIRouter(
    prefix="/auth",
    tags=["🔐 Autenticación"],
    responses={
        401: {"description": "Credenciales inválidas"},
        422: {"description": "Error de validación en los datos enviados"},
    },
)


def _extract_browser(user_agent: str | None) -> str | None:
    """Extrae el nombre del navegador del user-agent.

    Args:
        user_agent: String del user-agent HTTP.

    Returns:
        Nombre del navegador detectado o "Unknown" si no se reconoce.
        None si no se proporciona user_agent.
    """
    if not user_agent:
        return None

    user_agent = user_agent.lower()
    if "edg" in user_agent:
        return "Edge"
    elif "chrome" in user_agent:
        return "Chrome"
    elif "safari" in user_agent and "chrome" not in user_agent:
        return "Safari"
    elif "firefox" in user_agent:
        return "Firefox"
    elif "opera" in user_agent or "opr" in user_agent:
        return "Opera"
    else:
        return "Unknown"


@router.post(
    "/login-app",
    response_model=LoginAppResponse,
    summary="Login de usuario",
    description="Autenticar usuario con username y contraseña. Devuelve un token JWT válido por 30 minutos junto con los datos del usuario.",
    responses={
        200: {
            "description": "Login exitoso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "usuario123",
                        "nombre": "Juan",
                        "apellido": "Pérez",
                    }
                }
            },
        },
        401: {
            "description": "Credenciales incorrectas",
            "content": {
                "application/json": {"example": {"detail": "Username o contraseña incorrectos"}}
            },
        },
    },
)
def login_app(login_data: LoginAppRequest, request: Request, db: Session = Depends(get_db)):
    """
    ## Autenticar Usuario

    Valida las credenciales del usuario y devuelve un token JWT.

    ### Parámetros
    - **username**: Nombre de usuario único
    - **password**: Contraseña del usuario

    ### Respuesta Exitosa
    - **access_token**: Token JWT para autenticación
    - **token_type**: Tipo de token (siempre "bearer")

    ### Uso del Token
    Incluye el token en el header de las peticiones:
    ```
    Authorization: Bearer <access_token>
    ```

    ### Notas
    - El token expira en 30 minutos
    - La contraseña se valida con bcrypt
    - Se registra cada intento de login en los logs
    """
    client_ip = request.client.host if request.client else "unknown"

    # Log de intento de inicio de sesión
    log_auth("login_attempt", username=login_data.username, success=True, client_ip=client_ip)

    # Buscar usuario por username
    log_debug("Buscando usuario en BD", username=login_data.username)
    usuario = db.query(Usuario).filter(Usuario.username == login_data.username).first()

    # Verificar que el usuario existe
    if not usuario:
        log_auth(
            "login_failed",
            username=login_data.username,
            success=False,
            reason="Usuario no encontrado",
            client_ip=client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El usuario no existe",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que la contraseña es correcta
    if not verify_password(login_data.password, usuario.password):
        log_auth(
            "login_failed",
            username=login_data.username,
            success=False,
            reason="Contraseña incorrecta",
            client_ip=client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token
    log_debug("Generando token de acceso", username=usuario.username)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.username}, expires_delta=access_token_expires
    )

    # Log de autenticación exitosa
    log_auth(
        "login_success",
        username=usuario.username,
        success=True,
        usuario_id=usuario.id,
        client_ip=client_ip,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": usuario.id,
        "username": usuario.username,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
    }


# Comentado temporalmente - requiere modelo Alumno
# @router.get("/me", response_model=AlumnoResponse)
# def get_current_alumno(...):


@router.post(
    "/login-profesor",
    response_model=LoginProfesorResponse,
    summary="Login de profesor",
    description="Autenticar profesor con username y contraseña. Devuelve un token JWT válido por 30 minutos junto con datos del profesor.",
    responses={
        200: {
            "description": "Login exitoso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "profesor_id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "admin",
                        "nombre": "Profesor",
                        "apellido": "Admin",
                    }
                }
            },
        },
        401: {
            "description": "Credenciales incorrectas",
            "content": {
                "application/json": {"example": {"detail": "Username o contraseña incorrectos"}}
            },
        },
    },
)
def login_profesor(login_data: LoginAppRequest, request: Request, db: Session = Depends(get_db)):
    """
    ## Autenticar Profesor

    Valida las credenciales del profesor y devuelve un token JWT.

    ### Parámetros
    - **username**: Nombre de usuario único del profesor
    - **password**: Contraseña del profesor

    ### Respuesta Exitosa
    - **access_token**: Token JWT para autenticación
    - **token_type**: Tipo de token (siempre "bearer")
    """
    client_ip = request.client.host if request.client else "unknown"

    log_auth(
        "login_profesor_attempt",
        username=login_data.username,
        success=True,
        client_ip=client_ip,
    )

    # Buscar profesor por username
    log_debug("Buscando profesor en BD", username=login_data.username)
    profesor = db.query(Profesor).filter(Profesor.username == login_data.username).first()

    # Verificar que existe y la contraseña coincide
    if not profesor or not verify_password(login_data.password, profesor.password):
        log_auth(
            "login_profesor_failed",
            username=login_data.username,
            success=False,
            reason="Credenciales inválidas",
            client_ip=client_ip,
        )

        # Crear audit log de fallo de login (Web)
        audit_log_fallo = AuditLogWeb(
            id=str(uuid.uuid4()),
            profesor_id=None,  # No sabemos el ID si falló el login
            accion="login_fallo",
            detalles=f"Intento de login fallido para usuario '{login_data.username}'",
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            browser=_extract_browser(request.headers.get("user-agent")),
        )
        db.add(audit_log_fallo)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token
    log_debug("Generando token de acceso para profesor", username=profesor.username)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": profesor.username, "type": "profesor"},
        expires_delta=access_token_expires,
    )

    log_auth(
        "login_profesor_success",
        username=profesor.username,
        success=True,
        profesor_id=profesor.id,
        client_ip=client_ip,
    )

    # Crear audit log de login exitoso (Web)
    audit_log_exito = AuditLogWeb(
        id=str(uuid.uuid4()),
        profesor_id=profesor.id,
        accion="login_exitoso",
        detalles=f"Login exitoso desde web para profesor '{profesor.username}'",
        ip_address=client_ip,
        user_agent=request.headers.get("user-agent"),
        browser=_extract_browser(request.headers.get("user-agent")),
    )
    db.add(audit_log_exito)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "profesor_id": profesor.id,
        "username": profesor.username,
        "nombre": profesor.nombre,
        "apellido": profesor.apellido,
    }
