"""
Cliente HTTP para interactuar con la API de GerniBide

En lugar de acceder directamente a la base de datos, usa los endpoints
de la API con autenticación via API Key. Esto es más seguro y respeta
los permisos y auditoría de la aplicación.
"""

import os
from typing import Any

import httpx
from rich.console import Console

console = Console()


class APIClient:
    """Cliente para interactuar con la API de GerniBide"""

    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        """
        Inicializa el cliente API

        Args:
            base_url: URL base de la API (ej: http://localhost:8000)
            api_key: API Key para autenticación. Si no se proporciona,
                     se lee de la variable de entorno API_KEY
        """
        self.base_url = base_url or os.getenv("API_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("API_KEY")

        if not self.api_key:
            console.print(
                "[bold red]❌ Error:[/bold red] API_KEY no configurada\n"
                "[dim]Configura la variable de entorno API_KEY o pásala como parámetro[/dim]"
            )
            raise ValueError("API_KEY requerida")

        self.headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
        self.client = httpx.Client(base_url=self.base_url, headers=self.headers, timeout=30.0)

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Maneja la respuesta HTTP y errores"""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = "Error desconocido"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", error_data.get("message", str(error_data)))
            except Exception:
                error_detail = e.response.text

            console.print(
                f"[bold red]❌ Error HTTP {e.response.status_code}:[/bold red] {error_detail}"
            )
            raise

    # ==================== Usuarios ====================

    def list_usuarios(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """Lista usuarios"""
        response = self.client.get("/api/v1/usuarios", params={"skip": skip, "limit": limit})
        return self._handle_response(response)

    def get_usuario(self, usuario_id: str) -> dict[str, Any]:
        """Obtiene un usuario por ID"""
        response = self.client.get(f"/api/v1/usuarios/{usuario_id}")
        return self._handle_response(response)

    def create_usuario(self, data: dict[str, Any]) -> dict[str, Any]:
        """Crea un nuevo usuario"""
        response = self.client.post("/api/v1/usuarios", json=data)
        return self._handle_response(response)

    def delete_usuario(self, usuario_id: str) -> dict[str, Any]:
        """Elimina un usuario"""
        response = self.client.delete(f"/api/v1/usuarios/{usuario_id}")
        return self._handle_response(response)

    def bulk_import_usuarios(
        self, usuarios: list[dict[str, Any]], id_clase: str | None = None
    ) -> dict[str, Any]:
        """Importación masiva de usuarios"""
        data = {"usuarios": usuarios}
        if id_clase:
            data["id_clase"] = id_clase

        response = self.client.post("/api/v1/usuarios/bulk", json=data)
        return self._handle_response(response)

    # ==================== Profesores ====================

    def list_profesores(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """Lista profesores"""
        response = self.client.get("/api/v1/profesores", params={"skip": skip, "limit": limit})
        return self._handle_response(response)

    def create_profesor(self, data: dict[str, Any]) -> dict[str, Any]:
        """Crea un nuevo profesor"""
        response = self.client.post("/api/v1/profesores", json=data)
        return self._handle_response(response)

    def delete_profesor(self, profesor_id: str) -> dict[str, Any]:
        """Elimina un profesor"""
        response = self.client.delete(f"/api/v1/profesores/{profesor_id}")
        return self._handle_response(response)

    # ==================== Clases ====================

    def list_clases(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """Lista clases"""
        response = self.client.get("/api/v1/clases", params={"skip": skip, "limit": limit})
        return self._handle_response(response)

    def get_clase(self, clase_id: str) -> dict[str, Any]:
        """Obtiene una clase por ID"""
        response = self.client.get(f"/api/v1/clases/{clase_id}")
        return self._handle_response(response)

    # ==================== Actividades ====================

    def list_actividades(self, skip: int = 0, limit: int = 1000) -> list[dict[str, Any]]:
        """Lista actividades"""
        response = self.client.get("/api/v1/actividades", params={"skip": skip, "limit": limit})
        return self._handle_response(response)

    # ==================== Partidas ====================

    def list_partidas(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """Lista partidas"""
        response = self.client.get("/api/v1/partidas", params={"skip": skip, "limit": limit})
        return self._handle_response(response)

    # ==================== Puntos ====================

    def list_puntos(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """Lista puntos"""
        response = self.client.get("/api/v1/puntos", params={"skip": skip, "limit": limit})
        return self._handle_response(response)

    # ==================== Estadísticas ====================

    def get_usuario_stats(self, usuario_id: str) -> dict[str, Any]:
        """Obtiene estadísticas de un usuario"""
        response = self.client.get(f"/api/v1/usuarios/{usuario_id}/estadisticas")
        return self._handle_response(response)

    def get_gameplay_stats(self, usuario_id: str) -> dict[str, Any]:
        """Obtiene estadísticas de gameplay de un usuario"""
        response = self.client.get(f"/api/v1/statistics/gameplay/{usuario_id}")
        return self._handle_response(response)

    # ==================== Utilidades ====================

    def health_check(self) -> dict[str, Any]:
        """Verifica que la API está funcionando"""
        response = self.client.get("/health")
        return self._handle_response(response)

    def close(self):
        """Cierra el cliente HTTP"""
        self.client.close()

    def __enter__(self):
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()
