"""
Tests para endpoints de autenticación
"""


class TestAuth:
    """Tests para autenticación de usuarios"""

    def test_login_exitoso(self, client, test_usuario):
        """Test: Login con credenciales correctas debe devolver token"""
        response = client.post(
            "/api/v1/auth/login-app",
            json={"username": "testuser", "password": "password123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_usuario_inexistente(self, client):
        """Test: Login con usuario inexistente debe fallar"""
        response = client.post(
            "/api/v1/auth/login-app",
            json={"username": "noexiste", "password": "password123"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "error" in data

    def test_login_password_incorrecta(self, client, test_usuario):
        """Test: Login con password incorrecta debe fallar"""
        response = client.post(
            "/api/v1/auth/login-app",
            json={"username": "testuser", "password": "incorrecta"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "error" in data

    def test_login_datos_faltantes(self, client):
        """Test: Login sin datos requeridos debe fallar"""
        response = client.post("/api/v1/auth/login-app", json={"username": "testuser"})

        assert response.status_code == 422

    def test_login_datos_vacios(self, client):
        """Test: Login con strings vacíos debe fallar"""
        response = client.post("/api/v1/auth/login-app", json={"username": "", "password": ""})

        assert response.status_code == 401
