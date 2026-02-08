"""Repositorio para operaciones de Clase en la base de datos.

Abstrae el acceso a datos de clases, desacoplando la lógica
de negocio de los detalles de implementación de SQLAlchemy.

Autor: Gernibide
"""


from sqlalchemy.orm import Session

from app.models.clase import Clase


class ClaseRepository:
    """Repositorio para gestionar operaciones de Clase.

    Proporciona una capa de abstracción sobre SQLAlchemy para
    desacoplar la lógica de negocio del ORM.
    """

    def __init__(self, db: Session):
        """Inicializa el repositorio.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def get_by_id(self, clase_id: str) -> Clase | None:
        """Obtiene una clase por ID.

        Args:
            clase_id: ID de la clase.

        Returns:
            Clase si existe, None si no.
        """
        return self.db.query(Clase).filter(Clase.id == clase_id).first()

    def exists(self, clase_id: str) -> bool:
        """Verifica si existe una clase con el ID dado.

        Args:
            clase_id: ID de la clase a verificar.

        Returns:
            True si existe, False si no.
        """
        return self.db.query(Clase).filter(Clase.id == clase_id).first() is not None
