"""Router de gestión de clases.

Este módulo maneja todos los endpoints relacionados con clases:
creación, listado, actualización y eliminación. Requiere autenticación
mediante API Key o Token JWT.

Autor: Gernibide
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_info, log_warning
from app.models.audit_log import AuditLogWeb
from app.models.clase import Clase
from app.models.profesor import Profesor
from app.schemas.clase import ClaseCreate, ClaseResponse, ClaseUpdate
from app.utils.dependencies import AuthResult, require_auth

router = APIRouter(prefix="/clases", tags=["🏫 Clases"])


@router.post("", response_model=ClaseResponse, status_code=status.HTTP_201_CREATED)
def crear_clase(
    clase_data: ClaseCreate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """Crear una nueva clase.

    Args:
        clase_data: Datos de la clase a crear.
        db: Sesión de base de datos.
        auth: Resultado de autenticación.

    Returns:
        Datos de la clase creada.

    Raises:
        HTTPException: Si el profesor especificado no existe.
    """
    # Validar que el profesor existe
    profesor = db.query(Profesor).filter(Profesor.id == clase_data.id_profesor).first()
    if not profesor:
        log_warning(
            "Intento de crear clase con profesor inexistente",
            profesor_id=clase_data.id_profesor,
            auth_type="api_key" if auth.is_api_key else "token",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El profesor especificado no existe",
        )

    # Crear clase con UUID generado
    nueva_clase = Clase(
        id=str(uuid.uuid4()),
        id_profesor=clase_data.id_profesor,
        nombre=clase_data.nombre,
    )

    db.add(nueva_clase)
    db.commit()
    db.refresh(nueva_clase)

    # Log estructurado
    log_info(
        "Clase creada exitosamente",
        clase_id=nueva_clase.id,
        clase_nombre=nueva_clase.nombre,
        profesor_id=nueva_clase.id_profesor,
        profesor_nombre=f"{profesor.nombre} {profesor.apellido}",
        auth_type="api_key" if auth.is_api_key else "token",
    )

    # Audit log
    audit_log = AuditLogWeb(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        profesor_id=clase_data.id_profesor,
        accion="CREAR_CLASE",
        detalles=f"Clase '{nueva_clase.nombre}' creada con ID {nueva_clase.id}",
        tipo="web",
    )
    db.add(audit_log)
    db.commit()

    return nueva_clase


@router.get("", response_model=list[ClaseResponse])
def listar_clases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """Obtener lista paginada de clases.

    Args:
        skip: Número de registros a saltar.
        limit: Número máximo de registros a retornar.
        db: Sesión de base de datos.
        auth: Resultado de autenticación.

    Returns:
        Lista de clases.
    """
    clases = db.query(Clase).offset(skip).limit(limit).all()
    return clases


@router.get("/{clase_id}", response_model=ClaseResponse)
def obtener_clase(
    clase_id: str,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """Obtener una clase por ID.

    Args:
        clase_id: ID único de la clase.
        db: Sesión de base de datos.
        auth: Resultado de autenticación.

    Returns:
        Datos de la clase.

    Raises:
        HTTPException: Si la clase no existe.
    """
    clase = db.query(Clase).filter(Clase.id == clase_id).first()
    if not clase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clase no encontrada")
    return clase


@router.put("/{clase_id}", response_model=ClaseResponse)
def actualizar_clase(
    clase_id: str,
    clase_data: ClaseUpdate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """Actualizar una clase existente."""
    clase = db.query(Clase).filter(Clase.id == clase_id).first()
    if not clase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clase no encontrada")

    # Validar profesor si se proporciona
    if clase_data.id_profesor:
        profesor = db.query(Profesor).filter(Profesor.id == clase_data.id_profesor).first()
        if not profesor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El profesor especificado no existe",
            )

    # Actualizar campos proporcionados
    update_data = clase_data.model_dump(exclude_unset=True)
    campos_actualizados = list(update_data.keys())

    for field, value in update_data.items():
        setattr(clase, field, value)

    db.commit()
    db.refresh(clase)

    # Log estructurado
    log_info(
        "Clase actualizada",
        clase_id=clase.id,
        clase_nombre=clase.nombre,
        campos_actualizados=",".join(campos_actualizados),
        auth_type="api_key" if auth.is_api_key else "token",
    )

    # Audit log
    audit_log = AuditLogWeb(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        profesor_id=clase.id_profesor,
        accion="ACTUALIZAR_CLASE",
        detalles=f"Clase '{clase.nombre}' actualizada. Campos: {', '.join(campos_actualizados)}",
        tipo="web",
    )
    db.add(audit_log)
    db.commit()

    return clase


@router.delete("/{clase_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_clase(
    clase_id: str,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """Eliminar una clase del sistema.

    Args:
        clase_id: ID único de la clase a eliminar.
        db: Sesión de base de datos.
        auth: Resultado de autenticación.

    Raises:
        HTTPException: Si la clase no existe.
    """
    clase = db.query(Clase).filter(Clase.id == clase_id).first()
    if not clase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clase no encontrada")

    clase_nombre = clase.nombre
    profesor_id = clase.id_profesor

    db.delete(clase)
    db.commit()

    # Log estructurado
    log_info(
        "Clase eliminada",
        clase_id=clase_id,
        clase_nombre=clase_nombre,
        profesor_id=profesor_id,
        auth_type="api_key" if auth.is_api_key else "token",
    )

    # Audit log
    audit_log = AuditLogWeb(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        profesor_id=profesor_id,
        accion="ELIMINAR_CLASE",
        detalles=f"Clase '{clase_nombre}' (ID: {clase_id}) eliminada",
        tipo="web",
    )
    db.add(audit_log)
    db.commit()
