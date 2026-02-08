"""Tests unitarios para UsuarioService.

Tests aislados de la lógica de negocio del servicio de usuarios,
usando mocks para los repositorios (sin base de datos).

Autor: Gernibide
"""

import uuid
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioBulkCreate, UsuarioCreate, UsuarioUpdate
from app.services.usuario_service import UsuarioService


class TestUsuarioServiceCreacion:
    """Tests unitarios para crear usuarios"""

    def test_crear_usuario_exitoso(self):
        """Test: Crear usuario con datos válidos"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()

        mock_usuario_repo.exists_by_username.return_value = False
        mock_usuario_repo.create.return_value = Usuario(
            id=str(uuid.uuid4()),
            username="testuser",
            nombre="Test",
            apellido="User",
            password="hashed_password",
        )

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)
        usuario_data = UsuarioCreate(
            username="testuser",
            nombre="Test",
            apellido="User",
            password="password123",
        )

        # Act
        resultado = service.crear_usuario(usuario_data)

        # Assert
        assert resultado.username == "testuser"
        mock_usuario_repo.exists_by_username.assert_called_once_with("testuser")
        mock_usuario_repo.create.assert_called_once()

    def test_crear_usuario_username_duplicado(self):
        """Test: Falla si username ya existe"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()

        mock_usuario_repo.exists_by_username.return_value = True  # Username existe

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)
        usuario_data = UsuarioCreate(
            username="duplicado",
            nombre="Test",
            apellido="User",
            password="password123",
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.crear_usuario(usuario_data)

        assert exc_info.value.status_code == 400
        assert "username" in exc_info.value.detail.lower()
        mock_usuario_repo.create.assert_not_called()

    def test_crear_usuario_valida_clase_existe(self):
        """Test: Valida que la clase existe al crear usuario"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()

        mock_usuario_repo.exists_by_username.return_value = False
        mock_clase_repo.exists.return_value = False  # Clase NO existe

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)
        usuario_data = UsuarioCreate(
            username="testuser",
            nombre="Test",
            apellido="User",
            password="password123",
            id_clase=str(uuid.uuid4()),
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.crear_usuario(usuario_data)

        assert exc_info.value.status_code == 404
        assert "clase" in exc_info.value.detail.lower()
        mock_clase_repo.exists.assert_called_once()
        mock_usuario_repo.create.assert_not_called()

    def test_crear_usuario_sin_clase_no_valida(self):
        """Test: No valida clase si no se proporciona"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()

        mock_usuario_repo.exists_by_username.return_value = False
        mock_usuario_repo.create.return_value = Usuario(
            id=str(uuid.uuid4()),
            username="testuser",
            nombre="Test",
            apellido="User",
            password="hashed_password",
        )

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)
        usuario_data = UsuarioCreate(
            username="testuser",
            nombre="Test",
            apellido="User",
            password="password123",
            # Sin id_clase
        )

        # Act
        service.crear_usuario(usuario_data)

        # Assert
        mock_clase_repo.exists.assert_not_called()  # No debe validar clase


class TestUsuarioServiceActualizacion:
    """Tests unitarios para actualizar usuarios"""

    def test_actualizar_usuario_exitoso(self):
        """Test: Actualizar usuario con datos válidos"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()

        usuario_existente = Usuario(
            id=str(uuid.uuid4()),
            username="testuser",
            nombre="Test",
            apellido="User",
            password="hashed_password",
        )

        mock_usuario_repo.get_by_id.return_value = usuario_existente
        mock_usuario_repo.update.return_value = usuario_existente

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)
        usuario_data = UsuarioUpdate(nombre="Nombre Actualizado")

        # Act
        resultado = service.actualizar_usuario(usuario_existente.id, usuario_data)

        # Assert
        assert resultado.nombre == "Nombre Actualizado"
        mock_usuario_repo.update.assert_called_once()

    def test_actualizar_usuario_username_duplicado(self):
        """Test: Falla si intenta cambiar a username existente"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()

        usuario_existente = Usuario(
            id=str(uuid.uuid4()),
            username="testuser",
            nombre="Test",
            apellido="User",
            password="hashed_password",
        )

        mock_usuario_repo.get_by_id.return_value = usuario_existente
        mock_usuario_repo.exists_by_username.return_value = True  # Username ya existe

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)
        usuario_data = UsuarioUpdate(username="otro_username")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.actualizar_usuario(usuario_existente.id, usuario_data)

        assert exc_info.value.status_code == 400
        mock_usuario_repo.update.assert_not_called()

    def test_actualizar_usuario_clase_inexistente(self):
        """Test: Falla si intenta asignar clase inexistente"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()

        usuario_existente = Usuario(
            id=str(uuid.uuid4()),
            username="testuser",
            nombre="Test",
            apellido="User",
            password="hashed_password",
        )

        mock_usuario_repo.get_by_id.return_value = usuario_existente
        mock_clase_repo.exists.return_value = False  # Clase NO existe

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)
        usuario_data = UsuarioUpdate(id_clase=str(uuid.uuid4()))

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.actualizar_usuario(usuario_existente.id, usuario_data)

        assert exc_info.value.status_code == 404
        assert "clase" in exc_info.value.detail.lower()
        mock_usuario_repo.update.assert_not_called()


class TestUsuarioServiceBulk:
    """Tests unitarios para importación masiva"""

    def test_bulk_validacion_clase_inexistente(self):
        """Test: Falla si clase no existe en bulk import"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()
        mock_db = Mock()

        mock_clase_repo.exists.return_value = False  # Clase NO existe

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)
        bulk_data = UsuarioBulkCreate(
            id_clase=str(uuid.uuid4()),
            usuarios=[
                UsuarioCreate(
                    username="user1",
                    nombre="User",
                    apellido="1",
                    password="password123",
                )
            ],
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.crear_usuarios_bulk(bulk_data, mock_db)

        assert exc_info.value.status_code == 404
        assert "clase" in exc_info.value.detail.lower()
        mock_db.rollback.assert_called_once()

    def test_bulk_validacion_duplicados_en_batch(self):
        """Test: Falla si hay usernames duplicados dentro del batch"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()
        mock_db = Mock()

        mock_clase_repo.exists.return_value = True

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)
        bulk_data = UsuarioBulkCreate(
            id_clase=str(uuid.uuid4()),
            usuarios=[
                UsuarioCreate(
                    username="duplicado",
                    nombre="User",
                    apellido="1",
                    password="password123",
                ),
                UsuarioCreate(
                    username="duplicado",  # Duplicado
                    nombre="User",
                    apellido="2",
                    password="password123",
                ),
            ],
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.crear_usuarios_bulk(bulk_data, mock_db)

        assert exc_info.value.status_code == 400
        assert "duplicado" in exc_info.value.detail.lower()
        mock_db.rollback.assert_called_once()

    def test_bulk_validacion_username_existe_bd(self):
        """Test: Falla si username ya existe en BD"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()
        mock_db = Mock()

        mock_clase_repo.exists.return_value = True
        # Simular que un username ya existe
        usuario_existente = Mock()
        usuario_existente.username = "existente"
        mock_usuario_repo.get_by_usernames.return_value = [usuario_existente]

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)
        bulk_data = UsuarioBulkCreate(
            id_clase=str(uuid.uuid4()),
            usuarios=[
                UsuarioCreate(
                    username="existente",  # Ya existe en BD
                    nombre="User",
                    apellido="1",
                    password="password123",
                )
            ],
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.crear_usuarios_bulk(bulk_data, mock_db)

        assert exc_info.value.status_code == 400
        assert "existente" in exc_info.value.detail.lower()
        mock_db.rollback.assert_called_once()

    def test_bulk_creacion_exitosa(self):
        """Test: Bulk import exitoso con todos los datos válidos"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()
        mock_db = Mock()

        mock_clase_repo.exists.return_value = True
        mock_usuario_repo.get_by_usernames.return_value = []  # Ninguno existe
        mock_usuario_repo.bulk_create.return_value = [
            Usuario(
                id=str(uuid.uuid4()),
                username="user1",
                nombre="User",
                apellido="1",
                password="hashed",
            ),
            Usuario(
                id=str(uuid.uuid4()),
                username="user2",
                nombre="User",
                apellido="2",
                password="hashed",
            ),
        ]

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)
        bulk_data = UsuarioBulkCreate(
            id_clase=str(uuid.uuid4()),
            usuarios=[
                UsuarioCreate(
                    username="user1",
                    nombre="User",
                    apellido="1",
                    password="password123",
                ),
                UsuarioCreate(
                    username="user2",
                    nombre="User",
                    apellido="2",
                    password="password123",
                ),
            ],
        )

        # Act
        usuarios_creados, errores = service.crear_usuarios_bulk(bulk_data, mock_db)

        # Assert
        assert len(usuarios_creados) == 2
        assert errores == []
        mock_usuario_repo.bulk_create.assert_called_once()
        mock_db.rollback.assert_not_called()


class TestUsuarioServiceConsultas:
    """Tests unitarios para consultas de usuarios"""

    def test_obtener_usuario_existente(self):
        """Test: Obtener usuario que existe"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()

        usuario_mock = Usuario(
            id=str(uuid.uuid4()),
            username="testuser",
            nombre="Test",
            apellido="User",
            password="hashed",
        )
        mock_usuario_repo.get_by_id.return_value = usuario_mock

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)

        # Act
        resultado = service.obtener_usuario(usuario_mock.id)

        # Assert
        assert resultado == usuario_mock
        mock_usuario_repo.get_by_id.assert_called_once_with(usuario_mock.id)

    def test_obtener_usuario_inexistente(self):
        """Test: Falla si usuario no existe"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()

        mock_usuario_repo.get_by_id.return_value = None  # Usuario no existe

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.obtener_usuario(str(uuid.uuid4()))

        assert exc_info.value.status_code == 404

    def test_listar_usuarios_con_paginacion(self):
        """Test: Listar usuarios respeta skip y limit"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()

        mock_usuario_repo.get_all.return_value = [Mock(), Mock()]

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)

        # Act
        resultado = service.listar_usuarios(skip=10, limit=20)

        # Assert
        assert len(resultado) == 2
        mock_usuario_repo.get_all.assert_called_once_with(10, 20)

    def test_eliminar_usuario_existente(self):
        """Test: Eliminar usuario que existe"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()

        usuario_mock = Usuario(
            id=str(uuid.uuid4()),
            username="testuser",
            nombre="Test",
            apellido="User",
            password="hashed",
        )
        mock_usuario_repo.get_by_id.return_value = usuario_mock

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)

        # Act
        service.eliminar_usuario(usuario_mock.id)

        # Assert
        mock_usuario_repo.delete.assert_called_once_with(usuario_mock)

    def test_eliminar_usuario_inexistente(self):
        """Test: Falla si intenta eliminar usuario inexistente"""
        # Arrange
        mock_usuario_repo = Mock()
        mock_clase_repo = Mock()

        mock_usuario_repo.get_by_id.return_value = None  # Usuario no existe

        service = UsuarioService(mock_usuario_repo, mock_clase_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.eliminar_usuario(str(uuid.uuid4()))

        assert exc_info.value.status_code == 404
        mock_usuario_repo.delete.assert_not_called()
