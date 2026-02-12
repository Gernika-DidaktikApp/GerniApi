"""Aplicación principal FastAPI para GerniBide.

Este módulo configura y ejecuta la aplicación FastAPI principal,
incluyendo la configuración de middlewares, CORS, archivos estáticos
y todos los routers de la API.

Autor: Gernibide
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

# Importar modelos para que SQLAlchemy los conozca
import app.models  # noqa
from app.config import settings
from app.database import Base, engine
from app.logging import LoggingMiddleware, logger, register_exception_handlers
from app.routers import (
    actividad_progreso,
    actividades,
    audit_logs,
    auth,
    clases,
    gameplay_statistics,
    i18n,
    learning_statistics,
    partidas,
    profesores,
    puntos,
    statistics,
    teacher_dashboard,
    usuarios,
)
from app.utils.rate_limit import close_rate_limiter, init_rate_limiter, limiter, rate_limit_handler
from app.web.flask_app import flask_app

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
## API REST para GerniBide

API completa para la gestión de usuarios, clases, profesores, partidas y actividades educativas.

---

## Sistema de Autenticación

Esta API utiliza **dos mecanismos de autenticación**:

### [API-KEY] API Key (Acceso Administrativo)
Para backends y operaciones administrativas:
```
X-API-Key: tu-api-key
```
- Acceso completo a todos los endpoints
- Requerida para: crear usuarios masivos, gestionar profesores/clases, eliminar recursos

### [JWT] Token JWT (Acceso de Usuario/Profesor)
Para la aplicación móvil y web:
```
Authorization: Bearer <token>
```
1. Obtén un token en `POST /api/v1/auth/login-app` (usuarios) o `POST /api/v1/auth/login-profesor` (profesores)
2. El token expira en 30 minutos
3. Acceso limitado a recursos propios

---

## Endpoints por Categoría

### [PUBLIC] Autenticación (sin auth requerida)
- `GET /` - Verificar que la API está funcionando
- `GET /health` - Health check
- `POST /api/v1/auth/login-app` - Login de usuario (estudiante)
- `POST /api/v1/auth/login-profesor` - Login de profesor

### [API-KEY] Solo Administración
- **Profesores**: CRUD completo
- **Clases**: CRUD completo, creación con código compartible (6 chars)
- **Usuarios**: Importación masiva (bulk), eliminación
- **Actividades**: POST, PUT, DELETE
- **Puntos**: POST, PUT, DELETE
- **Partidas**: GET lista, DELETE
- **Progreso**: GET lista, DELETE

### [MIXED] API Key o Token JWT
- **Usuarios**:
  - `GET /{id}` - Ver perfil (solo propio con token)
  - `PUT /{id}` - Actualizar perfil (solo propio con token)
  - `GET /{id}/estadisticas` - Estadísticas de usuario
- **Partidas**:
  - `POST` - Crear partida (con token)
  - `GET /{id}`, `PUT /{id}` - Solo sus propias partidas con token
- **Actividades**:
  - `GET`, `GET /{id}` - Lectura pública con token
  - `GET /{id}/respuestas-publicas` - Ver respuestas públicas (mensaje wall)
- **Puntos**: `GET`, `GET /{id}` - Lectura pública con token
- **Progreso**: POST, GET/{id}, PUT/{id} - Vía su partida con token
- **Estadísticas**: Endpoints de estadísticas de juego y aprendizaje
- **Audit Logs**: GET con token, POST con API Key

---

## Características

✅ Autenticación dual (API Key + JWT)
✅ Control de acceso por recurso
✅ Hash de contraseñas con bcrypt
✅ Validación automática de datos con Pydantic
✅ Paginación en listados
✅ Logging estructurado con contexto
✅ Códigos de clase compartibles (6 caracteres)
✅ Importación masiva de usuarios (transaccional)
✅ Sistema de trazabilidad con audit logs
✅ Internacionalización (i18n) español/euskera
    """,
    version="1.2.0",
    contact={"name": "Equipo GerniBide"},
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "🔐 Autenticación",
            "description": "[PUBLIC] Login de usuarios y profesores. Genera tokens JWT válidos por 30 minutos.",
        },
        {
            "name": "👥 Usuarios",
            "description": "[MIXED] Gestión de usuarios estudiantes. Incluye importación masiva (bulk), registro con código de clase, estadísticas y perfil.",
        },
        {
            "name": "👨‍🏫 Profesores",
            "description": "[API-KEY] CRUD completo de profesores. Solo administración.",
        },
        {
            "name": "🏫 Clases",
            "description": "[API-KEY] Gestión de clases con códigos compartibles (6 caracteres). Solo administración.",
        },
        {
            "name": "🎮 Partidas",
            "description": "[MIXED] Partidas de juego. Estudiantes crean sus propias partidas con token JWT.",
        },
        {
            "name": "📍 Puntos",
            "description": "[MIXED] Puntos del mapa educativo. Lectura pública con token, modificación solo con API Key.",
        },
        {
            "name": "📝 Actividades",
            "description": "[MIXED] Actividades educativas. Incluye endpoint de respuestas públicas para muro de mensajes.",
        },
        {
            "name": "📊 Progreso",
            "description": "[MIXED] Progreso de actividades de estudiantes. Gestión vía partida con token JWT.",
        },
        {
            "name": "📈 Estadísticas",
            "description": "[MIXED] Estadísticas de juego y aprendizaje. Acceso con token JWT.",
        },
        {
            "name": "🔍 Audit Logs",
            "description": "[MIXED] Trazabilidad de acciones. Sistema polimórfico (Web/App logs).",
        },
    ],
)

# Configurar logging al inicio de la aplicación
logger.info("Iniciando GerniBide API", extra={"extra_fields": {"version": "1.0.0"}})

# Registrar manejadores de excepciones globales
register_exception_handlers(app)

# Registrar slowapi state y error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Configurar middleware de logging (debe ir ANTES de otros middlewares)
app.add_middleware(LoggingMiddleware)

# Configurar CORS para permitir peticiones desde la app móvil
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Configurable desde .env (CORS_ORIGINS)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos para la interfaz web
STATIC_DIR = Path(__file__).parent / "web" / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
logger.info(f"Archivos estáticos montados en /static desde {STATIC_DIR}")

# Incluir routers de API - Todos bajo /api/v1/ para versionado consistente
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(usuarios.router, prefix=settings.API_V1_PREFIX)
app.include_router(profesores.router, prefix=settings.API_V1_PREFIX)
app.include_router(clases.router, prefix=settings.API_V1_PREFIX)
app.include_router(puntos.router, prefix=settings.API_V1_PREFIX)
app.include_router(actividades.router, prefix=settings.API_V1_PREFIX)
app.include_router(partidas.router, prefix=settings.API_V1_PREFIX)
app.include_router(actividad_progreso.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_logs.router, prefix=settings.API_V1_PREFIX)
app.include_router(statistics.router)  # Includes /api/v1/statistics prefix internally
app.include_router(
    gameplay_statistics.router
)  # Includes /api/v1/statistics/gameplay prefix internally
app.include_router(
    learning_statistics.router
)  # Includes /api/v1/statistics/learning prefix internally
app.include_router(teacher_dashboard.router)  # Includes /api/v1/teacher/dashboard prefix internally
app.include_router(i18n.router)  # Includes /api/v1/i18n prefix internally
logger.info(f"Routers de API registrados en {settings.API_V1_PREFIX}")

# Incluir router de interfaz web FastAPI (DESACTIVADO - ahora usa Flask)
# app.include_router(web_routes.router)
# logger.info("Router de interfaz web FastAPI registrado")

# Montar aplicación Flask para servir interfaz web (requisito académico)
# Flask maneja: /, /login, /dashboard, /statistics, /gallery, etc.
# FastAPI maneja: /api/v1/*, /health
app.mount("/", WSGIMiddleware(flask_app))
logger.info("Aplicación Flask montada en raíz para interfaz web")


@app.on_event("startup")
async def startup_event():
    """Evento ejecutado al iniciar la aplicación.

    Crea las tablas en la base de datos si no existen, inicializa
    el rate limiter con Redis y registra el inicio en los logs.

    Raises:
        Exception: Si hay un error al crear las tablas (no detiene la app).
    """
    try:
        # Crear todas las tablas si no existen
        logger.info("Creando tablas en la base de datos si no existen...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas creadas/verificadas exitosamente")

        # Inicializar rate limiter si está habilitado
        if settings.RATE_LIMIT_ENABLED:
            try:
                await init_rate_limiter()
            except Exception as e:
                logger.warning(
                    f"Rate limiter no pudo inicializarse: {e}. Continuando sin rate limiting."
                )

        logger.info("Aplicación iniciada correctamente")
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {e}", exc_info=True)
        # No re-raise para que la app al menos arranque (sin BD)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento ejecutado al detener la aplicación.

    Cierra la conexión del rate limiter y registra el cierre en los logs.
    """
    if settings.RATE_LIMIT_ENABLED:
        try:
            await close_rate_limiter()
        except Exception as e:
            logger.warning(f"Error al cerrar rate limiter: {e}")

    logger.info("Aplicación detenida")


# Endpoint raíz ahora manejado por Flask
# @app.get("/")
# def root():
#     """Endpoint raíz de la API.
#
#     Returns:
#         dict: Mensaje indicando que la API está funcionando correctamente.
#     """
#     logger.debug("Endpoint raíz accedido")
#     return {"message": "GerniBide API - Funcionando correctamente"}


@app.get("/health")
def health_check():
    """Endpoint de verificación de salud de la API.

    Returns:
        dict: Estado de salud de la aplicación.
    """
    logger.debug("Health check realizado")
    return {"status": "healthy"}
