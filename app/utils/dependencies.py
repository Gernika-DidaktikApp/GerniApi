from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.juego import Partida
from app.models.usuario import Usuario
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login-app", auto_error=False)


@dataclass
class AuthResult:
    """Resultado de autenticación que indica el tipo de auth y el usuario si aplica."""
    is_api_key: bool
    user: Optional[Usuario] = None
    user_id: Optional[str] = None


def verify_api_key(api_key: Optional[str] = Header(None, alias="X-API-Key")) -> Optional[str]:
    """Verifica si el API Key proporcionado es válido."""
    if api_key and api_key == settings.API_KEY:
        return api_key
    return None


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[Usuario]:
    """Obtiene el usuario actual del token JWT."""
    if not token:
        return None

    payload = decode_access_token(token)
    if payload is None:
        return None

    username: str = payload.get("sub")
    if username is None:
        return None

    usuario = db.query(Usuario).filter(Usuario.username == username).first()
    return usuario


def require_api_key_only(
    api_key: Optional[str] = Depends(verify_api_key)
) -> str:
    """Requiere API Key válida. Rechaza cualquier otro tipo de autenticación."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key requerida"
        )
    return api_key


def require_auth(
    api_key: Optional[str] = Depends(verify_api_key),
    user: Optional[Usuario] = Depends(get_current_user)
) -> AuthResult:
    """
    Requiere autenticación válida (API Key O Token de usuario).
    Retorna AuthResult con información sobre el tipo de autenticación.
    """
    if api_key:
        return AuthResult(is_api_key=True)

    if user:
        return AuthResult(is_api_key=False, user=user, user_id=user.id)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autenticación requerida",
        headers={"WWW-Authenticate": "Bearer"},
    )


def validate_user_ownership(auth: AuthResult, resource_user_id: str) -> None:
    """
    Valida que el usuario autenticado es dueño del recurso.
    API Key tiene acceso total, Token solo a sus propios recursos.
    """
    if auth.is_api_key:
        return  # API Key tiene acceso total

    if auth.user_id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este recurso"
        )


def validate_partida_ownership(
    auth: AuthResult,
    partida_id: str,
    db: Session
) -> Partida:
    """
    Valida que el usuario autenticado es dueño de la partida.
    Retorna la partida si la validación es exitosa.
    """
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La partida especificada no existe"
        )

    if auth.is_api_key:
        return partida  # API Key tiene acceso total

    if partida.id_usuario != auth.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta partida"
        )

    return partida
