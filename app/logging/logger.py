"""
Módulo de configuración de logging estructurado
Proporciona logging con rotación de archivos y diferentes niveles
"""

import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """
    Formateador personalizado que genera logs estructurados
    Facilita el análisis de logs sin necesidad de JSON
    """

    def format(self, record: logging.LogRecord) -> str:
        # Formato base del log
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        base = f"[{timestamp}] [{record.levelname:8}] [{record.module}:{record.lineno}] - {record.getMessage()}"

        # Añadir campos extra si existen
        if hasattr(record, "extra_fields") and record.extra_fields:
            extras = []
            for key, value in record.extra_fields.items():
                extras.append(f"{key}={value}")
            if extras:
                base += " | " + " | ".join(extras)

        # Añadir información de excepción si existe
        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)

        return base


class SimpleFormatter(logging.Formatter):
    """
    Formateador simple para consola
    Más legible para desarrollo
    """

    # Colores ANSI para diferentes niveles
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Emojis para cada nivel
    ICONS = {
        "DEBUG": "🔍",
        "INFO": "✓",
        "WARNING": "⚠️ ",
        "ERROR": "✗",
        "CRITICAL": "🔥",
    }

    def format(self, record: logging.LogRecord) -> str:
        # Obtener emoji
        icon = self.ICONS.get(record.levelname, "•")

        # Añadir color al nivel de log
        levelname = record.levelname
        if levelname in self.COLORS:
            colored_level = f"{self.COLORS[levelname]}{self.BOLD}{levelname:8}{self.RESET}"
        else:
            colored_level = f"{levelname:8}"

        # Timestamp con formato más compacto
        timestamp = self.formatTime(record, "%H:%M:%S")

        # Módulo y línea en gris tenue
        location = f"{self.DIM}{record.module}:{record.lineno}{self.RESET}"

        # Mensaje
        message = record.getMessage()

        # Formato final bonito: 🔍 14:23:45 INFO     auth:42 → Usuario autenticado
        return f"{icon} {self.DIM}{timestamp}{self.RESET} {colored_level} {location} → {message}"


def setup_logging(
    app_name: str = "GerniApi",
    log_dir: str = "logs",
    console_level: str = "INFO",
    file_level: str = "INFO",
    debug_level: str = "DEBUG",
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB por archivo
    backup_count: int = 5,  # Mantener 5 archivos de respaldo
) -> logging.Logger:
    """
    Configura el sistema de logging con múltiples handlers

    Args:
        app_name: Nombre de la aplicación para el logger
        log_dir: Directorio donde se guardarán los logs
        console_level: Nivel de log para consola (INFO, DEBUG, WARNING, etc.)
        file_level: Nivel de log para archivo principal
        debug_level: Nivel de log para archivo de debug
        max_bytes: Tamaño máximo de cada archivo de log antes de rotar
        backup_count: Número de archivos de respaldo a mantener

    Returns:
        Logger configurado
    """
    import os

    # Detectar si estamos en Railway o entorno de producción
    is_production = os.getenv("RAILWAY_ENVIRONMENT") is not None or os.getenv("PORT") is not None

    # Obtener o crear el logger principal
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)  # Nivel más bajo para capturar todo

    # Limpiar handlers existentes para evitar duplicados
    logger.handlers.clear()

    # ====================================
    # Handler 1: Consola (salida estándar)
    # SIEMPRE presente (funciona en Railway)
    # ====================================
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, console_level.upper()))
    console_handler.setFormatter(SimpleFormatter())
    logger.addHandler(console_handler)

    # Solo añadir file handlers en desarrollo local
    if not is_production:
        try:
            # Crear directorio de logs si no existe
            log_path = Path(log_dir)
            log_path.mkdir(exist_ok=True)

            # ====================================
            # Handler 2: Archivo principal (app.log)
            # ====================================
            app_log_file = log_path / "app.log"
            app_file_handler = RotatingFileHandler(
                app_log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            app_file_handler.setLevel(getattr(logging, file_level.upper()))
            app_file_handler.setFormatter(StructuredFormatter())
            logger.addHandler(app_file_handler)

            # ====================================
            # Handler 3: Archivo de debug (debug.log)
            # ====================================
            debug_log_file = log_path / "debug.log"
            debug_file_handler = RotatingFileHandler(
                debug_log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            debug_file_handler.setLevel(getattr(logging, debug_level.upper()))
            debug_file_handler.setFormatter(StructuredFormatter())
            logger.addHandler(debug_file_handler)

            # ====================================
            # Handler 4: Archivo de errores (error.log)
            # ====================================
            error_log_file = log_path / "error.log"
            error_file_handler = RotatingFileHandler(
                error_log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            error_file_handler.setLevel(logging.ERROR)
            error_file_handler.setFormatter(StructuredFormatter())
            logger.addHandler(error_file_handler)

            logger.info(
                "Sistema de logging inicializado (desarrollo)",
                extra={
                    "extra_fields": {
                        "log_dir": str(log_path),
                        "max_file_size": f"{max_bytes / 1024 / 1024}MB",
                        "backup_count": backup_count,
                    }
                },
            )
        except Exception as e:
            # Si falla la creación de archivos, solo usar consola
            logger.warning(f"No se pudieron crear archivos de log: {e}. Usando solo consola.")
    else:
        # En producción (Railway), solo consola
        logger.info("Sistema de logging inicializado (producción - solo consola)")

    # Evitar que los logs se propaguen al logger raíz
    logger.propagate = False

    return logger


# Crear una instancia global del logger para usar en toda la aplicación
logger = setup_logging()


def log_with_context(level: str, message: str, **context):
    """
    Función helper para hacer logs con contexto adicional

    Args:
        level: Nivel del log (debug, info, warning, error, critical)
        message: Mensaje del log
        **context: Campos adicionales para añadir al log

    Ejemplo:
        log_with_context("info", "Usuario autenticado", user_id=123, ip="192.168.1.1")
    """
    log_method = getattr(logger, level.lower())
    log_method(message, extra={"extra_fields": context})


def log_debug(message: str, **context):
    """Log de nivel DEBUG con contexto"""
    log_with_context("debug", message, **context)


def log_info(message: str, **context):
    """Log de nivel INFO con contexto"""
    log_with_context("info", message, **context)


def log_warning(message: str, **context):
    """Log de nivel WARNING con contexto"""
    log_with_context("warning", message, **context)


def log_error(message: str, exc_info: bool = False, **context):
    """Log de nivel ERROR con contexto y opcionalmente traceback"""
    if exc_info:
        logger.error(message, exc_info=True, extra={"extra_fields": context})
    else:
        log_with_context("error", message, **context)


def log_critical(message: str, exc_info: bool = True, **context):
    """Log de nivel CRITICAL con contexto y traceback"""
    logger.critical(message, exc_info=exc_info, extra={"extra_fields": context})


def log_request(method: str, path: str, status_code: int, duration_ms: float, **extra):
    """Log específico para peticiones HTTP"""
    level = "error" if status_code >= 500 else "warning" if status_code >= 400 else "info"
    log_with_context(
        level,
        f"{method} {path} - {status_code} ({duration_ms}ms)",
        http_method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        **extra,
    )


def log_db_operation(operation: str, table: str, record_id: str = None, **extra):
    """Log específico para operaciones de base de datos"""
    log_with_context(
        "debug",
        f"DB {operation}: {table}" + (f" (id={record_id})" if record_id else ""),
        db_operation=operation,
        table=table,
        record_id=record_id,
        **extra,
    )


def log_auth(event: str, username: str = None, success: bool = True, **extra):
    """Log específico para eventos de autenticación"""
    level = "info" if success else "warning"
    log_with_context(
        level,
        f"Auth: {event}" + (f" - user={username}" if username else ""),
        auth_event=event,
        username=username,
        success=success,
        **extra,
    )
