from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.evento_estado import EventoEstado
from app.models.juego import Partida
from app.models.actividad import Actividad
from app.schemas.evento_estado import EventoEstadoCreate, EventoEstadoUpdate, EventoEstadoResponse
from app.logging import log_with_context

router = APIRouter(prefix="/evento-estados", tags=["Estados de Evento"])

@router.post("", response_model=EventoEstadoResponse, status_code=status.HTTP_201_CREATED)
def crear_evento_estado(estado_data: EventoEstadoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo estado de evento."""
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

    # Crear estado de evento con UUID generado
    nuevo_estado = EventoEstado(
        id=str(uuid.uuid4()),
        id_juego=estado_data.id_juego,
        id_actividad=estado_data.id_actividad,
        estado=estado_data.estado
    )

    db.add(nuevo_estado)
    db.commit()
    db.refresh(nuevo_estado)

    log_with_context("info", "Estado de evento creado", estado_id=nuevo_estado.id)

    return nuevo_estado

@router.get("", response_model=List[EventoEstadoResponse])
def listar_evento_estados(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de estados de evento."""
    estados = db.query(EventoEstado).offset(skip).limit(limit).all()
    return estados

@router.get("/{estado_id}", response_model=EventoEstadoResponse)
def obtener_evento_estado(estado_id: str, db: Session = Depends(get_db)):
    """Obtener un estado de evento por ID."""
    estado = db.query(EventoEstado).filter(EventoEstado.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado de evento no encontrado"
        )
    return estado

@router.put("/{estado_id}", response_model=EventoEstadoResponse)
def actualizar_evento_estado(estado_id: str, estado_data: EventoEstadoUpdate, db: Session = Depends(get_db)):
    """Actualizar un estado de evento existente."""
    estado = db.query(EventoEstado).filter(EventoEstado.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado de evento no encontrado"
        )

    # Actualizar campos proporcionados
    update_data = estado_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(estado, field, value)

    db.commit()
    db.refresh(estado)

    log_with_context("info", "Estado de evento actualizado", estado_id=estado.id)

    return estado

@router.delete("/{estado_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_evento_estado(estado_id: str, db: Session = Depends(get_db)):
    """Eliminar un estado de evento."""
    estado = db.query(EventoEstado).filter(EventoEstado.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado de evento no encontrado"
        )

    db.delete(estado)
    db.commit()

    log_with_context("info", "Estado de evento eliminado", estado_id=estado_id)
