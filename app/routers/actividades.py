import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_with_context
from app.models.actividad import Actividad
from app.models.punto import Punto
from app.schemas.actividad import ActividadCreate, ActividadResponse, ActividadUpdate
from app.utils.dependencies import require_api_key_only

router = APIRouter(prefix="/actividades", tags=["📝 Actividades"])


@router.post(
    "",
    response_model=ActividadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key_only)],
)
def crear_actividad(actividad_data: ActividadCreate, db: Session = Depends(get_db)):
    """Crear una nueva actividad. Requiere API Key."""
    punto = db.query(Punto).filter(Punto.id == actividad_data.id_punto).first()
    if not punto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El punto especificado no existe",
        )

    nueva_actividad = Actividad(
        id=str(uuid.uuid4()),
        id_punto=actividad_data.id_punto,
        nombre=actividad_data.nombre,
    )

    db.add(nueva_actividad)
    db.commit()
    db.refresh(nueva_actividad)

    log_with_context(
        "info", "Actividad creada", actividad_id=nueva_actividad.id, nombre=nueva_actividad.nombre
    )

    return nueva_actividad


@router.get(
    "",
    response_model=list[ActividadResponse],
    dependencies=[Depends(require_api_key_only)],
)
def listar_actividades(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Obtener lista de actividades. Requiere API Key."""
    actividades = db.query(Actividad).offset(skip).limit(limit).all()
    return actividades


@router.get(
    "/{actividad_id}",
    response_model=ActividadResponse,
    dependencies=[Depends(require_api_key_only)],
)
def obtener_actividad(
    actividad_id: str,
    db: Session = Depends(get_db),
):
    """Obtener una actividad por ID. Requiere API Key."""
    actividad = db.query(Actividad).filter(Actividad.id == actividad_id).first()
    if not actividad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")
    return actividad


@router.put(
    "/{actividad_id}",
    response_model=ActividadResponse,
    dependencies=[Depends(require_api_key_only)],
)
def actualizar_actividad(
    actividad_id: str,
    actividad_data: ActividadUpdate,
    db: Session = Depends(get_db),
):
    """Actualizar una actividad existente. Requiere API Key."""
    actividad = db.query(Actividad).filter(Actividad.id == actividad_id).first()
    if not actividad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")

    if actividad_data.id_punto:
        punto = db.query(Punto).filter(Punto.id == actividad_data.id_punto).first()
        if not punto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El punto especificado no existe",
            )

    update_data = actividad_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(actividad, field, value)

    db.commit()
    db.refresh(actividad)

    log_with_context("info", "Actividad actualizada", actividad_id=actividad.id)

    return actividad


@router.delete(
    "/{actividad_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key_only)],
)
def eliminar_actividad(actividad_id: str, db: Session = Depends(get_db)):
    """Eliminar una actividad. Requiere API Key."""
    actividad = db.query(Actividad).filter(Actividad.id == actividad_id).first()
    if not actividad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")

    db.delete(actividad)
    db.commit()

    log_with_context("info", "Actividad eliminada", actividad_id=actividad_id)
