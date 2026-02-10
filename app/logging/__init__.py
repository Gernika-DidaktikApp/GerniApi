"""Módulo de logging para GerniApi.

Proporciona logging estructurado con rotación de archivos, middleware
para logging HTTP y manejadores de excepciones globales.

Autor: Gernibide
"""

from .exceptions import register_exception_handlers
from .logger import (
    log_auth,
    log_critical,
    log_db_operation,
    log_debug,
    log_error,
    log_info,
    log_request,
    log_warning,
    log_with_context,
    logger,
    setup_logging,
)
from .middleware import LoggingMiddleware

__all__ = [
    "logger",
    "log_with_context",
    "setup_logging",
    "log_debug",
    "log_info",
    "log_warning",
    "log_error",
    "log_critical",
    "log_request",
    "log_db_operation",
    "log_auth",
    "LoggingMiddleware",
    "register_exception_handlers",
]
