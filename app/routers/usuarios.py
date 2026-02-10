"""Router de gestión de usuarios.

Este módulo maneja todos los endpoints relacionados con usuarios:
creación, listado, actualización, eliminación, importación masiva y estadísticas.

Arquitectura (Clean Architecture - 3 capas):
- Router (presentación): Coordina requests HTTP, autenticación y respuestas
- UsuarioService (negocio): Lógica CRUD de usuarios y validaciones
- UsuarioStatsService (negocio): Cálculo de estadísticas complejas
- Repositorios (datos): Acceso abstracto a base de datos

El router mantiene:
- Validaciones de autenticación (validate_user_ownership, require_auth)
- Audit logging (AuditLogWeb para trazabilidad)
- Logging estructurado de aplicación web (log_info, log_warning)

Autor: Gernibide
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_info, log_warning
from app.models.audit_log import AuditLogWeb
from app.repositories.clase_repository import ClaseRepository
from app.schemas.usuario import (
    PerfilProgreso,
    UsuarioBulkCreate,
    UsuarioBulkResponse,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioStatsResponse,
    UsuarioUpdate,
)
from app.services.usuario_perfil_service import UsuarioPerfilService
from app.services.usuario_service import UsuarioService
from app.services.usuario_stats_service import UsuarioStatsService
from app.utils.dependencies import (
    AuthResult,
    get_clase_repository,
    get_usuario_perfil_service,
    get_usuario_service,
    get_usuario_stats_service,
    require_api_key_only,
    require_auth,
    validate_user_ownership,
)

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
    usuario_service: UsuarioService = Depends(get_usuario_service),
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
    # Delegar al servicio
    nuevo_usuario = usuario_service.crear_usuario(usuario_data)

    # Log estructurado (MANTENER en router - es logging de aplicación web)
    log_info(
        "Usuario creado",
        usuario_id=nuevo_usuario.id,
        username=nuevo_usuario.username,
        nombre=f"{nuevo_usuario.nombre} {nuevo_usuario.apellido}",
        id_clase=nuevo_usuario.id_clase,
    )

    return nuevo_usuario


@router.post(
    "/bulk",
    response_model=UsuarioBulkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear múltiples usuarios",
    description="Crea múltiples usuarios de forma transaccional (todo o nada).",
)
def crear_usuarios_bulk(
    usuarios_data: UsuarioBulkCreate,
    db: Session = Depends(get_db),  # MANTENER para audit log
    auth: AuthResult = Depends(require_auth),
    usuario_service: UsuarioService = Depends(get_usuario_service),
    clase_repo: ClaseRepository = Depends(get_clase_repository),
):
    """
    ## Crear Múltiples Usuarios (Importación Masiva)

    Endpoint para importar múltiples usuarios de forma transaccional.
    Si algún usuario falla la validación, ninguno se crea (rollback).

    ### Validaciones
    - Todos los usernames deben ser únicos (entre sí y con los existentes)
    - Si se proporciona id_clase, la clase debe existir
    - Las contraseñas se hashean automáticamente con bcrypt

    ### Retorna
    - **usuarios_creados**: Lista de usuarios creados exitosamente
    - **total**: Número total de usuarios creados
    - **errores**: Lista de errores si los hubo (en validación previa)
    """
    # Log inicio de importación
    log_info(
        "Iniciando importación masiva de usuarios",
        total_usuarios=len(usuarios_data.usuarios),
        id_clase=usuarios_data.id_clase,
        auth_type="api_key" if auth.is_api_key else "token",
    )

    try:
        # Delegar al servicio (incluye validaciones + creación)
        usuarios_creados, errores = usuario_service.crear_usuarios_bulk(usuarios_data, db)

        # Log estructurado de éxito
        log_info(
            "Importación masiva completada exitosamente",
            total_usuarios=len(usuarios_creados),
            id_clase=usuarios_data.id_clase,
            usernames=", ".join([u.username for u in usuarios_creados]),
            auth_type="api_key" if auth.is_api_key else "token",
        )

        # Audit log (MANTENER en router - es infraestructura, no negocio)
        clase_info = ""
        profesor_id = None
        if usuarios_data.id_clase:
            clase = clase_repo.get_by_id(usuarios_data.id_clase)
            if clase:
                clase_info = f" en clase '{clase.nombre}'"
                profesor_id = clase.id_profesor

        audit_log = AuditLogWeb(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            profesor_id=profesor_id,
            accion="IMPORTAR_USUARIOS_MASIVO",
            detalles=f"{len(usuarios_creados)} usuarios importados{clase_info}. "
            f"Usernames: {', '.join([u.username for u in usuarios_creados])}",
            tipo="web",
        )
        db.add(audit_log)
        db.commit()

        return UsuarioBulkResponse(
            usuarios_creados=usuarios_creados,
            total=len(usuarios_creados),
            errores=errores,
        )

    except HTTPException:
        log_info(
            "Importación masiva cancelada por validación",
            total_usuarios=len(usuarios_data.usuarios),
            id_clase=usuarios_data.id_clase,
        )
        raise
    except Exception as e:
        log_warning(
            "Error inesperado en importación masiva de usuarios",
            error=str(e),
            total_usuarios=len(usuarios_data.usuarios),
            id_clase=usuarios_data.id_clase,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuarios: {str(e)}",
        )


@router.get(
    "",
    response_model=list[UsuarioResponse],
    summary="Listar usuarios",
    description="Obtiene una lista paginada de todos los usuarios registrados.",
    dependencies=[Depends(require_api_key_only)],
)
def listar_usuarios(
    skip: int = Query(0, ge=0, description="Número de registros a saltar (para paginación)"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    usuario_service: UsuarioService = Depends(get_usuario_service),
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
    return usuario_service.listar_usuarios(skip, limit)


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Obtener usuario",
    description="Obtiene los detalles de un usuario específico por su ID.",
)
def obtener_usuario(
    usuario_id: str = Path(..., description="ID único del usuario (UUID)"),
    auth: AuthResult = Depends(require_auth),
    usuario_service: UsuarioService = Depends(get_usuario_service),
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
    # Validación de ownership (MANTENER en router - es autorización, no negocio)
    validate_user_ownership(auth, usuario_id)

    # Delegar al servicio
    return usuario_service.obtener_usuario(usuario_id)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(
    usuario_id: str,
    usuario_data: UsuarioUpdate,
    auth: AuthResult = Depends(require_auth),
    usuario_service: UsuarioService = Depends(get_usuario_service),
):
    """Actualizar un usuario existente.

    Args:
        usuario_id: ID único del usuario.
        usuario_data: Datos a actualizar.
        auth: Resultado de autenticación.
        usuario_service: Servicio de usuarios.

    Returns:
        Datos actualizados del usuario.

    Raises:
        HTTPException: Si el usuario no existe, el username está en uso,
            o la clase especificada no existe.

    Note:
        - Con API Key: Puede actualizar cualquier usuario
        - Con Token: Solo puede actualizar su propio perfil
    """
    # Validación de ownership (MANTENER en router - es autorización, no negocio)
    validate_user_ownership(auth, usuario_id)

    # Delegar al servicio
    return usuario_service.actualizar_usuario(usuario_id, usuario_data)


@router.post("/{usuario_id}/remove-from-class", status_code=status.HTTP_204_NO_CONTENT)
def remover_alumno_de_clase(
    usuario_id: str,
    auth: AuthResult = Depends(require_auth),
    usuario_service: UsuarioService = Depends(get_usuario_service),
):
    """Remover alumno de su clase asignada (id_clase = NULL).

    Args:
        usuario_id: ID único del usuario.
        auth: Resultado de autenticación.
        usuario_service: Servicio de usuarios.

    Raises:
        HTTPException: Si el usuario no existe.

    Note:
        Solo accesible con API Key.
    """
    from app.models.usuario import Usuario
    from app.schemas.usuario import UsuarioUpdate

    # Solo con API Key
    if not auth.is_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operación requiere API Key",
        )

    # Actualizar usuario para quitar clase
    usuario_data = UsuarioUpdate(id_clase=None)
    usuario_service.actualizar_usuario(usuario_id, usuario_data)

    return None


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key_only)],
)
def eliminar_usuario(
    usuario_id: str,
    usuario_service: UsuarioService = Depends(get_usuario_service),
):
    """Eliminar un usuario del sistema.

    Args:
        usuario_id: ID único del usuario a eliminar.
        usuario_service: Servicio de usuarios.

    Raises:
        HTTPException: Si el usuario no existe.

    Note:
        Requiere API Key.
    """
    usuario_service.eliminar_usuario(usuario_id)


@router.get(
    "/{usuario_id}/estadisticas",
    response_model=UsuarioStatsResponse,
    summary="Obtener estadísticas del usuario",
    description="Obtiene estadísticas detalladas para el perfil del usuario en la app móvil",
)
def obtener_estadisticas_usuario(
    usuario_id: str = Path(..., description="ID único del usuario (UUID)"),
    auth: AuthResult = Depends(require_auth),
    usuario_service: UsuarioService = Depends(get_usuario_service),
    stats_service: UsuarioStatsService = Depends(get_usuario_stats_service),
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
    usuario_service.obtener_usuario(usuario_id)  # Lanza 404 si no existe

    # Validar ownership (MANTENER en router - es autorización, no negocio)
    validate_user_ownership(auth, usuario_id)

    # Delegar al servicio de estadísticas
    return stats_service.obtener_estadisticas(usuario_id)


@router.get(
    "/{usuario_id}/perfil-progreso",
    response_model=PerfilProgreso,
    summary="Obtener perfil y progreso completo del usuario",
    description="Obtiene el perfil completo con progreso detallado de todas las actividades para la app móvil",
)
def obtener_perfil_progreso(
    usuario_id: str = Path(..., description="ID único del usuario (UUID)"),
    auth: AuthResult = Depends(require_auth),
    usuario_service: UsuarioService = Depends(get_usuario_service),
    perfil_service: UsuarioPerfilService = Depends(get_usuario_perfil_service),
):
    """
    ## Obtener Perfil y Progreso Completo del Usuario (App Móvil)

    Endpoint diseñado para la app móvil que retorna información completa:

    ### Información Incluida
    - **usuario**: Datos del perfil (id, username, nombre, apellido, clase, fecha creación, top_score)
    - **estadisticas**: Estadísticas generales de progreso
        - Total de actividades disponibles vs completadas
        - Porcentaje de progreso global
        - Total de puntos acumulados
        - Racha de días consecutivos
        - Fecha de última partida
        - Puntos/módulos completados
    - **puntos**: Lista de todos los puntos/módulos con:
        - Información del punto
        - Progreso (actividades completadas, porcentaje, puntos obtenidos)
        - **actividades**: Array de TODAS las actividades del punto
            - Estado: no_iniciada, en_progreso, completada
            - Puntuación (si está completada)
            - Fecha de completado (si está completada)
            - Duración (si está completada)

    ### Autenticación
    - Con API Key: Puede ver perfil de cualquier usuario
    - Con Token: Solo puede ver su propio perfil

    ### Diferencias con /estadisticas
    - Este endpoint es más completo y detallado
    - Incluye TODAS las actividades (hechas y no hechas)
    - Organizado por puntos/módulos
    - Ideal para mostrar progreso visual en la app

    ### Errores
    - **404**: Si el usuario no existe
    - **403**: Si intenta acceder al perfil de otro usuario con Token
    """
    # Verificar que el usuario existe
    usuario_service.obtener_usuario(usuario_id)  # Lanza 404 si no existe

    # Validar ownership (MANTENER en router - es autorización, no negocio)
    validate_user_ownership(auth, usuario_id)

    # Delegar al servicio de perfil
    return perfil_service.obtener_perfil_progreso(usuario_id)
