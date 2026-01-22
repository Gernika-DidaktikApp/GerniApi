import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_with_context
from app.models.actividad import Actividad
from app.models.evento import Eventos
from app.schemas.evento import EventoCreate, EventoResponse, EventoUpdate
from app.utils.dependencies import (AuthResult, require_api_key_only,
                                    require_auth)

router = APIRouter(prefix="/eventos", tags=["📅 Eventos"])

@router.post(
    "",
    response_model=EventoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key_only)]
)
def crear_evento(evento_data: EventoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo evento. Requiere API Key."""
    actividad = db.query(Actividad).filter(Actividad.id == evento_data.id_actividad).first()
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La actividad especificada no existe"
        )

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
def listar_eventos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth)
):
    """Obtener lista de eventos. Requiere API Key o Token de usuario."""
    eventos = db.query(Eventos).offset(skip).limit(limit).all()
    return eventos

@router.get("/{evento_id}", response_model=EventoResponse)
def obtener_evento(
    evento_id: str,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth)
):
    """Obtener un evento por ID. Requiere API Key o Token de usuario."""
    evento = db.query(Eventos).filter(Eventos.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )
    return evento

@router.put(
    "/{evento_id}",
    response_model=EventoResponse,
    dependencies=[Depends(require_api_key_only)]
)
def actualizar_evento(evento_id: str, evento_data: EventoUpdate, db: Session = Depends(get_db)):
    """Actualizar un evento existente. Requiere API Key."""
    evento = db.query(Eventos).filter(Eventos.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )

    if evento_data.id_actividad:
        actividad = db.query(Actividad).filter(Actividad.id == evento_data.id_actividad).first()
        if not actividad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La actividad especificada no existe"
            )

    update_data = evento_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(evento, field, value)

    db.commit()
    db.refresh(evento)

    log_with_context("info", "Evento actualizado", evento_id=evento.id)

    return evento

@router.delete(
    "/{evento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key_only)]
)
def eliminar_evento(evento_id: str, db: Session = Depends(get_db)):
    """Eliminar un evento. Requiere API Key."""
    evento = db.query(Eventos).filter(Eventos.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )

    db.delete(evento)
    db.commit()

    log_with_context("info", "Evento eliminado", evento_id=evento_id)
