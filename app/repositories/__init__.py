"""Capa de repositorios para acceso a datos.

Los repositorios abstraen el acceso a la base de datos,
desacoplando la lógica de negocio de SQLAlchemy.

Autor: Gernibide
"""

from .actividad_progreso_repository import ActividadProgresoRepository
from .actividad_repository import ActividadRepository
from .audit_log_repository import AuditLogRepository
from .clase_repository import ClaseRepository
from .partida_repository import PartidaRepository
from .profesor_repository import ProfesorRepository
from .punto_repository import PuntoRepository
from .usuario_repository import UsuarioRepository

__all__ = [
    "UsuarioRepository",
    "ClaseRepository",
    "PartidaRepository",
    "ActividadProgresoRepository",
    "ActividadRepository",
    "PuntoRepository",
    "ProfesorRepository",
    "AuditLogRepository",
]
