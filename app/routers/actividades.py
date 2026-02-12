"""Router de gestión de actividades.

Este módulo maneja los endpoints CRUD para actividades educativas.
Todas las operaciones requieren API Key.

Autor: Gernibide
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_with_context
from app.models.actividad import Actividad
from app.models.actividad_progreso import ActividadProgreso
from app.models.juego import Partida
from app.models.usuario import Usuario
from app.repositories.actividad_repository import ActividadRepository
from app.repositories.punto_repository import PuntoRepository
from app.schemas.actividad import (
    ActividadCreate,
    ActividadResponse,
    ActividadUpdate,
    RespuestaPublica,
    RespuestasPublicasResponse,
)
from app.utils.dependencies import require_api_key_only, require_auth

router = APIRouter(prefix="/actividades", tags=["📝 Actividades"])


@router.post(
    "",
    response_model=ActividadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key_only)],
)
def crear_actividad(actividad_data: ActividadCreate, db: Session = Depends(get_db)):
    """Crear una nueva actividad. Requiere API Key."""
    punto_repo = PuntoRepository(db)
    punto = punto_repo.get_by_id(actividad_data.id_punto)
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

    actividad_repo = ActividadRepository(db)
    nueva_actividad = actividad_repo.create(nueva_actividad)

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
    actividad_repo = ActividadRepository(db)
    actividades = actividad_repo.get_all(skip, limit)
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
    actividad_repo = ActividadRepository(db)
    actividad = actividad_repo.get_by_id(actividad_id)
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
    actividad_repo = ActividadRepository(db)
    actividad = actividad_repo.get_by_id(actividad_id)
    if not actividad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")

    if actividad_data.id_punto:
        punto_repo = PuntoRepository(db)
        punto = punto_repo.get_by_id(actividad_data.id_punto)
        if not punto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El punto especificado no existe",
            )

    update_data = actividad_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(actividad, field, value)

    actividad = actividad_repo.update(actividad)

    log_with_context("info", "Actividad actualizada", actividad_id=actividad.id)

    return actividad


@router.get(
    "/{actividad_id}/respuestas-publicas",
    response_model=RespuestasPublicasResponse,
    summary="Get public responses for an activity",
    description="Returns public responses (messages) from students who completed the activity",
)
def obtener_respuestas_publicas(
    actividad_id: str,
    limit: int = Query(20, ge=1, le=100, description="Maximum number of responses to return"),
    db: Session = Depends(get_db),
    auth=Depends(require_auth),
):
    """
    ## Get Public Responses

    Returns public responses from students who completed a specific activity.

    ### Features
    - ✅ Filters by specific activity ID
    - ✅ Only returns completed responses
    - ✅ Orders by most recent first
    - ✅ Limits results (default: 20, max: 100)
    - ✅ Requires authentication (students and teachers can access)
    - ✅ Does not expose sensitive data

    ### Parameters
    - **actividad_id**: ID of the activity to get responses from
    - **limit**: Maximum number of responses (default: 20, max: 100)

    ### Response Format
    Each response includes:
    - **mensaje**: The text message/response content
    - **fecha**: Completion date and time
    - **usuario**: Student's first name (optional)

    ### Use Cases
    - Display "Message Wall" for activities like "Mi Mensaje para el Mundo"
    - Show community responses to encourage participation
    - Create public galleries of student work

    ### Authentication
    Requires valid JWT token (student or teacher login).
    """
    # Validate that activity exists
    actividad_repo = ActividadRepository(db)
    actividad = actividad_repo.get_by_id(actividad_id)
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actividad no encontrada",
        )

    # Get completed responses with user info
    respuestas_query = (
        db.query(ActividadProgreso, Usuario.nombre)
        .join(Partida, ActividadProgreso.id_juego == Partida.id)
        .join(Usuario, Partida.id_usuario == Usuario.id)
        .filter(
            ActividadProgreso.id_actividad == actividad_id,
            ActividadProgreso.estado == "completado",
            ActividadProgreso.respuesta_contenido.isnot(None),
            ActividadProgreso.respuesta_contenido != "",
        )
        .order_by(ActividadProgreso.fecha_fin.desc())
        .limit(limit)
        .all()
    )

    # Format responses
    respuestas = [
        RespuestaPublica(
            mensaje=progreso.respuesta_contenido,
            fecha=progreso.fecha_fin,
            usuario=nombre,
        )
        for progreso, nombre in respuestas_query
    ]

    log_with_context(
        "info",
        "Respuestas públicas consultadas",
        actividad_id=actividad_id,
        total_respuestas=len(respuestas),
    )

    return RespuestasPublicasResponse(
        actividad_id=actividad_id,
        actividad_nombre=actividad.nombre,
        total_respuestas=len(respuestas),
        respuestas=respuestas,
    )


@router.delete(
    "/{actividad_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key_only)],
)
def eliminar_actividad(actividad_id: str, db: Session = Depends(get_db)):
    """Eliminar una actividad. Requiere API Key."""
    actividad_repo = ActividadRepository(db)
    actividad = actividad_repo.get_by_id(actividad_id)
    if not actividad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")

    actividad_repo.delete(actividad)

    log_with_context("info", "Actividad eliminada", actividad_id=actividad_id)
