from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.evento import Eventos
from app.models.actividad import Actividad
from app.schemas.evento import EventoCreate, EventoUpdate, EventoResponse
from app.logging import log_with_context

router = APIRouter(prefix="/eventos", tags=["Eventos"])

@router.post("", response_model=EventoResponse, status_code=status.HTTP_201_CREATED)
def crear_evento(evento_data: EventoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo evento."""
    # Validar que la actividad existe
    actividad = db.query(Actividad).filter(Actividad.id == evento_data.id_actividad).first()
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La actividad especificada no existe"
        )

    # Crear evento con UUID generado
    nuevo_evento = Eventos(
        id=str(uuid.uuid4()),
        id_actividad=evento_data.id_actividad,
        nombre=evento_data.nombre
    )

    db.add(nuevo_evento)
    db.commit()
    db.refresh(nuevo_evento)

    log_with_context("info", "Evento creado", evento_id=nuevo_evento.id, nombre=nuevo_evento.nombre)

    return nuevo_evento

@router.get("", response_model=List[EventoResponse])
def listar_eventos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de eventos."""
    eventos = db.query(Eventos).offset(skip).limit(limit).all()
    return eventos

@router.get("/{evento_id}", response_model=EventoResponse)
def obtener_evento(evento_id: str, db: Session = Depends(get_db)):
    """Obtener un evento por ID."""
    evento = db.query(Eventos).filter(Eventos.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )
    return evento

@router.put("/{evento_id}", response_model=EventoResponse)
def actualizar_evento(evento_id: str, evento_data: EventoUpdate, db: Session = Depends(get_db)):
    """Actualizar un evento existente."""
    evento = db.query(Eventos).filter(Eventos.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )

    # Validar actividad si se proporciona
    if evento_data.id_actividad:
        actividad = db.query(Actividad).filter(Actividad.id == evento_data.id_actividad).first()
        if not actividad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La actividad especificada no existe"
            )

    # Actualizar campos proporcionados
    update_data = evento_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(evento, field, value)

    db.commit()
    db.refresh(evento)

    log_with_context("info", "Evento actualizado", evento_id=evento.id)

    return evento

@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_evento(evento_id: str, db: Session = Depends(get_db)):
    """Eliminar un evento."""
    evento = db.query(Eventos).filter(Eventos.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )

    db.delete(evento)
    db.commit()

    log_with_context("info", "Evento eliminado", evento_id=evento_id)
