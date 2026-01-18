from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.actividad_estado import ActividadEstado
from app.models.juego import Partida
from app.models.actividad import Actividad
from app.schemas.actividad_estado import ActividadEstadoCreate, ActividadEstadoUpdate, ActividadEstadoResponse
from app.logging import log_with_context

router = APIRouter(prefix="/actividad-estados", tags=["📊 Estados"])

@router.post("/iniciar", response_model=ActividadEstadoResponse, status_code=status.HTTP_201_CREATED)
def iniciar_actividad(estado_data: ActividadEstadoCreate, db: Session = Depends(get_db)):
    """
    Iniciar una actividad para un jugador.

    Crea un nuevo registro de estado de actividad con estado 'en_progreso'.
    La fecha de inicio se registra automáticamente.
    """
    # Validar que el juego existe
    juego = db.query(Partida).filter(Partida.id == estado_data.id_juego).first()
    if not juego:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La partida especificada no existe"
        )

    # Validar que la actividad existe
    actividad = db.query(Actividad).filter(Actividad.id == estado_data.id_actividad).first()
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La actividad especificada no existe"
        )

    # Verificar si ya existe una actividad en progreso para este juego y actividad
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

    # Crear estado de actividad con UUID generado
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
def crear_actividad_estado(estado_data: ActividadEstadoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo estado de actividad."""
    # Validar que el juego existe
    juego = db.query(Partida).filter(Partida.id == estado_data.id_juego).first()
    if not juego:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La partida especificada no existe"
        )

    # Validar que la actividad existe
    actividad = db.query(Actividad).filter(Actividad.id == estado_data.id_actividad).first()
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La actividad especificada no existe"
        )

    # Crear estado de actividad con UUID generado
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

@router.get("", response_model=List[ActividadEstadoResponse])
def listar_actividad_estados(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de estados de actividad."""
    estados = db.query(ActividadEstado).offset(skip).limit(limit).all()
    return estados

@router.get("/{estado_id}", response_model=ActividadEstadoResponse)
def obtener_actividad_estado(estado_id: str, db: Session = Depends(get_db)):
    """Obtener un estado de actividad por ID."""
    estado = db.query(ActividadEstado).filter(ActividadEstado.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado de actividad no encontrado"
        )
    return estado

@router.put("/{estado_id}", response_model=ActividadEstadoResponse)
def actualizar_actividad_estado(estado_id: str, estado_data: ActividadEstadoUpdate, db: Session = Depends(get_db)):
    """Actualizar un estado de actividad existente."""
    estado = db.query(ActividadEstado).filter(ActividadEstado.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado de actividad no encontrado"
        )

    # Actualizar campos proporcionados
    update_data = estado_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(estado, field, value)

    db.commit()
    db.refresh(estado)

    log_with_context("info", "Estado de actividad actualizado", estado_id=estado.id)

    return estado

@router.delete("/{estado_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_actividad_estado(estado_id: str, db: Session = Depends(get_db)):
    """Eliminar un estado de actividad."""
    estado = db.query(ActividadEstado).filter(ActividadEstado.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado de actividad no encontrado"
        )

    db.delete(estado)
    db.commit()

    log_with_context("info", "Estado de actividad eliminado", estado_id=estado_id)
