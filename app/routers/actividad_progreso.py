"""Router de gestión de progreso de actividades.

Este módulo maneja el seguimiento del progreso de los usuarios en las actividades,
incluyendo inicio, completado, resumen de puntos y reseteo de progresos.

Autor: Gernibide
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_with_context
from app.models.actividad import Actividad as ActividadModel
from app.models.actividad_progreso import ActividadProgreso
from app.models.audit_log import AuditLogApp
from app.models.juego import Partida
from app.models.punto import Punto
from app.schemas.actividad_progreso import (
    ActividadProgresoCompletar,
    ActividadProgresoCreate,
    ActividadProgresoResponse,
    ActividadProgresoUpdate,
    PuntoResumen,
)
from app.utils.dependencies import (
    AuthResult,
    require_api_key_only,
    require_auth,
    validate_partida_ownership,
)

router = APIRouter(prefix="/actividad-progreso", tags=["📊 Progreso"])


@router.post("/iniciar", response_model=ActividadProgresoResponse)
def iniciar_actividad(
    estado_data: ActividadProgresoCreate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Iniciar una actividad dentro de un punto (IDEMPOTENTE).

    Crea un nuevo registro de progreso de actividad con estado 'en_progreso'.
    La fecha de inicio se registra automáticamente.

    **Comportamiento Idempotente:**
    - Si la actividad ya está en progreso → Devuelve el progreso existente (200 OK)
    - Si la actividad no está iniciada → Crea nuevo progreso (201 Created)
    - Si la actividad está completada → Crea nuevo intento (201 Created)

    Esto permite que la app móvil pueda:
    - Reintentar llamadas sin errores
    - Cerrar y abrir la app sin perder el progreso_id
    - Manejar reconexiones automáticamente

    - Con API Key: Puede iniciar actividades para cualquier partida
    - Con Token: Solo puede iniciar actividades para sus propias partidas
    """
    validate_partida_ownership(auth, estado_data.id_juego, db)

    punto = db.query(Punto).filter(Punto.id == estado_data.id_punto).first()
    if not punto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El punto especificado no existe",
        )

    actividad = (
        db.query(ActividadModel)
        .filter(
            ActividadModel.id == estado_data.id_actividad,
            ActividadModel.id_punto == estado_data.id_punto,
        )
        .first()
    )
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La actividad especificada no existe o no pertenece a este punto",
        )

    # Buscar si ya existe un progreso "en_progreso"
    progreso_existente = (
        db.query(ActividadProgreso)
        .filter(
            ActividadProgreso.id_juego == estado_data.id_juego,
            ActividadProgreso.id_actividad == estado_data.id_actividad,
            ActividadProgreso.estado == "en_progreso",
        )
        .first()
    )

    # Si ya existe en progreso, devolverlo (IDEMPOTENTE)
    if progreso_existente:
        log_with_context(
            "info",
            "Actividad ya iniciada - Devolviendo progreso existente",
            estado_id=progreso_existente.id,
            punto_id=estado_data.id_punto,
            is_retry=True,
        )
        return progreso_existente

    # Si no existe, crear uno nuevo
    nuevo_estado = ActividadProgreso(
        id=str(uuid.uuid4()),
        id_juego=estado_data.id_juego,
        id_punto=estado_data.id_punto,
        id_actividad=estado_data.id_actividad,
        estado="en_progreso",
    )

    db.add(nuevo_estado)
    db.commit()
    db.refresh(nuevo_estado)

    log_with_context(
        "info",
        "Actividad iniciada - Nuevo progreso creado",
        estado_id=nuevo_estado.id,
        punto_id=estado_data.id_punto,
        is_retry=False,
    )

    return nuevo_estado


@router.put("/{estado_id}/completar", response_model=ActividadProgresoResponse)
def completar_actividad(
    estado_id: str,
    data: ActividadProgresoCompletar,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Completar una actividad y registrar su puntuación.

    - Calcula automáticamente la duración de la actividad
    - Actualiza el estado a 'completado'
    - Registra la puntuación obtenida

    - Con API Key: Puede completar actividades de cualquier partida
    - Con Token: Solo puede completar actividades de sus propias partidas
    """
    estado = db.query(ActividadProgreso).filter(ActividadProgreso.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progreso de actividad no encontrado",
        )

    validate_partida_ownership(auth, estado.id_juego, db)

    if estado.estado != "en_progreso":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La actividad no está en progreso. Estado actual: {estado.estado}",
        )

    estado.fecha_fin = datetime.now()
    estado.duracion = int((estado.fecha_fin - estado.fecha_inicio).total_seconds())
    estado.estado = "completado"
    estado.puntuacion = data.puntuacion
    if data.respuesta_contenido is not None:
        estado.respuesta_contenido = data.respuesta_contenido

    db.commit()
    db.refresh(estado)

    log_with_context(
        "info",
        "Actividad completada",
        estado_id=estado.id,
        punto_id=estado.id_punto,
        puntuacion=data.puntuacion,
        duracion=estado.duracion,
    )

    # Verificar si se completaron TODOS los actividades del punto
    actividades_totales = (
        db.query(ActividadModel).filter(ActividadModel.id_punto == estado.id_punto).count()
    )
    actividades_completadas = (
        db.query(ActividadProgreso)
        .filter(
            ActividadProgreso.id_juego == estado.id_juego,
            ActividadProgreso.id_punto == estado.id_punto,
            ActividadProgreso.estado == "completado",
        )
        .count()
    )

    # Si se completaron todas las actividades, registrar audit log (SOLO para app móvil)
    if actividades_completadas == actividades_totales:
        partida = db.query(Partida).filter(Partida.id == estado.id_juego).first()
        punto = db.query(Punto).filter(Punto.id == estado.id_punto).first()

        if partida and punto:
            # Crear audit log de tipo App
            audit_log = AuditLogApp(
                id=str(uuid.uuid4()),
                usuario_id=partida.id_usuario,
                accion="completar_punto",
                detalles=f"Punto '{punto.nombre}' completado con {actividades_totales} actividades. Puntuación total: {data.puntuacion}",
                device_type=data.device_type if hasattr(data, "device_type") else None,
                app_version=data.app_version if hasattr(data, "app_version") else None,
            )
            db.add(audit_log)
            db.commit()

            log_with_context(
                "info",
                "Punto completado - Audit log creado",
                punto_id=estado.id_punto,
                usuario_id=partida.id_usuario,
                actividades_completadas=actividades_totales,
            )

    return estado


@router.get("/punto/{id_juego}/{id_punto}/resumen", response_model=PuntoResumen)
def obtener_resumen_punto(
    id_juego: str,
    id_punto: str,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Obtener resumen calculado de un punto.

    Calcula desde actividad_progreso:
    - Actividades totales, completadas y en progreso
    - Puntuación total (suma de puntuaciones de actividades)
    - Duración total
    - Estado del punto (no_iniciada, en_progreso, completada)
    """
    validate_partida_ownership(auth, id_juego, db)

    # Verificar que el punto existe
    punto = db.query(Punto).filter(Punto.id == id_punto).first()
    if not punto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Punto no encontrado",
        )

    # Contar actividades totales de este punto
    actividades_totales = (
        db.query(ActividadModel).filter(ActividadModel.id_punto == id_punto).count()
    )

    # Obtener estados de actividades para esta partida y punto
    estados = (
        db.query(ActividadProgreso)
        .filter(
            ActividadProgreso.id_juego == id_juego,
            ActividadProgreso.id_punto == id_punto,
        )
        .all()
    )

    actividades_completadas = sum(1 for e in estados if e.estado == "completado")
    actividades_en_progreso = sum(1 for e in estados if e.estado == "en_progreso")

    # Calcular puntuación total
    puntuacion_total = sum(e.puntuacion or 0 for e in estados if e.estado == "completado")

    # Calcular duración total
    duracion_total = sum(e.duracion or 0 for e in estados if e.duracion is not None)

    # Determinar fechas
    fecha_inicio = min((e.fecha_inicio for e in estados), default=None) if estados else None
    fechas_fin = [e.fecha_fin for e in estados if e.fecha_fin is not None]
    fecha_fin = (
        max(fechas_fin) if fechas_fin and actividades_completadas == actividades_totales else None
    )

    # Determinar estado del punto
    if not estados:
        estado = "no_iniciada"
    elif actividades_completadas == actividades_totales:
        estado = "completada"
    else:
        estado = "en_progreso"

    return PuntoResumen(
        id_juego=id_juego,
        id_punto=id_punto,
        nombre_punto=punto.nombre,
        actividades_totales=actividades_totales,
        actividades_completadas=actividades_completadas,
        actividades_en_progreso=actividades_en_progreso,
        puntuacion_total=puntuacion_total,
        duracion_total=duracion_total if duracion_total > 0 else None,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado=estado,
    )


@router.post("", response_model=ActividadProgresoResponse, status_code=status.HTTP_201_CREATED)
def crear_actividad_progreso(
    estado_data: ActividadProgresoCreate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Crear un nuevo progreso de actividad.

    - Con API Key: Puede crear progresos para cualquier partida
    - Con Token: Solo puede crear progresos para sus propias partidas
    """
    validate_partida_ownership(auth, estado_data.id_juego, db)

    punto = db.query(Punto).filter(Punto.id == estado_data.id_punto).first()
    if not punto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El punto especificado no existe",
        )

    actividad = (
        db.query(ActividadModel)
        .filter(
            ActividadModel.id == estado_data.id_actividad,
            ActividadModel.id_punto == estado_data.id_punto,
        )
        .first()
    )
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La actividad especificada no existe o no pertenece a este punto",
        )

    nuevo_estado = ActividadProgreso(
        id=str(uuid.uuid4()),
        id_juego=estado_data.id_juego,
        id_punto=estado_data.id_punto,
        id_actividad=estado_data.id_actividad,
        estado="en_progreso",
    )

    db.add(nuevo_estado)
    db.commit()
    db.refresh(nuevo_estado)

    log_with_context("info", "Progreso de actividad creado", estado_id=nuevo_estado.id)

    return nuevo_estado


@router.get(
    "",
    response_model=list[ActividadProgresoResponse],
    dependencies=[Depends(require_api_key_only)],
)
def listar_actividad_progresos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de progresos de actividad. Requiere API Key."""
    estados = db.query(ActividadProgreso).offset(skip).limit(limit).all()
    return estados


@router.get("/{estado_id}", response_model=ActividadProgresoResponse)
def obtener_actividad_progreso(
    estado_id: str,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Obtener un progreso de actividad por ID.

    - Con API Key: Puede ver cualquier progreso
    - Con Token: Solo puede ver progresos de sus propias partidas
    """
    estado = db.query(ActividadProgreso).filter(ActividadProgreso.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progreso de actividad no encontrado",
        )

    validate_partida_ownership(auth, estado.id_juego, db)

    return estado


@router.put("/{estado_id}", response_model=ActividadProgresoResponse)
def actualizar_actividad_progreso(
    estado_id: str,
    estado_data: ActividadProgresoUpdate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Actualizar un progreso de actividad existente.

    - Con API Key: Puede actualizar cualquier progreso
    - Con Token: Solo puede actualizar progresos de sus propias partidas

    Restricción: Solo se puede actualizar respuesta_contenido si la actividad está completada.
    """
    estado = db.query(ActividadProgreso).filter(ActividadProgreso.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progreso de actividad no encontrado",
        )

    validate_partida_ownership(auth, estado.id_juego, db)

    update_data = estado_data.model_dump(exclude_unset=True)

    # Validar que respuesta_contenido solo se actualice si está completada
    if "respuesta_contenido" in update_data and estado.estado != "completado":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede actualizar respuesta_contenido cuando la actividad está completada",
        )

    for field, value in update_data.items():
        setattr(estado, field, value)

    db.commit()
    db.refresh(estado)

    log_with_context("info", "Progreso de actividad actualizado", estado_id=estado.id)

    return estado


@router.post("/punto/{id_juego}/{id_punto}/reset", status_code=status.HTTP_200_OK)
def resetear_punto(
    id_juego: str,
    id_punto: str,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Resetear un punto para permitir repetirla.

    Elimina todos los actividad_progresos del punto para la partida especificada,
    permitiendo al usuario volver a iniciar y completar las actividades desde cero.

    - Con API Key: Puede resetear puntos de cualquier partida
    - Con Token: Solo puede resetear puntos de sus propias partidas
    """
    validate_partida_ownership(auth, id_juego, db)

    # Verificar que el punto existe
    punto = db.query(Punto).filter(Punto.id == id_punto).first()
    if not punto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Punto no encontrado",
        )

    # Buscar todos los actividad_progresos de este punto para esta partida
    estados = (
        db.query(ActividadProgreso)
        .filter(
            ActividadProgreso.id_juego == id_juego,
            ActividadProgreso.id_punto == id_punto,
        )
        .all()
    )

    if not estados:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay progresos de actividades para esta actividad en esta partida",
        )

    # Contar progresos antes de eliminar
    total_eliminados = len(estados)

    # Eliminar todos los actividad_progresos
    for estado in estados:
        db.delete(estado)

    db.commit()

    log_with_context(
        "info",
        "Punto reseteado",
        id_juego=id_juego,
        id_punto=id_punto,
        progresos_eliminados=total_eliminados,
    )

    return {
        "mensaje": "Punto reseteado exitosamente",
        "id_juego": id_juego,
        "id_punto": id_punto,
        "actividades_reseteadas": total_eliminados,
    }


@router.delete(
    "/{estado_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key_only)],
)
def eliminar_actividad_progreso(estado_id: str, db: Session = Depends(get_db)):
    """Eliminar un progreso de actividad. Requiere API Key."""
    estado = db.query(ActividadProgreso).filter(ActividadProgreso.id == estado_id).first()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progreso de actividad no encontrado",
        )

    db.delete(estado)
    db.commit()

    log_with_context("info", "Progreso de actividad eliminado", estado_id=estado_id)
