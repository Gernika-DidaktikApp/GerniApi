"""Repositorio para operaciones de Actividad en la base de datos.

Abstrae el acceso a datos de actividades, desacoplando la lógica
de negocio de los detalles de implementación de SQLAlchemy.

Autor: Gernibide
"""

from sqlalchemy.orm import Session

from app.models.actividad import Actividad


class ActividadRepository:
    """Repositorio para gestionar operaciones de Actividad.

    Proporciona queries para obtener actividades por punto.
    """

    def __init__(self, db: Session):
        """Inicializa el repositorio.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def get_all_by_punto(self, punto_id: str) -> list[Actividad]:
        """Obtiene todas las actividades de un punto.

        Args:
            punto_id: ID del punto.

        Returns:
            Lista de actividades ordenadas por nombre.
        """
        return (
            self.db.query(Actividad)
            .filter(Actividad.id_punto == punto_id)
            .order_by(Actividad.nombre)
            .all()
        )
