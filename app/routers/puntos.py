"""Router de gestión de puntos educativos.

Este módulo maneja los endpoints CRUD para puntos (módulos) del juego educativo.
Todas las operaciones requieren API Key.

Autor: Gernibide
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_with_context
from app.models.punto import Punto
from app.schemas.punto import PuntoCreate, PuntoResponse, PuntoUpdate
from app.utils.dependencies import require_api_key_only

router = APIRouter(prefix="/puntos", tags=["📍 Puntos"])


@router.post(
    "",
    response_model=PuntoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key_only)],
)
def crear_punto(punto_data: PuntoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo punto. Requiere API Key."""
    nuevo_punto = Punto(id=str(uuid.uuid4()), nombre=punto_data.nombre)

    db.add(nuevo_punto)
    db.commit()
    db.refresh(nuevo_punto)

    log_with_context(
        "info",
        "Punto creado",
        punto_id=nuevo_punto.id,
        nombre=nuevo_punto.nombre,
    )

    return nuevo_punto


@router.get(
    "",
    response_model=list[PuntoResponse],
    dependencies=[Depends(require_api_key_only)],
)
def listar_puntos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Obtener lista de puntos. Requiere API Key."""
    puntos = db.query(Punto).offset(skip).limit(limit).all()
    return puntos


@router.get(
    "/{punto_id}",
    response_model=PuntoResponse,
    dependencies=[Depends(require_api_key_only)],
)
def obtener_punto(
    punto_id: str,
    db: Session = Depends(get_db),
):
    """Obtener un punto por ID. Requiere API Key."""
    punto = db.query(Punto).filter(Punto.id == punto_id).first()
    if not punto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto no encontrado")
    return punto


@router.put(
    "/{punto_id}",
    response_model=PuntoResponse,
    dependencies=[Depends(require_api_key_only)],
)
def actualizar_punto(punto_id: str, punto_data: PuntoUpdate, db: Session = Depends(get_db)):
    """Actualizar un punto existente. Requiere API Key."""
    punto = db.query(Punto).filter(Punto.id == punto_id).first()
    if not punto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto no encontrado")

    update_data = punto_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(punto, field, value)

    db.commit()
    db.refresh(punto)

    log_with_context("info", "Punto actualizado", punto_id=punto.id)

    return punto


@router.delete(
    "/{punto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key_only)],
)
def eliminar_punto(punto_id: str, db: Session = Depends(get_db)):
    """Eliminar un punto. Requiere API Key."""
    punto = db.query(Punto).filter(Punto.id == punto_id).first()
    if not punto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto no encontrado")

    db.delete(punto)
    db.commit()

    log_with_context("info", "Punto eliminado", punto_id=punto_id)
