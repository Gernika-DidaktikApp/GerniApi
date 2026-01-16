from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import (
    auth,
    usuarios,
    profesores,
    clases,
    actividades,
    eventos,
    partidas,
    actividad_estados,
    evento_estados,
)
from app.logging import logger, LoggingMiddleware, register_exception_handlers
from app.database import Base, engine
# Importar modelos para que SQLAlchemy los conozca
import app.models  # noqa

app = FastAPI(title=settings.PROJECT_NAME)

# Configurar logging al inicio de la aplicación
logger.info("Iniciando GernikApp API", extra={"extra_fields": {"version": "1.0.0"}})

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

# Incluir routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(usuarios.router, prefix=settings.API_V1_PREFIX)
app.include_router(profesores.router, prefix=settings.API_V1_PREFIX)
app.include_router(clases.router, prefix=settings.API_V1_PREFIX)
app.include_router(actividades.router, prefix=settings.API_V1_PREFIX)
app.include_router(eventos.router, prefix=settings.API_V1_PREFIX)
app.include_router(partidas.router, prefix=settings.API_V1_PREFIX)
app.include_router(actividad_estados.router, prefix=settings.API_V1_PREFIX)
app.include_router(evento_estados.router, prefix=settings.API_V1_PREFIX)
logger.info(f"Routers registrados en {settings.API_V1_PREFIX}")


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
    return {"message": "GernikApp API - Funcionando correctamente"}


@app.get("/health")
def health_check():
    logger.debug("Health check realizado")
    return {"status": "healthy"}
