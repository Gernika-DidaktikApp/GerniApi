"""Router de gestión de audit logs.

Este módulo proporciona endpoints de solo lectura para consultar los registros
de auditoría del sistema. Los audit logs se crean automáticamente y demuestran
el uso de herencia y polimorfismo (AuditLogWeb y AuditLogApp).

Autor: Gernibide
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_with_context
from app.models.profesor import Profesor
from app.models.usuario import Usuario
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_log import AuditLogResponse
from app.utils.dependencies import AuthResult, get_current_profesor, get_current_user, require_auth

router = APIRouter(prefix="/audit-logs", tags=["📋 Audit Logs"])

# Los audit logs se crean automáticamente por el sistema (login, completar puntos, etc.)
# Solo se pueden leer, no crear ni eliminar manualmente


@router.get("", response_model=list[AuditLogResponse])
def listar_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tipo: str = Query(None, description="Filtrar por tipo: 'web' o 'app'"),
    accion: str = Query(None, description="Filtrar por acción"),
    usuario_id: str = Query(None, description="Filtrar por usuario"),
    profesor_id: str = Query(None, description="Filtrar por profesor"),
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
    current_profesor: Profesor | None = Depends(get_current_profesor),
    current_user: Usuario | None = Depends(get_current_user),
):
    """
    Obtener lista de audit logs con filtros opcionales.

    - Con API Key: Acceso total a todos los logs
    - Con Token de Profesor: Solo logs donde profesor_id = su ID
    - Con Token de Usuario: Solo logs donde usuario_id = su ID

    Demuestra polimorfismo: La query retorna instancias polimórficas (AuditLogWeb o AuditLogApp)
    según el discriminador 'tipo'.
    """
    audit_repo = AuditLogRepository(db)

    # Filtrar por ownership si NO es API Key
    if not auth.is_api_key:
        if current_profesor:
            # Profesor: solo sus propios logs (filtros adicionales se aplican en repository)
            logs = audit_repo.get_all_filtered(
                skip=skip,
                limit=limit,
                tipo=tipo,
                accion=accion,
                profesor_id=current_profesor.id,
            )
        elif current_user:
            # Usuario: solo sus propios logs
            logs = audit_repo.get_all_filtered(
                skip=skip,
                limit=limit,
                tipo=tipo,
                accion=accion,
                usuario_id=current_user.id,
            )
        else:
            # Token inválido (no debería llegar aquí por require_auth)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a los audit logs",
            )
    else:
        # API Key: acceso total con todos los filtros opcionales
        logs = audit_repo.get_all_filtered(
            skip=skip,
            limit=limit,
            tipo=tipo,
            accion=accion,
            usuario_id=usuario_id,
            profesor_id=profesor_id,
        )

    return logs


@router.get("/{log_id}", response_model=AuditLogResponse)
def obtener_audit_log(
    log_id: str,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
    current_profesor: Profesor | None = Depends(get_current_profesor),
    current_user: Usuario | None = Depends(get_current_user),
):
    """
    Obtener un audit log por ID.

    - Con API Key: Acceso total
    - Con Token de Profesor: Solo logs donde profesor_id = su ID
    - Con Token de Usuario: Solo logs donde usuario_id = su ID

    Demuestra polimorfismo: Retorna AuditLogWeb o AuditLogApp según el tipo.
    """
    audit_repo = AuditLogRepository(db)
    audit_log = audit_repo.get_by_id(log_id)
    if not audit_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log no encontrado")

    # Validar ownership si NO es API Key
    if not auth.is_api_key:
        is_owner = (current_profesor and audit_log.profesor_id == current_profesor.id) or (
            current_user and audit_log.usuario_id == current_user.id
        )

        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este audit log",
            )

    # Demuestra polimorfismo: get_description() funciona diferente según el tipo
    log_with_context(
        "info", "Audit log consultado", log_id=log_id, description=audit_log.get_description()
    )

    return audit_log
