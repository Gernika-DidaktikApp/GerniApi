from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
# from app.models.alumno import Alumno  # Comentado - modelo no existe
from app.models.usuario import Usuario
# from app.schemas.alumno import LoginRequest, Token, AlumnoResponse  # Comentado
from app.schemas.usuario import LoginAppRequest, UsuarioResponse
from app.utils.security import create_access_token, verify_password
from app.config import settings
from app.logging import logger, log_auth, log_debug
from pydantic import BaseModel

# Schema temporal para Token
class Token(BaseModel):
    access_token: str
    token_type: str

router = APIRouter(
    prefix="/auth",
    tags=["🔐 Autenticación"],
    responses={
        401: {"description": "Credenciales inválidas"},
        422: {"description": "Error de validación en los datos enviados"}
    }
)

@router.post(
    "/login-app",
    response_model=Token,
    summary="Login de usuario",
    description="Autenticar usuario con username y contraseña. Devuelve un token JWT válido por 30 minutos.",
    responses={
        200: {
            "description": "Login exitoso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Credenciales incorrectas",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Username o contraseña incorrectos"
                    }
                }
            }
        }
    }
)
def login_app(
    login_data: LoginAppRequest,
    request: Request,
    db: Session = Depends(get_db)
):
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
    log_debug(f"Buscando usuario en BD", username=login_data.username)
    usuario = db.query(Usuario).filter(Usuario.username == login_data.username).first()

    # Verificar que existe y la contraseña coincide
    if not usuario or not verify_password(login_data.password, usuario.password):
        # Log de fallo de autenticación
        log_auth(
            "login_failed",
            username=login_data.username,
            success=False,
            reason="Credenciales inválidas",
            client_ip=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token
    log_debug("Generando token de acceso", username=usuario.username)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": usuario.username},
        expires_delta=access_token_expires
    )

    # Log de autenticación exitosa
    log_auth(
        "login_success",
        username=usuario.username,
        success=True,
        usuario_id=usuario.id,
        client_ip=client_ip
    )

    return {"access_token": access_token, "token_type": "bearer"}

# Comentado temporalmente - requiere modelo Alumno
# @router.get("/me", response_model=AlumnoResponse)
# def get_current_alumno(...):
