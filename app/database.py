"""Configuración de la base de datos con SQLAlchemy.

Este módulo configura el motor de SQLAlchemy, la sesión de base de datos
y la clase base para los modelos. Soporta tanto SQLite como PostgreSQL.

Autor: Gernibide
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Detectar si estamos usando SQLite (para tests) o PostgreSQL (producción)
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Configurar engine según el tipo de base de datos
if is_sqlite:
    # SQLite: sin pool de conexiones (no soporta los parámetros de PostgreSQL)
    # Para SQLite en memoria (tests), usar StaticPool para compartir la misma BD entre conexiones
    from sqlalchemy.pool import StaticPool

    engine_kwargs = {
        "connect_args": {"check_same_thread": False},
        "echo": False,
    }

    # SQLite en memoria requiere StaticPool para tests
    if settings.DATABASE_URL == "sqlite:///:memory:":
        engine_kwargs["poolclass"] = StaticPool

    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
else:
    # PostgreSQL: con pool de conexiones optimizado
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Verifica conexiones antes de usarlas
        pool_size=5,  # Número de conexiones en el pool
        max_overflow=10,  # Conexiones adicionales permitidas
        echo=False,  # Cambiar a True para debug SQL
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependencia para obtener la sesión de BD
def get_db():
    """Dependencia de FastAPI para obtener una sesión de base de datos.

    Crea una nueva sesión de base de datos para cada petición
    y la cierra automáticamente al finalizar.

    Yields:
        Session: Sesión de SQLAlchemy para realizar operaciones de BD.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
