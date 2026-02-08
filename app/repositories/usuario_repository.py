"""Repositorio para operaciones de Usuario en la base de datos.

Abstrae el acceso a datos de usuarios, desacoplando la lógica
de negocio de los detalles de implementación de SQLAlchemy.

Autor: Gernibide
"""

from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class UsuarioRepository:
    """Repositorio para gestionar operaciones CRUD de Usuario.

    Proporciona una capa de abstracción sobre SQLAlchemy para
    desacoplar la lógica de negocio del ORM.
    """

    def __init__(self, db: Session):
        """Inicializa el repositorio.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def get_by_id(self, usuario_id: str) -> Usuario | None:
        """Obtiene un usuario por ID.

        Args:
            usuario_id: ID del usuario.

        Returns:
            Usuario si existe, None si no.
        """
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def get_by_username(self, username: str) -> Usuario | None:
        """Obtiene un usuario por username.

        Args:
            username: Username del usuario.

        Returns:
            Usuario si existe, None si no.
        """
        return self.db.query(Usuario).filter(Usuario.username == username).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Usuario]:
        """Obtiene lista paginada de usuarios.

        Args:
            skip: Número de registros a saltar.
            limit: Número máximo de registros.

        Returns:
            Lista de usuarios.
        """
        return self.db.query(Usuario).offset(skip).limit(limit).all()

    def create(self, usuario: Usuario) -> Usuario:
        """Crea un nuevo usuario.

        Args:
            usuario: Instancia de Usuario a crear.

        Returns:
            Usuario creado con datos actualizados.
        """
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def update(self, usuario: Usuario) -> Usuario:
        """Actualiza un usuario existente.

        Args:
            usuario: Instancia de Usuario a actualizar.

        Returns:
            Usuario actualizado.
        """
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def delete(self, usuario: Usuario) -> None:
        """Elimina un usuario.

        Args:
            usuario: Instancia de Usuario a eliminar.
        """
        self.db.delete(usuario)
        self.db.commit()

    def exists_by_username(self, username: str) -> bool:
        """Verifica si existe un usuario con el username dado.

        Args:
            username: Username a verificar.

        Returns:
            True si existe, False si no.
        """
        return self.db.query(Usuario).filter(Usuario.username == username).first() is not None

    def get_by_usernames(self, usernames: list[str]) -> list[Usuario]:
        """Obtiene usuarios por lista de usernames.

        Útil para validar duplicados en importación bulk.

        Args:
            usernames: Lista de usernames a buscar.

        Returns:
            Lista de usuarios encontrados.
        """
        return self.db.query(Usuario).filter(Usuario.username.in_(usernames)).all()

    def bulk_create(self, usuarios: list[Usuario]) -> list[Usuario]:
        """Crea múltiples usuarios de forma transaccional.

        Args:
            usuarios: Lista de instancias de Usuario a crear.

        Returns:
            Lista de usuarios creados con datos actualizados.

        Note:
            Si falla, el caller debe hacer rollback.
        """
        for usuario in usuarios:
            self.db.add(usuario)
        self.db.commit()
        for usuario in usuarios:
            self.db.refresh(usuario)
        return usuarios
