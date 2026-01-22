from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "GerniBide API"
    API_KEY: str
    API_KEY_HEADER: str = "X-API-Key"

    class Config:
        env_file = ".env"


settings = Settings()
