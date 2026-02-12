"""Repositorio para operaciones de Profesor en la base de datos.

Abstrae el acceso a datos de profesores, desacoplando la lógica
de negocio de los detalles de implementación de SQLAlchemy.

Autor: Gernibide
"""

from sqlalchemy.orm import Session

from app.models.profesor import Profesor


class ProfesorRepository:
    """Repositorio para gestionar operaciones CRUD de Profesor.

    Proporciona una capa de abstracción sobre SQLAlchemy para
    desacoplar la lógica de negocio del ORM.
    """

    def __init__(self, db: Session):
        """Inicializa el repositorio.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def get_by_id(self, profesor_id: str) -> Profesor | None:
        """Obtiene un profesor por ID.

        Args:
            profesor_id: ID del profesor.

        Returns:
            Profesor si existe, None si no.
        """
        return self.db.query(Profesor).filter(Profesor.id == profesor_id).first()

    def get_by_username(self, username: str) -> Profesor | None:
        """Obtiene un profesor por username.

        Args:
            username: Username del profesor.

        Returns:
            Profesor si existe, None si no.
        """
        return self.db.query(Profesor).filter(Profesor.username == username).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Profesor]:
        """Obtiene lista paginada de profesores.

        Args:
            skip: Número de registros a saltar.
            limit: Número máximo de registros.

        Returns:
            Lista de profesores.
        """
        return self.db.query(Profesor).offset(skip).limit(limit).all()

    def create(self, profesor: Profesor) -> Profesor:
        """Crea un nuevo profesor.

        Args:
            profesor: Instancia de Profesor a crear.

        Returns:
            Profesor creado con datos actualizados.
        """
        self.db.add(profesor)
        self.db.commit()
        self.db.refresh(profesor)
        return profesor

    def update(self, profesor: Profesor) -> Profesor:
        """Actualiza un profesor existente.

        Args:
            profesor: Instancia de Profesor a actualizar.

        Returns:
            Profesor actualizado.
        """
        self.db.commit()
        self.db.refresh(profesor)
        return profesor

    def delete(self, profesor: Profesor) -> None:
        """Elimina un profesor.

        Args:
            profesor: Instancia de Profesor a eliminar.
        """
        self.db.delete(profesor)
        self.db.commit()

    def exists(self, profesor_id: str) -> bool:
        """Verifica si existe un profesor con el ID dado.

        Args:
            profesor_id: ID del profesor a verificar.

        Returns:
            True si existe, False si no.
        """
        return self.db.query(Profesor).filter(Profesor.id == profesor_id).first() is not None

    def exists_by_username(self, username: str) -> bool:
        """Verifica si existe un profesor con el username dado.

        Args:
            username: Username a verificar.

        Returns:
            True si existe, False si no.
        """
        return self.db.query(Profesor).filter(Profesor.username == username).first() is not None
