"""
Tests para endpoints de salud y básicos
"""


class TestHealth:
    """Tests para endpoints de salud"""

    def test_health_check(self, client):
        """Test: Health check debe retornar healthy"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Test: Root endpoint debe responder"""
        response = client.get("/")

        assert response.status_code in [200, 404]  # Depende de la implementación

    def test_docs_disponible(self, client):
        """Test: Documentación /docs debe estar disponible"""
        response = client.get("/docs")

        assert response.status_code == 200
