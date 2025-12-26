"""
Módulo de configuración de logging estructurado
Proporciona logging con rotación de archivos y diferentes niveles
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """
    Formateador personalizado que genera logs en formato JSON estructurado
    Facilita el análisis y parsing de logs
    """

    def format(self, record: logging.LogRecord) -> str:
        # Crear estructura base del log
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Añadir información de excepción si existe
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Añadir campos extra si existen
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Convertir a JSON
        return json.dumps(log_data, ensure_ascii=False)


class SimpleFormatter(logging.Formatter):
    """
    Formateador simple para consola
    Más legible para desarrollo
    """

    # Colores ANSI para diferentes niveles
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        # Añadir color al nivel de log
        levelname = record.levelname
        if levelname in self.COLORS:
            colored_levelname = f"{self.COLORS[levelname]}{levelname:8}{self.RESET}"
            record.levelname = colored_levelname

        # Formato: [TIMESTAMP] [LEVEL] [module:line] - message
        log_format = "[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] - %(message)s"
        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

        return formatter.format(record)


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

    # Crear directorio de logs si no existe
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Obtener o crear el logger principal
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)  # Nivel más bajo para capturar todo

    # Limpiar handlers existentes para evitar duplicados
    logger.handlers.clear()

    # ====================================
    # Handler 1: Consola (salida estándar)
    # ====================================
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, console_level.upper()))
    console_handler.setFormatter(SimpleFormatter())
    logger.addHandler(console_handler)

    # ====================================
    # Handler 2: Archivo principal (app.log)
    # Logs de nivel INFO y superior
    # ====================================
    app_log_file = log_path / "app.log"
    app_file_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    app_file_handler.setLevel(getattr(logging, file_level.upper()))
    app_file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(app_file_handler)

    # ====================================
    # Handler 3: Archivo de debug (debug.log)
    # Todos los logs incluyendo DEBUG
    # ====================================
    debug_log_file = log_path / "debug.log"
    debug_file_handler = RotatingFileHandler(
        debug_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    debug_file_handler.setLevel(getattr(logging, debug_level.upper()))
    debug_file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(debug_file_handler)

    # ====================================
    # Handler 4: Archivo de errores (error.log)
    # Solo errores y críticos
    # ====================================
    error_log_file = log_path / "error.log"
    error_file_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(StructuredFormatter())
    logger.addHandler(error_file_handler)

    # Evitar que los logs se propaguen al logger raíz
    logger.propagate = False

    # Log inicial para confirmar que el sistema está funcionando
    logger.info(
        f"Sistema de logging inicializado",
        extra={"extra_fields": {
            "log_dir": str(log_path),
            "max_file_size": f"{max_bytes / 1024 / 1024}MB",
            "backup_count": backup_count
        }}
    )

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
