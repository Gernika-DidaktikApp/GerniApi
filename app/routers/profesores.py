"""Router de gestión de profesores.

Este módulo maneja todos los endpoints relacionados con profesores:
creación, listado, actualización y eliminación. Todos los endpoints
requieren API Key para autenticación.

Autor: Gernibide
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_with_context
from app.models.profesor import Profesor
from app.repositories.profesor_repository import ProfesorRepository
from app.schemas.profesor import ProfesorCreate, ProfesorResponse, ProfesorUpdate
from app.utils.dependencies import require_api_key_only
from app.utils.security import hash_password

router = APIRouter(
    prefix="/profesores",
    tags=["👨‍🏫 Profesores"],
    dependencies=[Depends(require_api_key_only)],
)


@router.post("", response_model=ProfesorResponse, status_code=status.HTTP_201_CREATED)
def crear_profesor(profesor_data: ProfesorCreate, db: Session = Depends(get_db)):
    """Crear un nuevo profesor.

    Args:
        profesor_data: Datos del profesor a crear.
        db: Sesión de base de datos.

    Returns:
        Datos del profesor creado.

    Raises:
        HTTPException: Si el username ya está en uso.
    """
    profesor_repo = ProfesorRepository(db)

    # Validar que el username no exista
    if profesor_repo.exists_by_username(profesor_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El username ya está en uso"
        )

    # Crear profesor con UUID generado
    nuevo_profesor = Profesor(
        id=str(uuid.uuid4()),
        username=profesor_data.username,
        nombre=profesor_data.nombre,
        apellido=profesor_data.apellido,
        password=hash_password(profesor_data.password),
    )

    nuevo_profesor = profesor_repo.create(nuevo_profesor)

    log_with_context(
        "info",
        "Profesor creado",
        profesor_id=nuevo_profesor.id,
        username=nuevo_profesor.username,
    )

    return nuevo_profesor


@router.get("", response_model=list[ProfesorResponse])
def listar_profesores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista paginada de profesores.

    Args:
        skip: Número de registros a saltar.
        limit: Número máximo de registros a retornar.
        db: Sesión de base de datos.

    Returns:
        Lista de profesores.
    """
    profesor_repo = ProfesorRepository(db)
    profesores = profesor_repo.get_all(skip, limit)
    return profesores


@router.get("/{profesor_id}", response_model=ProfesorResponse)
def obtener_profesor(profesor_id: str, db: Session = Depends(get_db)):
    """Obtener un profesor por ID.

    Args:
        profesor_id: ID único del profesor.
        db: Sesión de base de datos.

    Returns:
        Datos del profesor.

    Raises:
        HTTPException: Si el profesor no existe.
    """
    profesor_repo = ProfesorRepository(db)
    profesor = profesor_repo.get_by_id(profesor_id)
    if not profesor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesor no encontrado")
    return profesor


@router.put("/{profesor_id}", response_model=ProfesorResponse)
def actualizar_profesor(
    profesor_id: str, profesor_data: ProfesorUpdate, db: Session = Depends(get_db)
):
    """Actualizar un profesor existente.

    Args:
        profesor_id: ID único del profesor.
        profesor_data: Datos a actualizar.
        db: Sesión de base de datos.

    Returns:
        Datos actualizados del profesor.

    Raises:
        HTTPException: Si el profesor no existe o el username ya está en uso.
    """
    profesor_repo = ProfesorRepository(db)
    profesor = profesor_repo.get_by_id(profesor_id)
    if not profesor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesor no encontrado")

    # Validar username único si se está actualizando
    if (
        profesor_data.username
        and profesor_data.username != profesor.username
        and profesor_repo.exists_by_username(profesor_data.username)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username ya está en uso",
        )

    # Actualizar campos proporcionados
    update_data = profesor_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    for field, value in update_data.items():
        setattr(profesor, field, value)

    profesor = profesor_repo.update(profesor)

    log_with_context("info", "Profesor actualizado", profesor_id=profesor.id)

    return profesor


@router.delete("/{profesor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_profesor(profesor_id: str, db: Session = Depends(get_db)):
    """Eliminar un profesor del sistema.

    Args:
        profesor_id: ID único del profesor a eliminar.
        db: Sesión de base de datos.

    Raises:
        HTTPException: Si el profesor no existe.
    """
    profesor_repo = ProfesorRepository(db)
    profesor = profesor_repo.get_by_id(profesor_id)
    if not profesor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesor no encontrado")

    profesor_repo.delete(profesor)

    log_with_context("info", "Profesor eliminado", profesor_id=profesor_id)
