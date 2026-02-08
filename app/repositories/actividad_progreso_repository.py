"""Repositorio para operaciones de ActividadProgreso en la base de datos.

Abstrae el acceso a datos de progreso de actividades, desacoplando la lógica
de negocio de los detalles de implementación de SQLAlchemy.

Autor: Gernibide
"""

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.actividad_progreso import ActividadProgreso
from app.models.juego import Partida


class ActividadProgresoRepository:
    """Repositorio para gestionar operaciones de ActividadProgreso.

    Proporciona queries especializadas para estadísticas de usuarios.
    """

    def __init__(self, db: Session):
        """Inicializa el repositorio.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def count_completed_by_user(self, user_id: str) -> int:
        """Cuenta actividades completadas por el usuario.

        Args:
            user_id: ID del usuario.

        Returns:
            Número de actividades completadas.
        """
        count = (
            self.db.query(func.count(ActividadProgreso.id))
            .join(Partida, ActividadProgreso.id_juego == Partida.id)
            .filter(
                and_(
                    Partida.id_usuario == user_id,
                    ActividadProgreso.estado == "completado",
                )
            )
            .scalar()
        )
        return count or 0

    def sum_points_by_user(self, user_id: str) -> float:
        """Suma total de puntos obtenidos por el usuario.

        Args:
            user_id: ID del usuario.

        Returns:
            Suma de puntos (0.0 si no hay puntos).
        """
        total = (
            self.db.query(func.sum(ActividadProgreso.puntuacion))
            .join(Partida, ActividadProgreso.id_juego == Partida.id)
            .filter(
                and_(
                    Partida.id_usuario == user_id,
                    ActividadProgreso.puntuacion.isnot(None),
                )
            )
            .scalar()
        )
        return total or 0.0
