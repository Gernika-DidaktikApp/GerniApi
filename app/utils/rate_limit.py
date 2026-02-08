"""Configuración de rate limiting con Redis.

Este módulo proporciona rate limiting basado en IP usando Redis
para proteger la API contra abuso y ataques de fuerza bruta.

Autor: Gernibide
"""

from fastapi import Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis import asyncio as aioredis

from app.config import settings
from app.logging import logger


async def init_rate_limiter():
    """Inicializa el rate limiter con conexión a Redis.

    Configura fastapi-limiter para usar Redis como backend de almacenamiento.
    Usa identificador basado en IP del cliente.

    Raises:
        Exception: Si no se puede conectar a Redis.
    """
    try:
        redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await FastAPILimiter.init(redis)
        logger.info(
            "Rate limiter inicializado correctamente",
            extra={
                "extra_fields": {
                    "redis_url": settings.REDIS_URL.split("@")[-1],  # Ocultar credenciales
                    "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
                }
            },
        )
    except Exception as e:
        logger.error(
            f"Error al inicializar rate limiter: {e}",
            exc_info=True,
            extra={
                "extra_fields": {
                    "redis_url": settings.REDIS_URL.split("@")[-1],
                }
            },
        )
        raise


async def close_rate_limiter():
    """Cierra la conexión del rate limiter con Redis.

    Se ejecuta al apagar la aplicación para liberar recursos.
    """
    try:
        await FastAPILimiter.close()
        logger.info("Rate limiter cerrado correctamente")
    except Exception as e:
        logger.warning(f"Error al cerrar rate limiter: {e}")


def ip_based_identifier(request: Request) -> str:
    """Función para identificar clientes por IP.

    Args:
        request: Request de FastAPI.

    Returns:
        IP del cliente o "unknown" si no se puede obtener.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Tomar la primera IP si hay múltiples (caso de proxies)
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"

    return ip


# Dependencias de rate limiting predefinidas

# Rate limit general (10 req/min por defecto)
rate_limit_default = RateLimiter(
    times=settings.RATE_LIMIT_PER_MINUTE,
    seconds=60,
    identifier=ip_based_identifier,
)

# Rate limit estricto para endpoints sensibles (5 req/min)
rate_limit_strict = RateLimiter(
    times=5,
    seconds=60,
    identifier=ip_based_identifier,
)

# Rate limit permisivo para lectura (60 req/min)
rate_limit_permissive = RateLimiter(
    times=60,
    seconds=60,
    identifier=ip_based_identifier,
)
