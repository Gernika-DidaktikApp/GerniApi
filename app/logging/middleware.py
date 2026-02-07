"""
Middleware para logging de peticiones HTTP
Registra todas las peticiones y respuestas con métricas de rendimiento
"""

import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .logger import log_with_context, logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que registra automáticamente todas las peticiones HTTP
    Incluye información sobre método, path, duración, código de estado, etc.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Timestamp de inicio para calcular duración
        start_time = time.time()

        # Extraer información de la petición de forma segura
        try:
            method = request.method
            path = str(request.url.path) if hasattr(request.url, "path") else "unknown"
            client_host = (
                request.client.host
                if (hasattr(request, "client") and request.client)
                else "unknown"
            )
            user_agent = (
                request.headers.get("user-agent", "unknown")
                if hasattr(request, "headers")
                else "unknown"
            )
            query_params = str(request.query_params) if hasattr(request, "query_params") else ""
        except Exception as e:
            # Si falla la extracción de información, usar valores por defecto
            method = "UNKNOWN"
            path = "unknown"
            client_host = "unknown"
            user_agent = "unknown"
            query_params = ""
            logger.warning(f"Error extrayendo información de request: {e}")

        # Log de petición entrante (nivel DEBUG)
        try:
            logger.debug(
                f"Petición entrante: {method} {path}",
                extra={
                    "extra_fields": {
                        "http_method": method,
                        "path": path,
                        "client_ip": client_host,
                        "user_agent": user_agent,
                        "query_params": query_params,
                    }
                },
            )
        except Exception as e:
            # Si falla el logging, no detener la petición
            logger.warning(f"Error logging petición entrante: {e}")

        # Procesar la petición y capturar posibles errores
        try:
            response = await call_next(request)

            # Calcular duración de la petición
            duration = time.time() - start_time
            duration_ms = round(duration * 1000, 2)

            # Determinar nivel de log según código de estado
            status_code = response.status_code
            if status_code >= 500:
                log_level = "error"
            elif status_code >= 400:
                log_level = "warning"
            else:
                log_level = "info"

            # Log de respuesta
            log_with_context(
                log_level,
                f"{method} {path} - {status_code} - {duration_ms}ms",
                http_method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
                client_ip=client_host,
            )

            return response

        except Exception as e:
            # Calcular duración incluso en caso de error
            duration = time.time() - start_time
            duration_ms = round(duration * 1000, 2)

            # Log de error
            logger.error(
                f"Error procesando petición: {method} {path}",
                exc_info=True,
                extra={
                    "extra_fields": {
                        "http_method": method,
                        "path": path,
                        "client_ip": client_host,
                        "duration_ms": duration_ms,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    }
                },
            )

            # Re-lanzar la excepción para que FastAPI la maneje
            raise
