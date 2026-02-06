import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_with_context
from app.models.audit_log import AuditLog, AuditLogApp, AuditLogWeb
from app.models.profesor import Profesor
from app.models.usuario import Usuario
from app.schemas.audit_log import AuditLogAppCreate, AuditLogResponse, AuditLogWebCreate
from app.utils.dependencies import AuthResult, require_api_key_only, require_auth

router = APIRouter(prefix="/audit-logs", tags=["📋 Audit Logs"])


@router.post(
    "/web",
    response_model=AuditLogResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key_only)],
)
def crear_audit_log_web(log_data: AuditLogWebCreate, db: Session = Depends(get_db)):
    """
    Crear un audit log desde la aplicación web. Requiere API Key.

    Demuestra herencia: AuditLogWeb hereda de AuditLog.
    """
    # Validar que al menos uno de usuario_id o profesor_id esté presente
    if not log_data.usuario_id and not log_data.profesor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar usuario_id o profesor_id",
        )

    # Validar que el usuario o profesor exista
    if log_data.usuario_id:
        usuario = db.query(Usuario).filter(Usuario.id == log_data.usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario especificado no existe",
            )

    if log_data.profesor_id:
        profesor = db.query(Profesor).filter(Profesor.id == log_data.profesor_id).first()
        if not profesor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El profesor especificado no existe",
            )

    # Crear instancia de AuditLogWeb (clase heredada)
    nuevo_log = AuditLogWeb(
        id=str(uuid.uuid4()),
        usuario_id=log_data.usuario_id,
        profesor_id=log_data.profesor_id,
        accion=log_data.accion,
        detalles=log_data.detalles,
        ip_address=log_data.ip_address,
        user_agent=log_data.user_agent,
        browser=log_data.browser,
    )

    db.add(nuevo_log)
    db.commit()
    db.refresh(nuevo_log)

    # Demuestra polimorfismo: get_description() se comporta diferente según el tipo
    log_with_context("info", "Audit log web creado", description=nuevo_log.get_description())

    return nuevo_log


@router.post(
    "/app",
    response_model=AuditLogResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key_only)],
)
def crear_audit_log_app(log_data: AuditLogAppCreate, db: Session = Depends(get_db)):
    """
    Crear un audit log desde la aplicación móvil. Requiere API Key.

    Demuestra herencia: AuditLogApp hereda de AuditLog.
    """
    # Validar que al menos uno de usuario_id o profesor_id esté presente
    if not log_data.usuario_id and not log_data.profesor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar usuario_id o profesor_id",
        )

    # Validar que el usuario o profesor exista
    if log_data.usuario_id:
        usuario = db.query(Usuario).filter(Usuario.id == log_data.usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario especificado no existe",
            )

    if log_data.profesor_id:
        profesor = db.query(Profesor).filter(Profesor.id == log_data.profesor_id).first()
        if not profesor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El profesor especificado no existe",
            )

    # Crear instancia de AuditLogApp (clase heredada)
    nuevo_log = AuditLogApp(
        id=str(uuid.uuid4()),
        usuario_id=log_data.usuario_id,
        profesor_id=log_data.profesor_id,
        accion=log_data.accion,
        detalles=log_data.detalles,
        device_type=log_data.device_type,
        app_version=log_data.app_version,
        device_id=log_data.device_id,
    )

    db.add(nuevo_log)
    db.commit()
    db.refresh(nuevo_log)

    # Demuestra polimorfismo: get_description() se comporta diferente según el tipo
    log_with_context("info", "Audit log app creado", description=nuevo_log.get_description())

    return nuevo_log


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


@router.delete(
    "/{log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key_only)],
)
def eliminar_audit_log(log_id: str, db: Session = Depends(get_db)):
    """Eliminar un audit log. Requiere API Key."""
    audit_log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not audit_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log no encontrado")

    db.delete(audit_log)
    db.commit()

    log_with_context("info", "Audit log eliminado", log_id=log_id)
