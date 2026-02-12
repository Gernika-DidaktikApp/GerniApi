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

    def exists_by_codigo(self, codigo: str) -> bool:
        """Verifica si existe una clase con el código dado.

        Args:
            codigo: Código de la clase a verificar.

        Returns:
            True si existe, False si no.
        """
        return self.db.query(Clase).filter(Clase.codigo == codigo).first() is not None

    def get_by_codigo(self, codigo: str) -> Clase | None:
        """Obtiene una clase por su código.

        Args:
            codigo: Código de la clase.

        Returns:
            Clase si existe, None si no.
        """
        return self.db.query(Clase).filter(Clase.codigo == codigo).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Clase]:
        """Obtiene lista paginada de clases.

        Args:
            skip: Número de registros a saltar.
            limit: Número máximo de registros.

        Returns:
            Lista de clases.
        """
        return self.db.query(Clase).offset(skip).limit(limit).all()

    def get_by_profesor(self, profesor_id: str, skip: int = 0, limit: int = 100) -> list[Clase]:
        """Obtiene lista paginada de clases de un profesor.

        Args:
            profesor_id: ID del profesor.
            skip: Número de registros a saltar.
            limit: Número máximo de registros.

        Returns:
            Lista de clases del profesor.
        """
        return (
            self.db.query(Clase)
            .filter(Clase.id_profesor == profesor_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, clase: Clase) -> Clase:
        """Crea una nueva clase.

        Args:
            clase: Instancia de Clase a crear.

        Returns:
            Clase creada con datos actualizados.
        """
        self.db.add(clase)
        self.db.commit()
        self.db.refresh(clase)
        return clase

    def update(self, clase: Clase) -> Clase:
        """Actualiza una clase existente.

        Args:
            clase: Instancia de Clase a actualizar.

        Returns:
            Clase actualizada.
        """
        self.db.commit()
        self.db.refresh(clase)
        return clase

    def delete(self, clase: Clase) -> None:
        """Elimina una clase.

        Args:
            clase: Instancia de Clase a eliminar.
        """
        self.db.delete(clase)
        self.db.commit()

    def count_by_profesor(self, profesor_id: str) -> int:
        """Cuenta el número de clases de un profesor.

        Args:
            profesor_id: ID del profesor.

        Returns:
            Número de clases del profesor.
        """
        return self.db.query(Clase).filter(Clase.id_profesor == profesor_id).count()
