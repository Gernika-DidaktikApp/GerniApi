"""Tests de integración para endpoints de usuarios.

Tests para los endpoints del módulo usuarios después de la refactorización
a Clean Architecture (Router → Service → Repository).

Autor: Gernibide
"""

import uuid


class TestUsuariosEndpoints:
    """Tests de integración para endpoints de usuarios"""

    def test_crear_usuario_exitoso(self, client):
        """Test: Crear usuario con datos válidos"""
        response = client.post(
            "/api/v1/usuarios",
            json={
                "username": "nuevo_usuario",
                "nombre": "Test",
                "apellido": "Usuario",
                "password": "password123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "nuevo_usuario"
        assert data["nombre"] == "Test"
        assert data["apellido"] == "Usuario"
        assert "password" not in data  # No debe devolver password
        assert "id" in data

    def test_crear_usuario_username_duplicado(self, client, test_usuario):
        """Test: No permite crear usuario con username existente"""
        response = client.post(
            "/api/v1/usuarios",
            json={
                "username": "testuser",  # Ya existe en test_usuario
                "nombre": "Test",
                "apellido": "Usuario",
                "password": "password123",
            },
        )

        assert response.status_code == 400
        assert "username" in response.json()["error"]["message"].lower()

    def test_crear_usuario_con_clase_valida(self, client, test_clase):
        """Test: Crear usuario asignado a una clase existente"""
        response = client.post(
            "/api/v1/usuarios",
            json={
                "username": "estudiante_nuevo",
                "nombre": "Estudiante",
                "apellido": "Nuevo",
                "password": "password123",
                "id_clase": test_clase.id,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id_clase"] == test_clase.id

    def test_crear_usuario_clase_inexistente(self, client):
        """Test: Falla si se intenta asignar a clase inexistente"""
        response = client.post(
            "/api/v1/usuarios",
            json={
                "username": "estudiante_nuevo",
                "nombre": "Estudiante",
                "apellido": "Nuevo",
                "password": "password123",
                "id_clase": str(uuid.uuid4()),  # Clase inexistente
            },
        )

        assert response.status_code == 404
        assert "clase" in response.json()["error"]["message"].lower()

    def test_crear_usuario_con_codigo_clase(self, client, test_clase):
        """Test: Crear usuario usando código de clase en lugar de UUID"""
        response = client.post(
            "/api/v1/usuarios",
            json={
                "username": "estudiante_codigo",
                "nombre": "Estudiante",
                "apellido": "Codigo",
                "password": "password123",
                "codigo_clase": test_clase.codigo,  # Usar código en lugar de UUID
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id_clase"] == test_clase.id
        assert data["username"] == "estudiante_codigo"

    def test_crear_usuario_codigo_clase_inexistente(self, client):
        """Test: Falla si se usa código de clase inexistente"""
        response = client.post(
            "/api/v1/usuarios",
            json={
                "username": "estudiante_nuevo",
                "nombre": "Estudiante",
                "apellido": "Nuevo",
                "password": "password123",
                "codigo_clase": "FAKE99",  # Código inexistente
            },
        )

        assert response.status_code == 404
        message = response.json()["error"]["message"].lower()
        assert "codigo" in message or "código" in message or "clase" in message

    def test_listar_usuarios_requiere_api_key(self, client, test_usuario):
        """Test: Listar usuarios requiere API Key"""
        response = client.get("/api/v1/usuarios")

        assert response.status_code == 403

    def test_listar_usuarios_con_api_key(self, admin_client, test_usuario):
        """Test: Listar usuarios con API Key funciona"""
        response = admin_client.get("/api/v1/usuarios")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(u["username"] == "testuser" for u in data)

    def test_listar_usuarios_paginacion(self, admin_client, test_usuario):
        """Test: Paginación de usuarios funciona"""
        response = admin_client.get("/api/v1/usuarios?skip=0&limit=1")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1

    def test_obtener_usuario_propio_con_token(self, client, test_usuario, auth_headers):
        """Test: Usuario puede ver su propio perfil con token"""
        response = client.get(f"/api/v1/usuarios/{test_usuario.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_usuario.id
        assert data["username"] == test_usuario.username

    def test_obtener_usuario_otro_con_token_falla(self, client, test_usuario, auth_headers):
        """Test: Usuario no puede ver perfil de otro usuario con token"""
        otro_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/usuarios/{otro_id}", headers=auth_headers)

        # Debería fallar con 403 (sin permiso) o 404 (no existe)
        assert response.status_code in [403, 404]

    def test_obtener_usuario_con_api_key(self, admin_client, test_usuario):
        """Test: API Key puede ver cualquier usuario"""
        response = admin_client.get(f"/api/v1/usuarios/{test_usuario.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_usuario.id

    def test_obtener_usuario_inexistente(self, admin_client):
        """Test: Obtener usuario inexistente devuelve 404"""
        usuario_id = str(uuid.uuid4())
        response = admin_client.get(f"/api/v1/usuarios/{usuario_id}")

        assert response.status_code == 404

    def test_actualizar_usuario_propio(self, client, test_usuario, auth_headers):
        """Test: Usuario puede actualizar su propio perfil"""
        response = client.put(
            f"/api/v1/usuarios/{test_usuario.id}",
            headers=auth_headers,
            json={"nombre": "Nombre Actualizado"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Nombre Actualizado"
        assert data["apellido"] == test_usuario.apellido  # No cambió

    def test_actualizar_usuario_username_duplicado(
        self, client, test_usuario, test_usuario_secundario, auth_headers
    ):
        """Test: No permite actualizar a username ya existente"""
        response = client.put(
            f"/api/v1/usuarios/{test_usuario.id}",
            headers=auth_headers,
            json={"username": test_usuario_secundario.username},
        )

        assert response.status_code == 400
        assert "username" in response.json()["error"]["message"].lower()

    def test_actualizar_usuario_otro_falla(self, client, test_usuario_secundario, auth_headers):
        """Test: Usuario no puede actualizar otro usuario con token"""
        response = client.put(
            f"/api/v1/usuarios/{test_usuario_secundario.id}",
            headers=auth_headers,
            json={"nombre": "Intento Malicioso"},
        )

        assert response.status_code == 403

    def test_actualizar_usuario_clase_inexistente(self, client, test_usuario, auth_headers):
        """Test: Falla al actualizar con clase inexistente"""
        response = client.put(
            f"/api/v1/usuarios/{test_usuario.id}",
            headers=auth_headers,
            json={"id_clase": str(uuid.uuid4())},
        )

        assert response.status_code == 404
        assert "clase" in response.json()["error"]["message"].lower()

    def test_eliminar_usuario_requiere_api_key(self, client, test_usuario):
        """Test: Eliminar usuario requiere API Key"""
        response = client.delete(f"/api/v1/usuarios/{test_usuario.id}")

        assert response.status_code == 403

    def test_eliminar_usuario_con_api_key(self, admin_client, test_usuario_secundario):
        """Test: API Key puede eliminar usuarios"""
        response = admin_client.delete(f"/api/v1/usuarios/{test_usuario_secundario.id}")

        assert response.status_code == 204

        # Verificar que fue eliminado
        response = admin_client.get(f"/api/v1/usuarios/{test_usuario_secundario.id}")
        assert response.status_code == 404

    def test_eliminar_usuario_inexistente(self, admin_client):
        """Test: Eliminar usuario inexistente devuelve 404"""
        usuario_id = str(uuid.uuid4())
        response = admin_client.delete(f"/api/v1/usuarios/{usuario_id}")

        assert response.status_code == 404


class TestUsuariosBulk:
    """Tests para importación masiva de usuarios"""

    def test_bulk_import_exitoso(self, admin_client, test_clase):
        """Test: Importación masiva exitosa con clase válida"""
        response = admin_client.post(
            "/api/v1/usuarios/bulk",
            json={
                "id_clase": test_clase.id,
                "usuarios": [
                    {
                        "username": "bulk_user1",
                        "nombre": "Bulk",
                        "apellido": "User1",
                        "password": "password123",
                    },
                    {
                        "username": "bulk_user2",
                        "nombre": "Bulk",
                        "apellido": "User2",
                        "password": "password123",
                    },
                    {
                        "username": "bulk_user3",
                        "nombre": "Bulk",
                        "apellido": "User3",
                        "password": "password123",
                    },
                ],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["total"] == 3
        assert len(data["usuarios_creados"]) == 3
        assert data["errores"] == []

    def test_bulk_import_sin_clase(self, admin_client):
        """Test: Importación masiva sin clase asignada"""
        response = admin_client.post(
            "/api/v1/usuarios/bulk",
            json={
                "usuarios": [
                    {
                        "username": "bulk_no_clase1",
                        "nombre": "Sin",
                        "apellido": "Clase",
                        "password": "password123",
                    }
                ]
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["total"] == 1

    def test_bulk_import_clase_inexistente(self, admin_client):
        """Test: Falla si clase no existe (transaccional)"""
        response = admin_client.post(
            "/api/v1/usuarios/bulk",
            json={
                "id_clase": str(uuid.uuid4()),
                "usuarios": [
                    {
                        "username": "bulk_fail1",
                        "nombre": "Fail",
                        "apellido": "User",
                        "password": "password123",
                    }
                ],
            },
        )

        assert response.status_code == 404
        assert "clase" in response.json()["error"]["message"].lower()

    def test_bulk_import_username_duplicado_en_batch(self, admin_client, test_clase):
        """Test: Falla si hay usernames duplicados dentro del batch (transaccional)"""
        response = admin_client.post(
            "/api/v1/usuarios/bulk",
            json={
                "id_clase": test_clase.id,
                "usuarios": [
                    {
                        "username": "duplicado",
                        "nombre": "Usuario",
                        "apellido": "1",
                        "password": "password123",
                    },
                    {
                        "username": "duplicado",  # Duplicado
                        "nombre": "Usuario",
                        "apellido": "2",
                        "password": "password123",
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert "duplicado" in response.json()["error"]["message"].lower()

    def test_bulk_import_username_ya_existe_bd(self, admin_client, test_usuario, test_clase):
        """Test: Falla si username ya existe en BD (transaccional)"""
        response = admin_client.post(
            "/api/v1/usuarios/bulk",
            json={
                "id_clase": test_clase.id,
                "usuarios": [
                    {
                        "username": "testuser",  # Ya existe (test_usuario)
                        "nombre": "Intento",
                        "apellido": "Duplicado",
                        "password": "password123",
                    },
                    {
                        "username": "nuevo_valido",
                        "nombre": "Nuevo",
                        "apellido": "Valido",
                        "password": "password123",
                    },
                ],
            },
        )

        assert response.status_code == 400
        assert "testuser" in response.json()["error"]["message"].lower()

        # Verificar que NINGUNO fue creado (transaccional)
        response = admin_client.get("/api/v1/usuarios")
        usernames = [u["username"] for u in response.json()]
        assert "nuevo_valido" not in usernames  # No se creó por rollback

    def test_bulk_import_requiere_autenticacion(self, client, test_clase):
        """Test: Bulk import requiere autenticación"""
        response = client.post(
            "/api/v1/usuarios/bulk",
            json={
                "id_clase": test_clase.id,
                "usuarios": [
                    {
                        "username": "fail",
                        "nombre": "Fail",
                        "apellido": "User",
                        "password": "password123",
                    }
                ],
            },
        )

        assert response.status_code == 401


class TestUsuariosEstadisticas:
    """Tests para estadísticas de usuarios"""

    def test_estadisticas_usuario_sin_datos(self, client, test_usuario, auth_headers):
        """Test: Estadísticas de usuario sin actividad"""
        response = client.get(
            f"/api/v1/usuarios/{test_usuario.id}/estadisticas", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["actividades_completadas"] == 0
        assert data["racha_dias"] == 0
        assert data["modulos_completados"] == []
        assert data["ultima_partida"] is None
        assert data["total_puntos_acumulados"] == 0.0

    def test_estadisticas_usuario_con_actividad(
        self,
        client,
        test_usuario,
        auth_headers,
        test_partida,
        test_actividad_completada,
    ):
        """Test: Estadísticas con actividad completada"""
        response = client.get(
            f"/api/v1/usuarios/{test_usuario.id}/estadisticas", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["actividades_completadas"] >= 1
        assert data["total_puntos_acumulados"] >= 0

    def test_estadisticas_usuario_otro_falla(self, client, test_usuario_secundario, auth_headers):
        """Test: No puede ver estadísticas de otro usuario con token"""
        response = client.get(
            f"/api/v1/usuarios/{test_usuario_secundario.id}/estadisticas",
            headers=auth_headers,
        )

        assert response.status_code == 403

    def test_estadisticas_usuario_con_api_key(self, admin_client, test_usuario):
        """Test: API Key puede ver estadísticas de cualquier usuario"""
        response = admin_client.get(f"/api/v1/usuarios/{test_usuario.id}/estadisticas")

        assert response.status_code == 200
        data = response.json()
        assert "actividades_completadas" in data
        assert "racha_dias" in data

    def test_estadisticas_usuario_inexistente(self, admin_client):
        """Test: Estadísticas de usuario inexistente devuelve 404"""
        usuario_id = str(uuid.uuid4())
        response = admin_client.get(f"/api/v1/usuarios/{usuario_id}/estadisticas")

        assert response.status_code == 404
