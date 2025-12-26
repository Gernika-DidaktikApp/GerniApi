from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth
from app.logging import logger, LoggingMiddleware

app = FastAPI(title=settings.PROJECT_NAME)

# Configurar logging al inicio de la aplicación
logger.info("Iniciando GernikApp API", extra={"extra_fields": {"version": "1.0.0"}})

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
logger.info(f"Router de autenticación registrado en {settings.API_V1_PREFIX}")


@app.on_event("startup")
async def startup_event():
    """Evento ejecutado al iniciar la aplicación"""
    logger.info("Aplicación iniciada correctamente")


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
