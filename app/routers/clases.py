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
from app.logging import log_error, log_info, log_warning
from app.models.audit_log import AuditLogWeb
from app.models.clase import Clase
from app.models.profesor import Profesor
from app.repositories.clase_repository import ClaseRepository
from app.repositories.profesor_repository import ProfesorRepository
from app.schemas.clase import ClaseCreate, ClaseResponse, ClaseUpdate
from app.utils.dependencies import AuthResult, get_current_profesor, require_auth
from app.utils.security import generar_codigo_clase

router = APIRouter(prefix="/clases", tags=["🏫 Clases"])


def validate_clase_ownership(auth: AuthResult, clase: Clase, profesor: Profesor | None) -> None:
    """
    Valida que el profesor autenticado es dueño de la clase.
    API Key tiene acceso total, Token solo a sus propias clases.
    """
    if auth.is_api_key:
        return  # API Key tiene acceso total

    # Para tokens de profesor, verificar ownership
    if not profesor or clase.id_profesor != profesor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta clase",
        )


@router.post("", response_model=ClaseResponse, status_code=status.HTTP_201_CREATED)
def crear_clase(
    clase_data: ClaseCreate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
    current_profesor: Profesor | None = Depends(get_current_profesor),
):
    """Crear una nueva clase.

    Args:
        clase_data: Datos de la clase a crear.
        db: Sesión de base de datos.
        auth: Resultado de autenticación.
        current_profesor: Profesor autenticado (si aplica).

    Returns:
        Datos de la clase creada.

    Raises:
        HTTPException: Si el profesor especificado no existe.
        HTTPException: Si intenta crear clase para otro profesor (sin API Key).
    """
    # Con token de profesor: solo puede crear clases para sí mismo
    if not auth.is_api_key and current_profesor and clase_data.id_profesor != current_profesor.id:
        log_warning(
            "Intento de crear clase para otro profesor",
            profesor_autenticado=current_profesor.id,
            profesor_solicitado=clase_data.id_profesor,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes crear clases para ti mismo",
        )

    # Validar que el profesor existe
    profesor_repo = ProfesorRepository(db)
    profesor = profesor_repo.get_by_id(clase_data.id_profesor)
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

    # Generar código único para la clase
    clase_repo = ClaseRepository(db)
    codigo = generar_codigo_clase()
    while clase_repo.exists_by_codigo(codigo):
        codigo = generar_codigo_clase()

    # Crear clase con UUID y código generados
    nueva_clase = Clase(
        id=str(uuid.uuid4()),
        codigo=codigo,
        id_profesor=clase_data.id_profesor,
        nombre=clase_data.nombre,
    )

    nueva_clase = clase_repo.create(nueva_clase)

    # Log estructurado
    log_info(
        "Clase creada exitosamente",
        clase_id=nueva_clase.id,
        clase_codigo=nueva_clase.codigo,
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
        detalles=f"Clase '{nueva_clase.nombre}' creada con código {nueva_clase.codigo}",
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
    current_profesor: Profesor | None = Depends(get_current_profesor),
):
    """Obtener lista paginada de clases.

    Args:
        skip: Número de registros a saltar.
        limit: Número máximo de registros a retornar.
        db: Sesión de base de datos.
        auth: Resultado de autenticación.
        current_profesor: Profesor autenticado (si aplica).

    Returns:
        Lista de clases (filtrada por profesor si no es API Key).
    """
    clase_repo = ClaseRepository(db)

    # Con token de profesor: solo retornar sus propias clases
    if not auth.is_api_key and current_profesor:
        clases = clase_repo.get_by_profesor(current_profesor.id, skip, limit)
    else:
        # API Key: retornar todas las clases
        clases = clase_repo.get_all(skip, limit)

    return clases


@router.get("/{clase_id}", response_model=ClaseResponse)
def obtener_clase(
    clase_id: str,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
    current_profesor: Profesor | None = Depends(get_current_profesor),
):
    """Obtener una clase por ID.

    Args:
        clase_id: ID único de la clase.
        db: Sesión de base de datos.
        auth: Resultado de autenticación.
        current_profesor: Profesor autenticado (si aplica).

    Returns:
        Datos de la clase.

    Raises:
        HTTPException: Si la clase no existe.
        HTTPException: Si intenta acceder a clase de otro profesor (sin API Key).
    """
    clase_repo = ClaseRepository(db)
    clase = clase_repo.get_by_id(clase_id)
    if not clase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clase no encontrada")

    # Validar ownership
    validate_clase_ownership(auth, clase, current_profesor)

    return clase


@router.put("/{clase_id}", response_model=ClaseResponse)
def actualizar_clase(
    clase_id: str,
    clase_data: ClaseUpdate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
    current_profesor: Profesor | None = Depends(get_current_profesor),
):
    """Actualizar una clase existente.

    Args:
        clase_id: ID de la clase a actualizar.
        clase_data: Datos a actualizar.
        db: Sesión de base de datos.
        auth: Resultado de autenticación.
        current_profesor: Profesor autenticado (si aplica).

    Raises:
        HTTPException: Si la clase no existe.
        HTTPException: Si intenta actualizar clase de otro profesor (sin API Key).
    """
    clase_repo = ClaseRepository(db)
    clase = clase_repo.get_by_id(clase_id)
    if not clase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clase no encontrada")

    # Validar ownership
    validate_clase_ownership(auth, clase, current_profesor)

    # Validar profesor si se proporciona
    if clase_data.id_profesor:
        # Con token de profesor: no puede reasignar la clase a otro profesor
        if (
            not auth.is_api_key
            and current_profesor
            and clase_data.id_profesor != current_profesor.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes reasignar la clase a otro profesor",
            )

        profesor_repo = ProfesorRepository(db)
        profesor = profesor_repo.get_by_id(clase_data.id_profesor)
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

    clase = clase_repo.update(clase)

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
    current_profesor: Profesor | None = Depends(get_current_profesor),
):
    """Eliminar una clase del sistema.

    Los alumnos de la clase quedarán con id_clase = NULL (sin clase asignada).

    Args:
        clase_id: ID único de la clase a eliminar.
        db: Sesión de base de datos.
        auth: Resultado de autenticación.
        current_profesor: Profesor autenticado (si aplica).

    Raises:
        HTTPException: Si la clase no existe.
        HTTPException: Si intenta eliminar clase de otro profesor (sin API Key).
    """
    from app.models.usuario import Usuario

    clase_repo = ClaseRepository(db)
    clase = clase_repo.get_by_id(clase_id)
    if not clase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clase no encontrada")

    # Validar ownership
    validate_clase_ownership(auth, clase, current_profesor)

    clase_nombre = clase.nombre
    profesor_id = clase.id_profesor

    try:
        # Actualizar alumnos: quitar clase asignada (id_clase = NULL)
        # Nota: Mantenemos query directa aquí por ser parte de transacción
        alumnos_actualizados = (
            db.query(Usuario).filter(Usuario.id_clase == clase_id).update({Usuario.id_clase: None})
        )

        # Eliminar la clase usando repository
        # Nota: No usar clase_repo.delete() porque ya hizo commit en update de usuarios
        db.delete(clase)
        db.commit()

        # Log estructurado
        log_info(
            "Clase eliminada",
            clase_id=clase_id,
            clase_nombre=clase_nombre,
            profesor_id=profesor_id,
            alumnos_actualizados=alumnos_actualizados,
            auth_type="api_key" if auth.is_api_key else "token",
        )
    except Exception as e:
        db.rollback()
        log_error("Error al eliminar clase", clase_id=clase_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la clase: {str(e)}",
        )

    # Audit log
    detalles = f"Clase '{clase_nombre}' (ID: {clase_id}) eliminada"
    if alumnos_actualizados > 0:
        detalles += f". {alumnos_actualizados} alumno{'s' if alumnos_actualizados != 1 else ''} desasignado{'s' if alumnos_actualizados != 1 else ''}"

    audit_log = AuditLogWeb(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        profesor_id=profesor_id,
        accion="ELIMINAR_CLASE",
        detalles=detalles,
        tipo="web",
    )
    db.add(audit_log)
    db.commit()
