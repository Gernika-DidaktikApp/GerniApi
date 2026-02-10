"""Schemas Pydantic para gestión de usuarios.

Este módulo define los modelos de validación y serialización para todas las
operaciones relacionadas con usuarios, incluyendo autenticación, CRUD,
estadísticas y operaciones masivas.

Autor: Gernibide
"""

from datetime import datetime

from pydantic import BaseModel, Field


class LoginAppRequest(BaseModel):
    """Credenciales para autenticación de usuario.

    Modelo de validación para las solicitudes de login desde la aplicación móvil.

    Attributes:
        username: Nombre de usuario único en el sistema.
        password: Contraseña del usuario en texto plano (será hasheada).
    """

    username: str = Field(..., min_length=1, description="Nombre de usuario", example="usuario123")
    password: str = Field(
        ..., min_length=1, description="Contraseña del usuario", example="password123"
    )


class UsuarioCreate(BaseModel):
    """Datos para crear un nuevo usuario.

    Modelo de validación para la creación de usuarios. Requiere todos los campos
    obligatorios y valida longitudes y formatos.

    Attributes:
        username: Nombre de usuario único (3-45 caracteres).
        nombre: Nombre del usuario (1-45 caracteres).
        apellido: Apellido del usuario (1-45 caracteres).
        password: Contraseña en texto plano (4-100 caracteres, será hasheada con bcrypt).
        id_clase: ID de la clase asignada (UUID), opcional.
        codigo_clase: Código corto de la clase (6 caracteres, ej: A3X9K2), opcional.

    Note:
        Si se proporciona codigo_clase, se usará en lugar de id_clase.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=45,
        description="Nombre de usuario único",
        example="usuario123",
    )
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=45,
        description="Nombre del usuario",
        example="Juan",
    )
    apellido: str = Field(
        ...,
        min_length=1,
        max_length=45,
        description="Apellido del usuario",
        example="Pérez",
    )
    password: str = Field(
        ...,
        min_length=4,
        max_length=100,
        description="Contraseña (será hasheada con bcrypt)",
        example="password123",
    )
    id_clase: str | None = Field(
        None,
        description="ID de la clase asignada (opcional, usar codigo_clase es más fácil)",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    codigo_clase: str | None = Field(
        None,
        min_length=6,
        max_length=6,
        description="Código de la clase para unirse (6 caracteres, ej: A3X9K2)",
        example="A3X9K2",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "usuario123",
                    "nombre": "Juan",
                    "apellido": "Pérez",
                    "password": "password123",
                    "id_clase": None,
                }
            ]
        }
    }


class UsuarioUpdate(BaseModel):
    """Datos para actualizar un usuario existente.

    Modelo de validación para actualización parcial de usuarios. Todos los campos
    son opcionales, solo se actualizan los campos proporcionados.

    Attributes:
        username: Nuevo nombre de usuario (3-45 caracteres), opcional.
        nombre: Nuevo nombre (1-45 caracteres), opcional.
        apellido: Nuevo apellido (1-45 caracteres), opcional.
        password: Nueva contraseña (4-100 caracteres, será hasheada), opcional.
        id_clase: Nueva clase asignada (UUID), opcional.
        top_score: Nueva puntuación máxima, opcional.
    """

    username: str | None = Field(
        None,
        min_length=3,
        max_length=45,
        description="Nuevo username",
        example="usuario_nuevo",
    )
    nombre: str | None = Field(
        None, min_length=1, max_length=45, description="Nuevo nombre", example="Pedro"
    )
    apellido: str | None = Field(
        None,
        min_length=1,
        max_length=45,
        description="Nuevo apellido",
        example="García",
    )
    password: str | None = Field(
        None,
        min_length=4,
        max_length=100,
        description="Nueva contraseña",
        example="newpassword123",
    )
    id_clase: str | None = Field(
        None,
        description="Nueva clase asignada",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    top_score: int | None = Field(None, description="Nueva puntuación máxima", example=1500)

    model_config = {"json_schema_extra": {"examples": [{"nombre": "Pedro", "apellido": "García"}]}}


class LoginAppResponse(BaseModel):
    """Respuesta de login con token y datos del usuario.

    Modelo de respuesta tras autenticación exitosa. Incluye token JWT y
    datos básicos del usuario para la sesión.

    Attributes:
        access_token: Token JWT para autenticación en solicitudes posteriores.
        token_type: Tipo de token (siempre "bearer").
        user_id: ID único del usuario (UUID).
        username: Nombre de usuario.
        nombre: Nombre del usuario.
        apellido: Apellido del usuario.
    """

    access_token: str = Field(..., description="Token JWT para autenticación")
    token_type: str = Field(default="bearer", description="Tipo de token")
    user_id: str = Field(..., description="ID único del usuario (UUID)")
    username: str = Field(..., description="Nombre de usuario")
    nombre: str = Field(..., description="Nombre del usuario")
    apellido: str = Field(..., description="Apellido del usuario")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "usuario123",
                    "nombre": "Juan",
                    "apellido": "Pérez",
                }
            ]
        }
    }


class UsuarioResponse(BaseModel):
    """Respuesta con los datos del usuario.

    Modelo de respuesta con información completa del usuario, excluyendo
    la contraseña por seguridad.

    Attributes:
        id: ID único del usuario (UUID).
        username: Nombre de usuario.
        nombre: Nombre del usuario.
        apellido: Apellido del usuario.
        id_clase: ID de la clase asignada (UUID), puede ser None.
        creation: Fecha y hora de creación de la cuenta.
        top_score: Puntuación máxima alcanzada por el usuario.
    """

    id: str = Field(
        ...,
        description="ID único del usuario (UUID)",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    username: str = Field(..., description="Nombre de usuario", example="usuario123")
    nombre: str = Field(..., description="Nombre", example="Juan")
    apellido: str = Field(..., description="Apellido", example="Pérez")
    id_clase: str | None = Field(
        None,
        description="ID de la clase asignada",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    creation: datetime = Field(
        ..., description="Fecha de creación de la cuenta", example="2024-01-15T10:30:00"
    )
    top_score: int = Field(..., description="Puntuación máxima alcanzada", example=1000)

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "usuario123",
                    "nombre": "Juan",
                    "apellido": "Pérez",
                    "id_clase": None,
                    "creation": "2024-01-15T10:30:00",
                    "top_score": 1000,
                }
            ]
        },
    }


class UsuarioStatsResponse(BaseModel):
    """Estadísticas detalladas del usuario para la app móvil.

    Modelo de respuesta con estadísticas completas de progreso y actividad
    del usuario en el juego.

    Attributes:
        actividades_completadas: Número total de actividades terminadas.
        racha_dias: Días consecutivos de juego desde hoy hacia atrás.
        modulos_completados: Lista de nombres de módulos/actividades completados.
        ultima_partida: Fecha y hora de la última partida jugada, puede ser None.
        total_puntos_acumulados: Suma de todos los puntos obtenidos en actividades.
    """

    actividades_completadas: int = Field(
        ...,
        description="Número total de actividades completadas",
        example=12,
    )
    racha_dias: int = Field(
        ...,
        description="Días consecutivos que el usuario ha jugado (desde hoy hacia atrás)",
        example=5,
    )
    modulos_completados: list[str] = Field(
        ...,
        description="Lista de nombres de módulos/actividades que ha completado al menos una vez",
        example=["Árbol del Gernika", "Museo de la Paz"],
    )
    ultima_partida: datetime | None = Field(
        None,
        description="Fecha y hora de la última partida jugada",
        example="2024-01-20T15:30:00",
    )
    total_puntos_acumulados: float = Field(
        ...,
        description="Suma total de todos los puntos obtenidos en actividades completadas",
        example=1850.5,
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "actividades_completadas": 12,
                    "racha_dias": 5,
                    "modulos_completados": ["Árbol del Gernika", "Museo de la Paz", "Plaza"],
                    "ultima_partida": "2024-01-20T15:30:00",
                    "total_puntos_acumulados": 1850.5,
                }
            ]
        }
    }


class UsuarioBulkCreate(BaseModel):
    """Datos para crear múltiples usuarios de forma masiva.

    Modelo de validación para operaciones de creación masiva de usuarios,
    típicamente desde importación CSV.

    Attributes:
        usuarios: Lista de usuarios a crear (mínimo 1).
        id_clase: ID de clase para asignar a todos los usuarios (UUID), opcional.
    """

    usuarios: list[UsuarioCreate] = Field(
        ...,
        description="Lista de usuarios a crear",
        min_length=1,
    )
    id_clase: str | None = Field(
        None,
        description="ID de la clase para asignar a todos los usuarios (opcional)",
        example="550e8400-e29b-41d4-a716-446655440000",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "usuarios": [
                        {
                            "username": "jperez",
                            "nombre": "Juan",
                            "apellido": "Pérez",
                            "password": "password123",
                        },
                        {
                            "username": "mgarcia",
                            "nombre": "María",
                            "apellido": "García",
                            "password": "password456",
                        },
                    ],
                    "id_clase": "550e8400-e29b-41d4-a716-446655440000",
                }
            ]
        }
    }


class UsuarioBulkResponse(BaseModel):
    """Respuesta de creación masiva de usuarios.

    Modelo de respuesta tras operación de creación masiva. Incluye usuarios
    creados exitosamente y posibles errores encontrados.

    Attributes:
        usuarios_creados: Lista de usuarios creados exitosamente.
        total: Número total de usuarios creados.
        errores: Lista de mensajes de error encontrados durante la operación.
    """

    usuarios_creados: list[UsuarioResponse] = Field(
        ...,
        description="Lista de usuarios creados exitosamente",
    )
    total: int = Field(
        ...,
        description="Número total de usuarios creados",
        example=10,
    )
    errores: list[str] = Field(
        default=[],
        description="Lista de errores encontrados durante la operación",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "usuarios_creados": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "username": "jperez",
                            "nombre": "Juan",
                            "apellido": "Pérez",
                            "id_clase": "550e8400-e29b-41d4-a716-446655440000",
                            "creation": "2024-01-15T10:30:00",
                            "top_score": 0,
                        }
                    ],
                    "total": 1,
                    "errores": [],
                }
            ]
        }
    }


# ============================================
# Schemas para Perfil y Progreso Detallado (App Móvil)
# ============================================


class ActividadDetalle(BaseModel):
    """Detalle de una actividad individual con su estado de progreso.

    Attributes:
        id_actividad: ID único de la actividad (UUID).
        nombre_actividad: Nombre descriptivo de la actividad.
        estado: Estado (no_iniciada, en_progreso, completada).
        puntuacion: Puntuación obtenida (solo si completada).
        fecha_completado: Fecha de completado (solo si completada).
        duracion_segundos: Duración en segundos (solo si completada).
    """

    id_actividad: str = Field(..., description="ID único de la actividad")
    nombre_actividad: str = Field(..., description="Nombre de la actividad")
    estado: str = Field(..., description="Estado: no_iniciada, en_progreso, completada")
    puntuacion: float | None = Field(None, description="Puntuación obtenida")
    fecha_completado: datetime | None = Field(None, description="Fecha de completado")
    duracion_segundos: int | None = Field(None, description="Duración en segundos")

    model_config = {"from_attributes": True}


class PuntoProgreso(BaseModel):
    """Progreso de un punto/módulo educativo con todas sus actividades.

    Attributes:
        id_punto: ID único del punto (UUID).
        nombre_punto: Nombre descriptivo del punto.
        total_actividades: Número total de actividades en este punto.
        actividades_completadas: Número de actividades completadas.
        porcentaje_completado: Porcentaje de progreso (0-100).
        puntos_obtenidos: Puntos totales obtenidos en este punto.
        estado: Estado del punto (no_iniciado, en_progreso, completado).
        actividades: Lista detallada de todas las actividades del punto.
    """

    id_punto: str = Field(..., description="ID único del punto")
    nombre_punto: str = Field(..., description="Nombre del punto")
    total_actividades: int = Field(..., description="Total de actividades")
    actividades_completadas: int = Field(..., description="Actividades completadas")
    porcentaje_completado: float = Field(..., description="Porcentaje (0-100)")
    puntos_obtenidos: float = Field(..., description="Puntos obtenidos en este punto")
    estado: str = Field(..., description="Estado: no_iniciado, en_progreso, completado")
    actividades: list[ActividadDetalle] = Field(..., description="Lista de actividades")

    model_config = {"from_attributes": True}


class EstadisticasGenerales(BaseModel):
    """Estadísticas generales del progreso del usuario.

    Attributes:
        total_actividades_disponibles: Actividades totales en el sistema.
        actividades_completadas: Actividades completadas por el usuario.
        porcentaje_progreso_global: Porcentaje de progreso global (0-100).
        total_puntos_acumulados: Suma de todos los puntos obtenidos.
        racha_dias: Días consecutivos de juego.
        ultima_partida: Fecha de la última partida jugada.
        puntos_completados: Número de puntos/módulos completados al 100%.
        total_puntos_disponibles: Total de puntos/módulos en el sistema.
    """

    total_actividades_disponibles: int = Field(
        ..., description="Total de actividades en el sistema"
    )
    actividades_completadas: int = Field(..., description="Actividades completadas por el usuario")
    porcentaje_progreso_global: float = Field(
        ..., description="Porcentaje de progreso global (0-100)"
    )
    total_puntos_acumulados: float = Field(..., description="Suma de todos los puntos obtenidos")
    racha_dias: int = Field(..., description="Días consecutivos de juego")
    ultima_partida: datetime | None = Field(None, description="Fecha de la última partida")
    puntos_completados: int = Field(..., description="Número de puntos/módulos completados al 100%")
    total_puntos_disponibles: int = Field(..., description="Total de puntos/módulos en el sistema")


class PerfilProgreso(BaseModel):
    """Respuesta completa con perfil y progreso detallado del usuario para app móvil.

    Incluye información del perfil, estadísticas generales y progreso detallado
    de todas las actividades organizadas por punto/módulo.

    Attributes:
        usuario: Información básica del usuario.
        estadisticas: Estadísticas generales de progreso.
        puntos: Progreso detallado de cada punto/módulo.
    """

    usuario: UsuarioResponse = Field(..., description="Información del usuario")
    estadisticas: EstadisticasGenerales = Field(..., description="Estadísticas generales")
    puntos: list[PuntoProgreso] = Field(..., description="Progreso detallado por punto")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "usuario": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "usuario123",
                        "nombre": "Juan",
                        "apellido": "Pérez",
                        "id_clase": None,
                        "creation": "2024-01-15T10:30:00",
                        "top_score": 1000,
                    },
                    "estadisticas": {
                        "total_actividades_disponibles": 25,
                        "actividades_completadas": 15,
                        "porcentaje_progreso_global": 60.0,
                        "total_puntos_acumulados": 1850.5,
                        "racha_dias": 5,
                        "ultima_partida": "2024-01-20T15:30:00",
                        "puntos_completados": 2,
                        "total_puntos_disponibles": 5,
                    },
                    "puntos": [
                        {
                            "id_punto": "550e8400-e29b-41d4-a716-446655440002",
                            "nombre_punto": "Árbol del Gernika",
                            "total_actividades": 5,
                            "actividades_completadas": 5,
                            "porcentaje_completado": 100.0,
                            "puntos_obtenidos": 475.5,
                            "estado": "completado",
                            "actividades": [
                                {
                                    "id_actividad": "550e8400-e29b-41d4-a716-446655440001",
                                    "nombre_actividad": "Quiz del Árbol",
                                    "estado": "completada",
                                    "puntuacion": 95.5,
                                    "fecha_completado": "2024-01-20T15:30:00",
                                    "duracion_segundos": 120,
                                }
                            ],
                        }
                    ],
                }
            ]
        }
    }
