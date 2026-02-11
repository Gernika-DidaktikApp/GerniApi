"""Helper functions para reducir código duplicado.

Este módulo provee funciones reutilizables para operaciones comunes
en routers y servicios, reduciendo duplicación y mejorando mantenibilidad.

Autor: Gernibide
"""

from typing import TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database import Base

# Type variable para modelos SQLAlchemy
T = TypeVar("T", bound=Base)


def get_or_404(
    db: Session,
    model: type[T],
    record_id: str | UUID,
    error_message: str | None = None,
) -> T:
    """Obtiene un registro por ID o lanza 404 si no existe.

    Esta función encapsula el patrón común de buscar un registro
    y lanzar HTTPException 404 si no se encuentra.

    Args:
        db: Sesión de base de datos.
        model: Modelo SQLAlchemy a consultar.
        record_id: ID del registro (UUID string o UUID object).
        error_message: Mensaje de error personalizado. Si None, usa nombre del modelo.

    Returns:
        Instancia del modelo encontrada.

    Raises:
        HTTPException: 404 si el registro no existe.

    Examples:
        >>> usuario = get_or_404(db, Usuario, "123e4567-e89b-12d3-a456-426614174000")
        >>> clase = get_or_404(db, Clase, clase_id, "La clase no existe")
    """
    record = db.query(model).filter(model.id == str(record_id)).first()

    if not record:
        model_name = model.__name__
        message = error_message or f"{model_name} no encontrado"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )

    return record


def validate_exists(
    db: Session,
    model: type[T],
    record_id: str | UUID,
    error_message: str | None = None,
) -> None:
    """Valida que un registro existe o lanza 404.

    Similar a get_or_404 pero no retorna el registro (útil para validaciones).

    Args:
        db: Sesión de base de datos.
        model: Modelo SQLAlchemy a consultar.
        record_id: ID del registro (UUID string o UUID object).
        error_message: Mensaje de error personalizado.

    Raises:
        HTTPException: 404 si el registro no existe.

    Examples:
        >>> validate_exists(db, Clase, clase_id, "La clase no existe")
    """
    exists = db.query(model.id).filter(model.id == str(record_id)).first() is not None

    if not exists:
        model_name = model.__name__
        message = error_message or f"{model_name} no encontrado"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )
