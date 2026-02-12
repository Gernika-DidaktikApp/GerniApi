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

    def get_by_id(self, actividad_id: str) -> Actividad | None:
        """Obtiene una actividad por ID.

        Args:
            actividad_id: ID de la actividad.

        Returns:
            Actividad si existe, None si no.
        """
        return self.db.query(Actividad).filter(Actividad.id == actividad_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Actividad]:
        """Obtiene lista paginada de actividades.

        Args:
            skip: Número de registros a saltar.
            limit: Número máximo de registros.

        Returns:
            Lista de actividades.
        """
        return self.db.query(Actividad).offset(skip).limit(limit).all()

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

    def create(self, actividad: Actividad) -> Actividad:
        """Crea una nueva actividad.

        Args:
            actividad: Instancia de Actividad a crear.

        Returns:
            Actividad creada con datos actualizados.
        """
        self.db.add(actividad)
        self.db.commit()
        self.db.refresh(actividad)
        return actividad

    def update(self, actividad: Actividad) -> Actividad:
        """Actualiza una actividad existente.

        Args:
            actividad: Instancia de Actividad a actualizar.

        Returns:
            Actividad actualizada.
        """
        self.db.commit()
        self.db.refresh(actividad)
        return actividad

    def delete(self, actividad: Actividad) -> None:
        """Elimina una actividad.

        Args:
            actividad: Instancia de Actividad a eliminar.
        """
        self.db.delete(actividad)
        self.db.commit()
