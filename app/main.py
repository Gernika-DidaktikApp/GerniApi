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
    actividad_progreso,
    actividades,
    audit_logs,
    auth,
    clases,
    gameplay_statistics,
    learning_statistics,
    partidas,
    profesores,
    puntos,
    statistics,
    teacher_dashboard,
    usuarios,
)
from app.web import routes as web_routes

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
##
API REST para GerniBide

API completa para la gestión de usuarios, clases, profesores, partidas y actividades.

---

[AUTH] Sistema de Autenticación

Esta API utiliza **dos mecanismos de autenticación**:

[API-KEY] API Key (Acceso Administrativo)
Para backends y operaciones administrativas:
```
X-API-Key: tu-api-key
```
- Acceso completo a todos los endpoints
- Requerida para: crear usuarios, gestionar profesores/clases, eliminar recursos

[JWT] Token JWT (Acceso de Usuario)
Para la aplicación móvil:
Authorization: Bearer <token>
1. Obtén un token en `POST /api/v1/auth/login-app`
2. El token expira en 30 minutos
3. Acceso limitado a recursos propios

---

Niveles de Acceso por Endpoint

| Icono | Significado |
|-------|-------------|
| [PUBLIC] | **Público** - Sin autenticación |
| [API-KEY] | **Solo API Key** - Acceso administrativo |
| [MIXED] | **API Key o Token** - Acceso mixto |

Endpoints Públicos [PUBLIC]
- `GET /` - Root
- `GET /health` - Health check
- `POST /api/v1/auth/login-app` - Login usuario
- `POST /api/v1/auth/login-profesor` - Login profesor

Solo API Key [API-KEY]
- Profesores: Todo el CRUD
- Clases: Todo el CRUD
- Usuarios: POST, GET lista, DELETE
78: - Actividades: POST, PUT, DELETE
79: - Puntos: POST, PUT, DELETE
80: - Partidas: GET lista, DELETE
81: - Estados: GET lista, DELETE
82: 
83: API Key o Token [MIXED]
84: - Usuarios: GET/{id}, PUT/{id} *(solo su perfil)*
85: - Partidas: POST, GET/{id}, PUT/{id} *(solo sus partidas)*
86: - Actividades: GET, GET/{id} *(lectura)*
87: - Puntos: GET, GET/{id} *(lectura)*
88: - Progresos: POST, GET/{id}, PUT/{id} *(via su partida)*

---

Características

- Autenticación dual (API Key + JWT)
- Control de acceso por recurso
- Hash de contraseñas con bcrypt
- Validación automática de datos
- Paginación en listados
- Logging estructurado
- Base de datos PostgreSQL
    """,
    version="1.1.0",
    contact={"name": "Equipo GerniBide"},
    license_info={
        "name": "Uso privado",
    },
    openapi_tags=[
        {
            "name": "Autenticación",
            "description": "[PUBLIC] Endpoints para login y gestión de tokens JWT",
        },
        {
            "name": "Usuarios",
            "description": "[MIXED] POST/GET lista/DELETE requieren API Key. GET/{id}/PUT/{id} permiten Token (solo perfil propio)",
        },
        {
            "name": "Profesores",
            "description": "[API-KEY] Gestión completa de profesores",
        },
        {
            "name": "Clases",
            "description": "[API-KEY] Gestión de clases y asignaciones",
        },
        {
            "name": "Partidas",
            "description": "[MIXED] GET lista/DELETE requieren API Key. POST/GET/{id}/PUT/{id} permiten Token (solo sus partidas)",
        },
        {
            "name": "Puntos",
            "description": "[MIXED] POST/PUT/DELETE requieren API Key. GET permite Token (lectura pública)",
        },
        {
            "name": "Actividades",
            "description": "[MIXED] POST/PUT/DELETE requieren API Key. GET permite Token (lectura pública)",
        },
        {
            "name": "Progreso",
            "description": "[MIXED] GET lista/DELETE requieren API Key. Resto permite Token (via su partida)",
        },
        {
            "name": "Audit Logs",
            "description": "[MIXED] POST requiere API Key. GET permite Token. Sistema de trazabilidad con herencia y polimorfismo (Web/App)",
        },
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
app.include_router(puntos.router, prefix=settings.API_V1_PREFIX)
app.include_router(actividades.router, prefix=settings.API_V1_PREFIX)
app.include_router(partidas.router, prefix=settings.API_V1_PREFIX)
app.include_router(actividad_progreso.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_logs.router, prefix=settings.API_V1_PREFIX)
app.include_router(statistics.router)  # Statistics doesn't use API_V1_PREFIX
app.include_router(gameplay_statistics.router)  # Gameplay statistics doesn't use API_V1_PREFIX
app.include_router(learning_statistics.router)  # Learning statistics doesn't use API_V1_PREFIX
app.include_router(teacher_dashboard.router)  # Teacher dashboard doesn't use API_V1_PREFIX
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
