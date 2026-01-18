from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.evento_estado import EventoEstado
from app.models.juego import Partida
from app.models.actividad import Actividad
from app.models.actividad_estado import ActividadEstado
from app.models.evento import Eventos
from app.schemas.evento_estado import EventoEstadoCreate, EventoEstadoUpdate, EventoEstadoResponse, EventoEstadoCompletar
from app.logging import log_with_context
from datetime import datetime

router = APIRouter(prefix="/evento-estados", tags=["📊 Estados"])

@router.post("/iniciar", response_model=EventoEstadoResponse, status_code=status.HTTP_201_CREATED)
def iniciar_evento(estado_data: EventoEstadoCreate, db: Session = Depends(get_db)):
    """
    Iniciar un evento dentro de una actividad.

    Crea un nuevo registro de estado de evento con estado 'en_progreso'.
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

    # Validar que el evento existe y pertenece a la actividad
    evento = db.query(Eventos).filter(
        Eventos.id == estado_data.id_evento,
        Eventos.id_actividad == estado_data.id_actividad
    ).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El evento especificado no existe o no pertenece a esta actividad"
        )

    # Verificar si ya existe un evento en progreso para este juego y evento
    evento_existente = db.query(EventoEstado).filter(
        EventoEstado.id_juego == estado_data.id_juego,
        EventoEstado.id_evento == estado_data.id_evento,
        EventoEstado.estado == "en_progreso"
    ).first()

    if evento_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un evento en progreso para este juego y evento"
        )

    # Crear estado de evento con UUID generado
    nuevo_estado = EventoEstado(
        id=str(uuid.uuid4()),
        id_juego=estado_data.id_juego,
        id_actividad=estado_data.id_actividad,
        id_evento=estado_data.id_evento,
        estado="en_progreso"
    )

    db.add(nuevo_estado)
    db.commit()
    db.refresh(nuevo_estado)

    log_with_context("info", "Evento iniciado", estado_id=nuevo_estado.id, evento_id=estado_data.id_evento)

    return nuevo_estado

@router.put("/{estado_id}/completar", response_model=EventoEstadoResponse)
def completar_evento(estado_id: str, data: EventoEstadoCompletar, db: Session = Depends(get_db)):
    """
    Completar un evento y registrar su puntuación.

    - Calcula automáticamente la duración del evento
    - Actualiza el estado a 'completado'
    - Registra la puntuación obtenida
    - Verifica si es el último evento de la actividad
    - Si es el último, completa automáticamente la actividad con la suma de puntos
    """
    # Obtener el estado del evento
    estado = db.query(EventoEstado).filter(EventoEstado.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado de evento no encontrado"
        )

    # Verificar que el evento esté en progreso
    if estado.estado != "en_progreso":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El evento no está en progreso. Estado actual: {estado.estado}"
        )

    # Actualizar el estado del evento
    estado.fecha_fin = datetime.now()
    estado.duracion = int((estado.fecha_fin - estado.fecha_inicio).total_seconds())
    estado.estado = "completado"
    estado.puntuacion = data.puntuacion

    db.commit()
    db.refresh(estado)

    log_with_context("info", "Evento completado",
                     estado_id=estado.id,
                     evento_id=estado.id_evento,
                     puntuacion=data.puntuacion,
                     duracion=estado.duracion)

    # Verificar si todos los eventos de la actividad están completados
    # Obtener todos los eventos de la actividad
    todos_los_eventos = db.query(Eventos).filter(
        Eventos.id_actividad == estado.id_actividad
    ).all()
    total_eventos = len(todos_los_eventos)

    # Obtener todos los estados de eventos completados para esta actividad y juego
    eventos_completados = db.query(EventoEstado).filter(
        EventoEstado.id_juego == estado.id_juego,
        EventoEstado.id_actividad == estado.id_actividad,
        EventoEstado.estado == "completado"
    ).all()
    eventos_completados_count = len(eventos_completados)

    log_with_context("info", "Verificación de progreso de actividad",
                     total_eventos=total_eventos,
                     eventos_completados=eventos_completados_count)

    # Si todos los eventos están completados, completar la actividad
    if eventos_completados_count == total_eventos:
        actividad_estado = db.query(ActividadEstado).filter(
            ActividadEstado.id_juego == estado.id_juego,
            ActividadEstado.id_actividad == estado.id_actividad,
            ActividadEstado.estado == "en_progreso"
        ).first()

        if actividad_estado:
            # Calcular la puntuación total sumando todos los eventos
            puntuacion_total = sum(e.puntuacion for e in eventos_completados if e.puntuacion is not None)

            # Actualizar la actividad
            actividad_estado.fecha_fin = datetime.now()
            actividad_estado.duracion = int((actividad_estado.fecha_fin - actividad_estado.fecha_inicio).total_seconds())
            actividad_estado.estado = "completado"
            actividad_estado.puntuacion_total = puntuacion_total

            db.commit()
            db.refresh(actividad_estado)

            log_with_context("info", "Actividad completada automáticamente",
                           actividad_estado_id=actividad_estado.id,
                           actividad_id=estado.id_actividad,
                           puntuacion_total=puntuacion_total,
                           duracion_total=actividad_estado.duracion)

    return estado

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

    # Validar que el evento existe y pertenece a la actividad
    evento = db.query(Eventos).filter(
        Eventos.id == estado_data.id_evento,
        Eventos.id_actividad == estado_data.id_actividad
    ).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El evento especificado no existe o no pertenece a esta actividad"
        )

    # Crear estado de evento con UUID generado
    nuevo_estado = EventoEstado(
        id=str(uuid.uuid4()),
        id_juego=estado_data.id_juego,
        id_actividad=estado_data.id_actividad,
        id_evento=estado_data.id_evento,
        estado="en_progreso"
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
