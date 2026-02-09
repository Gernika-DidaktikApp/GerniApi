from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.juego import Partida
from app.models.usuario import Usuario
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login-app", auto_error=False)


@dataclass
class AuthResult:
    """Resultado de autenticación que indica el tipo de auth y el usuario si aplica."""

    is_api_key: bool
    user: Usuario | None = None
    user_id: str | None = None


def verify_api_key(
    api_key: str | None = Header(None, alias="X-API-Key"),
) -> str | None:
    """Verifica si el API Key proporcionado es válido."""
    if api_key and api_key == settings.API_KEY:
        return api_key
    return None


def get_current_user(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario | None:
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


def require_api_key_only(api_key: str | None = Depends(verify_api_key)) -> str:
    """Requiere API Key válida. Rechaza cualquier otro tipo de autenticación."""
    if not api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="API Key requerida")
    return api_key


def require_auth(
    api_key: str | None = Depends(verify_api_key),
    user: Usuario | None = Depends(get_current_user),
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
            detail="No tienes permiso para acceder a este recurso",
        )


def validate_partida_ownership(auth: AuthResult, partida_id: str, db: Session) -> Partida:
    """
    Valida que el usuario autenticado es dueño de la partida.
    Retorna la partida si la validación es exitosa.
    """
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La partida especificada no existe",
        )

    if auth.is_api_key:
        return partida  # API Key tiene acceso total

    if partida.id_usuario != auth.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta partida",
        )

    return partida


# ============================================================
# Dependency Injection para Repositorios y Servicios
# ============================================================


def get_usuario_repository(db: Session = Depends(get_db)):
    """Inyecta UsuarioRepository con sesión de BD."""
    from app.repositories import UsuarioRepository

    return UsuarioRepository(db)


def get_clase_repository(db: Session = Depends(get_db)):
    """Inyecta ClaseRepository con sesión de BD."""
    from app.repositories import ClaseRepository

    return ClaseRepository(db)


def get_partida_repository(db: Session = Depends(get_db)):
    """Inyecta PartidaRepository con sesión de BD."""
    from app.repositories import PartidaRepository

    return PartidaRepository(db)


def get_actividad_progreso_repository(db: Session = Depends(get_db)):
    """Inyecta ActividadProgresoRepository con sesión de BD."""
    from app.repositories import ActividadProgresoRepository

    return ActividadProgresoRepository(db)


def get_punto_repository(db: Session = Depends(get_db)):
    """Inyecta PuntoRepository con sesión de BD."""
    from app.repositories import PuntoRepository

    return PuntoRepository(db)


def get_actividad_repository(db: Session = Depends(get_db)):
    """Inyecta ActividadRepository con sesión de BD."""
    from app.repositories import ActividadRepository

    return ActividadRepository(db)


def get_usuario_service(
    usuario_repo=Depends(get_usuario_repository),
    clase_repo=Depends(get_clase_repository),
):
    """Inyecta UsuarioService con repositorios necesarios."""
    from app.services.usuario_service import UsuarioService

    return UsuarioService(usuario_repo, clase_repo)


def get_usuario_stats_service(
    partida_repo=Depends(get_partida_repository),
    actividad_repo=Depends(get_actividad_progreso_repository),
    punto_repo=Depends(get_punto_repository),
):
    """Inyecta UsuarioStatsService con repositorios necesarios."""
    from app.services.usuario_stats_service import UsuarioStatsService

    return UsuarioStatsService(partida_repo, actividad_repo, punto_repo)


def get_usuario_perfil_service(
    usuario_repo=Depends(get_usuario_repository),
    partida_repo=Depends(get_partida_repository),
    punto_repo=Depends(get_punto_repository),
    actividad_repo=Depends(get_actividad_repository),
    actividad_progreso_repo=Depends(get_actividad_progreso_repository),
):
    """Inyecta UsuarioPerfilService con repositorios necesarios."""
    from app.services.usuario_perfil_service import UsuarioPerfilService

    return UsuarioPerfilService(
        usuario_repo,
        partida_repo,
        punto_repo,
        actividad_repo,
        actividad_progreso_repo,
    )
