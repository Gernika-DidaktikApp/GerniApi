from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Importar modelos para que SQLAlchemy los conozca
import app.models  # noqa
from app.config import settings
from app.database import Base, engine
from app.logging import LoggingMiddleware, logger, register_exception_handlers
from app.routers import (
    actividad_estados,
    actividades,
    auth,
    clases,
    evento_estados,
    eventos,
    partidas,
    profesores,
    usuarios,
)
from app.web import routes as web_routes

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## 🎯 API REST para GerniBide

    API completa para la gestión de usuarios, clases, profesores, partidas y actividades.

    ### 🔐 Autenticación

    Esta API utiliza **JWT (JSON Web Tokens)** para autenticación:

    1. **Login**: Obtén un token en `/api/v1/auth/login-app`
    2. **Usar token**: Incluye el header `Authorization: Bearer <token>` en tus peticiones
    3. **Expiración**: Los tokens expiran en 30 minutos

    ### 📚 Características

    - ✅ Autenticación JWT segura
    - ✅ Hash de contraseñas con bcrypt
    - ✅ Validación automática de datos
    - ✅ Paginación en listados
    - ✅ Logging estructurado
    - ✅ Base de datos PostgreSQL

    ### 🔗 Enlaces Útiles

    - [Documentación completa](https://github.com/tu-repo)
    - [Colección de Postman](./GerniBide.postman_collection.json)
    - [Guía de integración](./API_ENDPOINTS.md)

    ### 📧 Soporte

    ¿Necesitas ayuda? Revisa los logs o contacta al equipo de desarrollo.
    """,
    version="1.0.0",
    contact={"name": "Equipo GerniBide", "email": "soporte@GerniBide.com"},
    license_info={
        "name": "Uso privado",
    },
    openapi_tags=[
        {
            "name": "🔐 Autenticación",
            "description": "Endpoints para login y gestión de tokens JWT",
        },
        {"name": "👥 Usuarios", "description": "CRUD completo de usuarios del sistema"},
        {"name": "👨‍🏫 Profesores", "description": "Gestión de profesores"},
        {"name": "🏫 Clases", "description": "Gestión de clases y asignaciones"},
        {"name": "🎮 Partidas", "description": "Gestión de partidas de juego"},
        {
            "name": "📝 Actividades",
            "description": "Gestión de actividades dentro de partidas",
        },
        {"name": "📅 Eventos", "description": "Gestión de eventos de actividades"},
        {"name": "📊 Estados", "description": "Estados de actividades y eventos"},
    ],
)

# Configurar logging al inicio de la aplicación
logger.info("Iniciando GerniBide API", extra={"extra_fields": {"version": "1.0.0"}})

# Registrar manejadores de excepciones globales
register_exception_handlers(app)

# Configurar middleware de logging (debe ir ANTES de otros middlewares)
app.add_middleware(LoggingMiddleware)

# Configurar CORS para permitir peticiones desde la app móvil
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos para la interfaz web
STATIC_DIR = Path(__file__).parent / "web" / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
logger.info(f"Archivos estáticos montados en /static desde {STATIC_DIR}")

# Incluir routers de API
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(usuarios.router, prefix=settings.API_V1_PREFIX)
app.include_router(profesores.router, prefix=settings.API_V1_PREFIX)
app.include_router(clases.router, prefix=settings.API_V1_PREFIX)
app.include_router(actividades.router, prefix=settings.API_V1_PREFIX)
app.include_router(eventos.router, prefix=settings.API_V1_PREFIX)
app.include_router(partidas.router, prefix=settings.API_V1_PREFIX)
app.include_router(actividad_estados.router, prefix=settings.API_V1_PREFIX)
app.include_router(evento_estados.router, prefix=settings.API_V1_PREFIX)
logger.info(f"Routers de API registrados en {settings.API_V1_PREFIX}")

# Incluir router de interfaz web
app.include_router(web_routes.router)
logger.info("Router de interfaz web registrado")


@app.on_event("startup")
async def startup_event():
    """Evento ejecutado al iniciar la aplicación"""
    try:
        # Crear todas las tablas si no existen
        logger.info("Creando tablas en la base de datos si no existen...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas creadas/verificadas exitosamente")
        logger.info("Aplicación iniciada correctamente")
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {e}", exc_info=True)
        # No re-raise para que la app al menos arranque (sin BD)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento ejecutado al detener la aplicación"""
    logger.info("Aplicación detenida")


@app.get("/")
def root():
    logger.debug("Endpoint raíz accedido")
    return {"message": "GerniBide API - Funcionando correctamente"}


@app.get("/health")
def health_check():
    logger.debug("Health check realizado")
    return {"status": "healthy"}
