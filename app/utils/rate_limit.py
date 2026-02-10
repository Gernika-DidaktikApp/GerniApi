"""Configuración de rate limiting con slowapi.

Este módulo proporciona rate limiting basado en IP usando Redis
para proteger la API contra abuso y ataques de fuerza bruta.

En producción usa Redis para almacenamiento distribuido.
En desarrollo o si Redis no está disponible, usa memoria local.

Autor: Gernibide
"""

import os

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address as slowapi_get_remote_address

from app.config import settings
from app.logging import logger


def get_remote_address(request: Request) -> str:
    """Obtiene la IP real del cliente, considerando proxies.

    En producción, Railway/Cloudflare ponen la IP real en X-Forwarded-For.

    Args:
        request: Request de FastAPI.

    Returns:
        IP del cliente.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return slowapi_get_remote_address(request)


def get_storage_uri() -> str:
    """Determina el storage URI para rate limiting.

    Prioridad:
    1. Variable de entorno REDIS_URL (Railway, producción)
    2. Redis local en desarrollo
    3. Fallback a memoria si Redis no está disponible

    Returns:
        URI de storage para slowapi.
    """
    # 1. Intentar usar REDIS_URL de entorno (producción)
    redis_url = settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else os.getenv("REDIS_URL")
    if redis_url:
        logger.info(f"Rate limiting usando Redis: {redis_url.split('@')[0] if '@' in redis_url else 'redis'}@***")
        return redis_url

    # 2. Intentar conectar a Redis local (desarrollo)
    try:
        import redis
        client = redis.Redis(host="localhost", port=6379, db=0, socket_connect_timeout=1)
        client.ping()
        logger.info("Rate limiting usando Redis local: redis://localhost:6379")
        return "redis://localhost:6379"
    except Exception:
        pass

    # 3. Fallback a memoria
    logger.warning("Redis no disponible, usando memoria para rate limiting")
    return "memory://"


# Inicializar limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri=get_storage_uri(),
)


# ==================== Límites por categoría ====================

# Rate limit por defecto (configurable desde settings)
RATE_LIMIT_DEFAULT = f"{settings.RATE_LIMIT_PER_MINUTE if hasattr(settings, 'RATE_LIMIT_PER_MINUTE') else 10}/minute"

# Rate limit estricto para endpoints sensibles
RATE_LIMIT_STRICT = "5/minute"

# Rate limit permisivo para lectura
RATE_LIMIT_PERMISSIVE = "60/minute"


# ==================== Error Handler ====================

def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Handler personalizado para errores de rate limiting.

    Args:
        request: Request que excedió el límite.
        exc: Excepción de RateLimitExceeded.

    Returns:
        JSONResponse con mensaje de error.
    """
    limit_info = str(exc.detail)

    # Calcular retry_after
    retry_after = 60
    if "minute" in limit_info:
        retry_after = 60
    elif "hour" in limit_info:
        retry_after = 3600

    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": f"Has excedido el límite de solicitudes ({limit_info}). Espera antes de intentar nuevamente.",
            "limit": limit_info,
            "retry_after_seconds": retry_after,
        },
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": limit_info,
        },
    )


# Funciones de compatibilidad (no-op para slowapi)
async def init_rate_limiter():
    """Inicializa el rate limiter.

    Con slowapi, la inicialización es automática al crear el limiter.
    Esta función se mantiene por compatibilidad.
    """
    logger.info("Rate limiter inicializado con slowapi")


async def close_rate_limiter():
    """Cierra el rate limiter.

    Con slowapi, no requiere cierre explícito.
    Esta función se mantiene por compatibilidad.
    """
    logger.info("Rate limiter cerrado")
