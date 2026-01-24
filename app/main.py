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
## 
🎯 API REST para GerniBide

API completa para la gestión de usuarios, clases, profesores, partidas y actividades.

---

🔐 Sistema de Autenticación

Esta API utiliza **dos mecanismos de autenticación**:

🔑 API Key (Acceso Administrativo)
Para backends y operaciones administrativas:
```
X-API-Key: tu-api-key
```
- Acceso completo a todos los endpoints
- Requerida para: crear usuarios, gestionar profesores/clases, eliminar recursos

🎫 Token JWT (Acceso de Usuario)
Para la aplicación móvil:
Authorization: Bearer <token>
1. Obtén un token en `POST /api/v1/auth/login-app`
2. El token expira en 30 minutos
3. Acceso limitado a recursos propios

---

📋 Niveles de Acceso por Endpoint

| Icono | Significado |
|-------|-------------|
| 🔓 | **Público** - Sin autenticación |
| 🔑 | **Solo API Key** - Acceso administrativo |
| 🎫 | **API Key o Token** - Acceso mixto |

Endpoints Públicos 🔓
- `GET /` - Root
- `GET /health` - Health check
- `POST /api/v1/auth/login-app` - Login usuario
- `POST /api/v1/auth/login-profesor` - Login profesor

Solo API Key 🔑
- Profesores: Todo el CRUD
- Clases: Todo el CRUD
- Usuarios: POST, GET lista, DELETE
- Actividades: POST, PUT, DELETE
- Eventos: POST, PUT, DELETE
- Partidas: GET lista, DELETE
- Estados: GET lista, DELETE

API Key o Token 🎫
- Usuarios: GET/{id}, PUT/{id} *(solo su perfil)*
- Partidas: POST, GET/{id}, PUT/{id} *(solo sus partidas)*
- Actividades: GET, GET/{id} *(lectura)*
- Eventos: GET, GET/{id} *(lectura)*
- Estados: POST, GET/{id}, PUT/{id} *(via su partida)*

---

📚 Características

- ✅ Autenticación dual (API Key + JWT)
- ✅ Control de acceso por recurso
- ✅ Hash de contraseñas con bcrypt
- ✅ Validación automática de datos
- ✅ Paginación en listados
- ✅ Logging estructurado
- ✅ Base de datos PostgreSQL
    """,
    version="1.1.0",
    contact={"name": "Equipo GerniBide"},
    license_info={
        "name": "Uso privado",
    },
    openapi_tags=[
        {
            "name": "🔐 Autenticación",
            "description": "🔓 **Público** - Endpoints para login y gestión de tokens JWT",
        },
        {
            "name": "👥 Usuarios",
            "description": "🔑🎫 **Mixto** - POST/GET lista/DELETE requieren API Key. GET/{id}/PUT/{id} permiten Token (solo perfil propio)",
        },
        {
            "name": "👨‍🏫 Profesores",
            "description": "🔑 **Solo API Key** - Gestión completa de profesores",
        },
        {
            "name": "🏫 Clases",
            "description": "🔑 **Solo API Key** - Gestión de clases y asignaciones",
        },
        {
            "name": "🎮 Partidas",
            "description": "🔑🎫 **Mixto** - GET lista/DELETE requieren API Key. POST/GET/{id}/PUT/{id} permiten Token (solo sus partidas)",
        },
        {
            "name": "📝 Actividades",
            "description": "🔑🎫 **Mixto** - POST/PUT/DELETE requieren API Key. GET permite Token (lectura pública)",
        },
        {
            "name": "📅 Eventos",
            "description": "🔑🎫 **Mixto** - POST/PUT/DELETE requieren API Key. GET permite Token (lectura pública)",
        },
        {
            "name": "📊 Estados",
            "description": "🔑🎫 **Mixto** - GET lista/DELETE requieren API Key. Resto permite Token (via su partida)",
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
app.include_router(actividades.router, prefix=settings.API_V1_PREFIX)
app.include_router(eventos.router, prefix=settings.API_V1_PREFIX)
app.include_router(partidas.router, prefix=settings.API_V1_PREFIX)
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
