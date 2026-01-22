import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_with_context
from app.models.actividad import Actividad
from app.models.actividad_estado import ActividadEstado
from app.models.juego import Partida
from app.schemas.actividad_estado import (ActividadEstadoCreate,
                                          ActividadEstadoResponse,
                                          ActividadEstadoUpdate)
from app.utils.dependencies import (AuthResult, require_api_key_only,
                                    require_auth, validate_partida_ownership)

router = APIRouter(prefix="/actividad-estados", tags=["📊 Estados"])

@router.post("/iniciar", response_model=ActividadEstadoResponse, status_code=status.HTTP_201_CREATED)
def iniciar_actividad(
    estado_data: ActividadEstadoCreate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth)
):
    """
    Iniciar una actividad para un jugador.

    Crea un nuevo registro de estado de actividad con estado 'en_progreso'.
    La fecha de inicio se registra automáticamente.

    - Con API Key: Puede iniciar actividades para cualquier partida
    - Con Token: Solo puede iniciar actividades para sus propias partidas
    """
    validate_partida_ownership(auth, estado_data.id_juego, db)

    actividad = db.query(Actividad).filter(Actividad.id == estado_data.id_actividad).first()
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La actividad especificada no existe"
        )

    actividad_existente = db.query(ActividadEstado).filter(
        ActividadEstado.id_juego == estado_data.id_juego,
        ActividadEstado.id_actividad == estado_data.id_actividad,
        ActividadEstado.estado == "en_progreso"
    ).first()

    if actividad_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una actividad en progreso para este juego y actividad"
        )

    nuevo_estado = ActividadEstado(
        id=str(uuid.uuid4()),
        id_juego=estado_data.id_juego,
        id_actividad=estado_data.id_actividad,
        estado="en_progreso",
        puntuacion_total=0.0
    )

    db.add(nuevo_estado)
    db.commit()
    db.refresh(nuevo_estado)

    log_with_context("info", "Actividad iniciada", estado_id=nuevo_estado.id, actividad_id=estado_data.id_actividad)

    return nuevo_estado

@router.post("", response_model=ActividadEstadoResponse, status_code=status.HTTP_201_CREATED)
def crear_actividad_estado(
    estado_data: ActividadEstadoCreate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth)
):
    """
    Crear un nuevo estado de actividad.

    - Con API Key: Puede crear estados para cualquier partida
    - Con Token: Solo puede crear estados para sus propias partidas
    """
    validate_partida_ownership(auth, estado_data.id_juego, db)

    actividad = db.query(Actividad).filter(Actividad.id == estado_data.id_actividad).first()
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La actividad especificada no existe"
        )

    nuevo_estado = ActividadEstado(
        id=str(uuid.uuid4()),
        id_juego=estado_data.id_juego,
        id_actividad=estado_data.id_actividad
    )

    db.add(nuevo_estado)
    db.commit()
    db.refresh(nuevo_estado)

    log_with_context("info", "Estado de actividad creado", estado_id=nuevo_estado.id)

    return nuevo_estado

@router.get(
    "",
    response_model=List[ActividadEstadoResponse],
    dependencies=[Depends(require_api_key_only)]
)
def listar_actividad_estados(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de estados de actividad. Requiere API Key."""
    estados = db.query(ActividadEstado).offset(skip).limit(limit).all()
    return estados

@router.get("/{estado_id}", response_model=ActividadEstadoResponse)
def obtener_actividad_estado(
    estado_id: str,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth)
):
    """
    Obtener un estado de actividad por ID.

    - Con API Key: Puede ver cualquier estado
    - Con Token: Solo puede ver estados de sus propias partidas
    """
    estado = db.query(ActividadEstado).filter(ActividadEstado.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado de actividad no encontrado"
        )

    validate_partida_ownership(auth, estado.id_juego, db)

    return estado

@router.put("/{estado_id}", response_model=ActividadEstadoResponse)
def actualizar_actividad_estado(
    estado_id: str,
    estado_data: ActividadEstadoUpdate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth)
):
    """
    Actualizar un estado de actividad existente.

    - Con API Key: Puede actualizar cualquier estado
    - Con Token: Solo puede actualizar estados de sus propias partidas
    """
    estado = db.query(ActividadEstado).filter(ActividadEstado.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado de actividad no encontrado"
        )

    validate_partida_ownership(auth, estado.id_juego, db)

    update_data = estado_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(estado, field, value)

    db.commit()
    db.refresh(estado)

    log_with_context("info", "Estado de actividad actualizado", estado_id=estado.id)

    return estado

@router.delete(
    "/{estado_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key_only)]
)
def eliminar_actividad_estado(estado_id: str, db: Session = Depends(get_db)):
    """Eliminar un estado de actividad. Requiere API Key."""
    estado = db.query(ActividadEstado).filter(ActividadEstado.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado de actividad no encontrado"
        )

    db.delete(estado)
    db.commit()

    log_with_context("info", "Estado de actividad eliminado", estado_id=estado_id)
