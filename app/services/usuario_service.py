"""Servicio de lógica de negocio para usuarios.

Contiene toda la lógica de negocio relacionada con usuarios,
usando repositorios para acceso a datos.

Autor: Gernibide
"""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.logging import log_db_operation
from app.models.usuario import Usuario
from app.repositories.clase_repository import ClaseRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioBulkCreate, UsuarioCreate, UsuarioUpdate
from app.utils.security import hash_password


class UsuarioService:
    """Servicio para gestionar lógica de negocio de usuarios.

    Coordina operaciones entre repositorios y aplica reglas
    de negocio sin conocer detalles de implementación de datos.
    """

    def __init__(self, usuario_repo: UsuarioRepository, clase_repo: ClaseRepository):
        """Inicializa el servicio.

        Args:
            usuario_repo: Repositorio de usuarios.
            clase_repo: Repositorio de clases.
        """
        self.usuario_repo = usuario_repo
        self.clase_repo = clase_repo

    def crear_usuario(self, usuario_data: UsuarioCreate) -> Usuario:
        """Crea un nuevo usuario.

        Args:
            usuario_data: Datos del usuario a crear.

        Returns:
            Usuario creado.

        Raises:
            HTTPException: Si el username ya existe o la clase no existe.
        """
        # Validar username único
        if self.usuario_repo.exists_by_username(usuario_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El username ya está en uso",
            )

        # Validar que la clase existe
        if usuario_data.id_clase and not self.clase_repo.exists(usuario_data.id_clase):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La clase especificada no existe",
            )

        # Crear instancia de usuario
        nuevo_usuario = Usuario(
            id=str(uuid.uuid4()),
            username=usuario_data.username,
            nombre=usuario_data.nombre,
            apellido=usuario_data.apellido,
            password=hash_password(usuario_data.password),
            id_clase=usuario_data.id_clase,
        )

        # Persistir en BD
        created = self.usuario_repo.create(nuevo_usuario)

        # Log de operación DB
        log_db_operation("CREATE", "usuario", created.id, username=created.username)

        return created

    def obtener_usuario(self, usuario_id: str) -> Usuario:
        """Obtiene un usuario por ID.

        Args:
            usuario_id: ID del usuario.

        Returns:
            Usuario encontrado.

        Raises:
            HTTPException: Si el usuario no existe.
        """
        usuario = self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        return usuario

    def actualizar_usuario(self, usuario_id: str, usuario_data: UsuarioUpdate) -> Usuario:
        """Actualiza un usuario existente.

        Args:
            usuario_id: ID del usuario.
            usuario_data: Datos a actualizar.

        Returns:
            Usuario actualizado.

        Raises:
            HTTPException: Si el usuario no existe, el username está en uso,
                o la clase especificada no existe.
        """
        # Obtener usuario
        usuario = self.obtener_usuario(usuario_id)

        # Validar username único si cambió
        if (
            usuario_data.username
            and usuario_data.username != usuario.username
            and self.usuario_repo.exists_by_username(usuario_data.username)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El username ya está en uso",
            )

        # Validar que la clase existe
        if usuario_data.id_clase and not self.clase_repo.exists(usuario_data.id_clase):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La clase especificada no existe",
            )

        # Aplicar cambios
        update_data = usuario_data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = hash_password(update_data["password"])

        for field, value in update_data.items():
            setattr(usuario, field, value)

        updated = self.usuario_repo.update(usuario)

        # Log de operación DB
        log_db_operation(
            "UPDATE", "usuario", updated.id, campos_actualizados=list(update_data.keys())
        )

        return updated

    def eliminar_usuario(self, usuario_id: str) -> None:
        """Elimina un usuario.

        Args:
            usuario_id: ID del usuario a eliminar.

        Raises:
            HTTPException: Si el usuario no existe.
        """
        usuario = self.obtener_usuario(usuario_id)
        self.usuario_repo.delete(usuario)

        # Log de operación DB
        log_db_operation("DELETE", "usuario", usuario_id)

    def listar_usuarios(self, skip: int = 0, limit: int = 100) -> list[Usuario]:
        """Lista usuarios paginados.

        Args:
            skip: Número de registros a saltar.
            limit: Número máximo de registros.

        Returns:
            Lista de usuarios.
        """
        return self.usuario_repo.get_all(skip, limit)

    def crear_usuarios_bulk(
        self, usuarios_data: UsuarioBulkCreate, db: Session
    ) -> tuple[list[Usuario], list[str]]:
        """Crea múltiples usuarios de forma transaccional.

        Args:
            usuarios_data: Datos de usuarios a crear.
            db: Sesión de BD (para rollback si falla).

        Returns:
            Tupla (usuarios_creados, errores).

        Raises:
            HTTPException: Si falla alguna validación.

        Note:
            Este método recibe db: Session excepcionalmente para control
            de rollback transaccional (regla de negocio: "todos o ninguno").
        """
        try:
            # 1. Validar que la clase existe
            if usuarios_data.id_clase and not self.clase_repo.exists(usuarios_data.id_clase):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"La clase con ID {usuarios_data.id_clase} no existe",
                )

            # 2. Validar usernames duplicados dentro del batch
            usernames = [u.username for u in usuarios_data.usuarios]
            usernames_set = set(usernames)
            if len(usernames_set) != len(usernames):
                duplicados = [u for u in usernames if usernames.count(u) > 1]
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Hay usernames duplicados en el archivo: {', '.join(set(duplicados))}",
                )

            # 3. Validar que ningún username existe en BD
            existentes = self.usuario_repo.get_by_usernames(usernames)
            if existentes:
                usernames_existentes = [u.username for u in existentes]
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Los siguientes usernames ya existen: {', '.join(usernames_existentes)}",
                )

            # 4. Crear instancias de usuarios
            nuevos_usuarios = []
            for usuario_data in usuarios_data.usuarios:
                nuevo_usuario = Usuario(
                    id=str(uuid.uuid4()),
                    username=usuario_data.username,
                    nombre=usuario_data.nombre,
                    apellido=usuario_data.apellido,
                    password=hash_password(usuario_data.password),
                    id_clase=usuarios_data.id_clase,
                )
                nuevos_usuarios.append(nuevo_usuario)

            # 5. Persistir todos (transaccional)
            created = self.usuario_repo.bulk_create(nuevos_usuarios)

            # 6. Log de operación
            log_db_operation(
                "BULK_CREATE",
                "usuario",
                ",".join([u.id for u in created]),
                count=len(created),
            )

            return created, []

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear usuarios: {str(e)}",
            )
