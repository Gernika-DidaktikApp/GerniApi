"""
Manejadores de excepciones globales con logging estructurado
Captura y registra todos los errores de la aplicación
"""

import traceback

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .logger import log_with_context, logger


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Manejador para excepciones HTTP (404, 401, 403, etc.)
    """
    # Determinar nivel de log según código de estado
    if exc.status_code >= 500:
        log_level = "error"
    elif exc.status_code >= 400:
        log_level = "warning"
    else:
        log_level = "info"

    log_with_context(
        log_level,
        f"HTTP Exception: {exc.status_code}",
        status_code=exc.status_code,
        detail=exc.detail,
        path=str(request.url.path),
        method=request.method,
        client_ip=request.client.host if request.client else "unknown",
        headers=dict(request.headers) if log_level == "error" else None,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error",
            },
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Manejador para errores de validación de Pydantic
    Registra los campos que fallaron la validación
    """
    # Extraer errores de validación
    errors = []
    for error in exc.errors():
        error_detail = {
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        # Añadir input si está disponible para debugging
        if "input" in error:
            error_detail["input_received"] = str(error["input"])[:100]  # Limitar longitud
        errors.append(error_detail)

    # Intentar obtener el body para logging
    try:
        body = await request.body()
        body_preview = body.decode("utf-8")[:200] if body else "empty"
    except Exception:
        body_preview = "unable_to_read"

    log_with_context(
        "warning",
        "Error de validación en request",
        path=str(request.url.path),
        method=request.method,
        client_ip=request.client.host if request.client else "unknown",
        validation_errors=str(errors),
        error_count=len(errors),
        body_preview=body_preview,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": 422,
                "message": "Error de validación en los datos enviados",
                "type": "validation_error",
                "details": errors,
            },
        },
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Manejador para errores de base de datos SQLAlchemy
    """
    error_message = str(exc)

    # Detectar tipo específico de error
    if isinstance(exc, IntegrityError):
        error_type = "integrity_error"
        user_message = (
            "Error de integridad en la base de datos. Posible duplicado o violación de restricción."
        )
        status_code = status.HTTP_409_CONFLICT
    else:
        error_type = "database_error"
        user_message = "Error interno de base de datos"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    logger.error(
        f"Error de base de datos: {error_type}",
        exc_info=True,
        extra={
            "extra_fields": {
                "path": str(request.url.path),
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown",
                "error_type": error_type,
                "error_detail": error_message[:500],  # Limitar longitud
                "traceback": traceback.format_exc(),
            }
        },
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {"code": status_code, "message": user_message, "type": error_type},
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Manejador genérico para excepciones no controladas
    Captura cualquier error no manejado y lo registra
    """
    # Log completo del error con traceback
    logger.critical(
        f"Excepción no controlada: {type(exc).__name__}",
        exc_info=True,
        extra={
            "extra_fields": {
                "path": str(request.url.path),
                "method": request.method,
                "client_ip": request.client.host if request.client else "unknown",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "traceback": traceback.format_exc(),
                "request_headers": dict(request.headers),
            }
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": "Error interno del servidor",
                "type": "internal_error",
            },
        },
    )


def register_exception_handlers(app):
    """
    Registra todos los manejadores de excepciones en la aplicación FastAPI

    Args:
        app: Instancia de FastAPI
    """
    from fastapi.exceptions import RequestValidationError
    from sqlalchemy.exc import SQLAlchemyError
    from starlette.exceptions import HTTPException as StarletteHTTPException

    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registrados correctamente")
