"""Repositorio para operaciones de Partida en la base de datos.

Abstrae el acceso a datos de partidas, desacoplando la lógica
de negocio de los detalles de implementación de SQLAlchemy.

Autor: Gernibide
"""

from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.juego import Partida


class PartidaRepository:
    """Repositorio para gestionar operaciones de Partida.

    Proporciona queries especializadas para estadísticas de usuarios.
    """

    def __init__(self, db: Session):
        """Inicializa el repositorio.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def get_distinct_dates_for_user(self, user_id: str) -> list[date]:
        """Obtiene fechas distintas donde el usuario jugó.

        Args:
            user_id: ID del usuario.

        Returns:
            Lista de fechas (date) ordenadas descendente.
        """
        fechas_query = (
            self.db.query(func.date(Partida.fecha_inicio))
            .filter(Partida.id_usuario == user_id)
            .distinct()
            .order_by(func.date(Partida.fecha_inicio).desc())
            .all()
        )
        return [fecha[0] for fecha in fechas_query]

    def get_last_partida_date(self, user_id: str) -> datetime | None:
        """Obtiene fecha de la última partida del usuario.

        Args:
            user_id: ID del usuario.

        Returns:
            Datetime de última partida o None si no hay partidas.
        """
        ultima_partida_obj = (
            self.db.query(Partida.fecha_inicio)
            .filter(Partida.id_usuario == user_id)
            .order_by(Partida.fecha_inicio.desc())
            .first()
        )
        return ultima_partida_obj[0] if ultima_partida_obj else None
