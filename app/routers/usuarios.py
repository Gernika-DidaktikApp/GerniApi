import uuid
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_db_operation, log_warning
from app.models.actividad_progreso import ActividadProgreso
from app.models.clase import Clase
from app.models.juego import Partida
from app.models.punto import Punto
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioStatsResponse, UsuarioUpdate
from app.utils.dependencies import (
    AuthResult,
    require_api_key_only,
    require_auth,
    validate_user_ownership,
)
from app.utils.security import hash_password

router = APIRouter(
    prefix="/usuarios",
    tags=["👥 Usuarios"],
    responses={
        404: {"description": "Usuario no encontrado"},
        422: {"description": "Error de validación"},
    },
)


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario en el sistema. Endpoint público para registro.",
)
def crear_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db),
):
    """
    ## Crear Nuevo Usuario (Registro)

    Endpoint público para registrar nuevos usuarios en el sistema.

    ### Validaciones
    - El username debe ser único
    - Si se proporciona id_clase, la clase debe existir
    - La contraseña se hashea automáticamente con bcrypt

    ### Retorna
    Los datos del usuario creado (sin la contraseña)
    """
    existe = db.query(Usuario).filter(Usuario.username == usuario_data.username).first()
    if existe:
        log_warning(
            "Intento de crear usuario con username duplicado",
            username=usuario_data.username,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El username ya está en uso"
        )

    if usuario_data.id_clase:
        clase = db.query(Clase).filter(Clase.id == usuario_data.id_clase).first()
        if not clase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La clase especificada no existe",
            )

    nuevo_usuario = Usuario(
        id=str(uuid.uuid4()),
        username=usuario_data.username,
        nombre=usuario_data.nombre,
        apellido=usuario_data.apellido,
        password=hash_password(usuario_data.password),
        id_clase=usuario_data.id_clase,
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    log_db_operation("CREATE", "usuario", nuevo_usuario.id, username=nuevo_usuario.username)

    return nuevo_usuario


@router.get(
    "",
    response_model=List[UsuarioResponse],
    summary="Listar usuarios",
    description="Obtiene una lista paginada de todos los usuarios registrados.",
    dependencies=[Depends(require_api_key_only)],
)
def listar_usuarios(
    skip: int = Query(0, ge=0, description="Número de registros a saltar (para paginación)"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db),
):
    """
    ## Listar Todos los Usuarios

    Retorna una lista paginada de usuarios. Requiere API Key.

    ### Paginación
    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Número máximo de registros (default: 100, max: 1000)

    ### Ejemplo
    - Para obtener los primeros 10: `?skip=0&limit=10`
    - Para obtener la segunda página: `?skip=10&limit=10`
    """
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Obtener usuario",
    description="Obtiene los detalles de un usuario específico por su ID.",
)
def obtener_usuario(
    usuario_id: str = Path(..., description="ID único del usuario (UUID)"),
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    ## Obtener Usuario por ID

    Retorna los detalles completos de un usuario específico.

    - Con API Key: Puede ver cualquier usuario
    - Con Token: Solo puede ver su propio perfil

    ### Parámetros
    - **usuario_id**: ID único del usuario (UUID)

    ### Errores
    - **404**: Si el usuario no existe
    - **403**: Si intenta acceder al perfil de otro usuario con Token
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    validate_user_ownership(auth, usuario_id)

    return usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(
    usuario_id: str,
    usuario_data: UsuarioUpdate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Actualizar un usuario existente.

    - Con API Key: Puede actualizar cualquier usuario
    - Con Token: Solo puede actualizar su propio perfil
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    validate_user_ownership(auth, usuario_id)

    if usuario_data.username and usuario_data.username != usuario.username:
        existe = db.query(Usuario).filter(Usuario.username == usuario_data.username).first()
        if existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El username ya está en uso",
            )

    if usuario_data.id_clase:
        clase = db.query(Clase).filter(Clase.id == usuario_data.id_clase).first()
        if not clase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La clase especificada no existe",
            )

    update_data = usuario_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    for field, value in update_data.items():
        setattr(usuario, field, value)

    db.commit()
    db.refresh(usuario)

    log_db_operation("UPDATE", "usuario", usuario.id, campos_actualizados=list(update_data.keys()))

    return usuario


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key_only)],
)
def eliminar_usuario(usuario_id: str, db: Session = Depends(get_db)):
    """Eliminar un usuario. Requiere API Key."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    db.delete(usuario)
    db.commit()

    log_db_operation("DELETE", "usuario", usuario_id)


@router.get(
    "/{usuario_id}/estadisticas",
    response_model=UsuarioStatsResponse,
    summary="Obtener estadísticas del usuario",
    description="Obtiene estadísticas detalladas para el perfil del usuario en la app móvil",
)
def obtener_estadisticas_usuario(
    usuario_id: str = Path(..., description="ID único del usuario (UUID)"),
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    ## Obtener Estadísticas del Usuario

    Retorna estadísticas detalladas del usuario para mostrar en el perfil de la app móvil.

    ### Información Incluida
    - **actividades_completadas**: Número de actividades completadas
    - **racha_dias**: Días consecutivos de juego (desde hoy hacia atrás)
    - **modulos_completados**: Lista de módulos/actividades completadas
    - **ultima_partida**: Fecha de la última partida jugada
    - **total_puntos_acumulados**: Suma de todos los puntos obtenidos

    ### Autenticación
    - Con API Key: Puede ver estadísticas de cualquier usuario
    - Con Token: Solo puede ver sus propias estadísticas

    ### Errores
    - **404**: Si el usuario no existe
    - **403**: Si intenta acceder a estadísticas de otro usuario con Token
    """
    # Verificar que el usuario existe
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    # Validar ownership
    validate_user_ownership(auth, usuario_id)

    # 1. Actividades completadas
    actividades_completadas = (
        db.query(func.count(ActividadProgreso.id))
        .join(Partida, ActividadProgreso.id_juego == Partida.id)
        .filter(and_(Partida.id_usuario == usuario_id, ActividadProgreso.estado == "completado"))
        .scalar()
        or 0
    )

    # 2. Racha de días consecutivos
    # Obtener todas las fechas distintas donde el usuario jugó (ordenadas DESC)
    fechas_juego = (
        db.query(func.date(Partida.fecha_inicio))
        .filter(Partida.id_usuario == usuario_id)
        .distinct()
        .order_by(func.date(Partida.fecha_inicio).desc())
        .all()
    )

    racha_dias = 0
    if fechas_juego:
        hoy = datetime.now().date()
        fechas_set = {fecha[0] for fecha in fechas_juego}

        # Calcular racha desde hoy hacia atrás
        fecha_actual = hoy
        while fecha_actual in fechas_set:
            racha_dias += 1
            fecha_actual -= timedelta(days=1)

    # 3. Módulos completados (puntos con al menos 1 actividad completada)
    modulos_completados_query = (
        db.query(Punto.nombre)
        .join(ActividadProgreso, Punto.id == ActividadProgreso.id_punto)
        .join(Partida, ActividadProgreso.id_juego == Partida.id)
        .filter(and_(Partida.id_usuario == usuario_id, ActividadProgreso.estado == "completado"))
        .distinct()
        .all()
    )
    modulos_completados = [modulo[0] for modulo in modulos_completados_query]

    # 4. Última partida
    ultima_partida_obj = (
        db.query(Partida.fecha_inicio)
        .filter(Partida.id_usuario == usuario_id)
        .order_by(Partida.fecha_inicio.desc())
        .first()
    )
    ultima_partida = ultima_partida_obj[0] if ultima_partida_obj else None

    # 5. Total puntos acumulados
    total_puntos = (
        db.query(func.sum(ActividadProgreso.puntuacion))
        .join(Partida, ActividadProgreso.id_juego == Partida.id)
        .filter(and_(Partida.id_usuario == usuario_id, ActividadProgreso.puntuacion.isnot(None)))
        .scalar()
        or 0.0
    )

    return UsuarioStatsResponse(
        actividades_completadas=actividades_completadas,
        racha_dias=racha_dias,
        modulos_completados=modulos_completados,
        ultima_partida=ultima_partida,
        total_puntos_acumulados=float(total_puntos),
    )
