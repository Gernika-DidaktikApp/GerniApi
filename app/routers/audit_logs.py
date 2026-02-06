from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_with_context
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogResponse
from app.utils.dependencies import AuthResult, require_auth

router = APIRouter(prefix="/audit-logs", tags=["📋 Audit Logs"])

# Los audit logs se crean automáticamente por el sistema (login, completar actividades, etc.)
# Solo se pueden leer, no crear ni eliminar manualmente


@router.get("", response_model=List[AuditLogResponse])
def listar_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tipo: str = Query(None, description="Filtrar por tipo: 'web' o 'app'"),
    accion: str = Query(None, description="Filtrar por acción"),
    usuario_id: str = Query(None, description="Filtrar por usuario"),
    profesor_id: str = Query(None, description="Filtrar por profesor"),
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Obtener lista de audit logs con filtros opcionales. Requiere API Key o Token de usuario.

    Demuestra polimorfismo: La query retorna instancias polimórficas (AuditLogWeb o AuditLogApp)
    según el discriminador 'tipo'.
    """
    query = db.query(AuditLog)

    # Aplicar filtros
    if tipo:
        query = query.filter(AuditLog.tipo == tipo)
    if accion:
        query = query.filter(AuditLog.accion == accion)
    if usuario_id:
        query = query.filter(AuditLog.usuario_id == usuario_id)
    if profesor_id:
        query = query.filter(AuditLog.profesor_id == profesor_id)

    # Ordenar por timestamp descendente (más recientes primero)
    query = query.order_by(AuditLog.timestamp.desc())

    # Aplicar paginación
    logs = query.offset(skip).limit(limit).all()

    return logs


@router.get("/{log_id}", response_model=AuditLogResponse)
def obtener_audit_log(
    log_id: str,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Obtener un audit log por ID. Requiere API Key o Token de usuario.

    Demuestra polimorfismo: Retorna AuditLogWeb o AuditLogApp según el tipo.
    """
    audit_log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not audit_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log no encontrado")

    # Demuestra polimorfismo: get_description() funciona diferente según el tipo
    log_with_context(
        "info", "Audit log consultado", log_id=log_id, description=audit_log.get_description()
    )

    return audit_log


