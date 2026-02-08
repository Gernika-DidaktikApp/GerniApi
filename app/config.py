"""Configuración de la aplicación usando Pydantic Settings.

Este módulo define la clase Settings que carga la configuración
desde variables de entorno y el archivo .env.

Autor: Gernibide
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación.

    Carga las variables de configuración desde el archivo .env
    y las expone como atributos de la clase.

    Attributes:
        DATABASE_URL: URL de conexión a la base de datos PostgreSQL.
        SECRET_KEY: Clave secreta para firmar tokens JWT.
        ALGORITHM: Algoritmo de cifrado para JWT (por defecto HS256).
        ACCESS_TOKEN_EXPIRE_MINUTES: Tiempo de expiración de tokens en minutos.
        API_V1_PREFIX: Prefijo para rutas de la API v1.
        PROJECT_NAME: Nombre del proyecto.
        API_KEY: Clave API para autenticación administrativa.
        API_KEY_HEADER: Nombre del header para la API Key.
    """

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 días
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "GerniBide API"
    API_KEY: str
    API_KEY_HEADER: str = "X-API-Key"

    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 10

    class Config:
        """Configuración de Pydantic Settings."""

        env_file = ".env"


settings = Settings()
