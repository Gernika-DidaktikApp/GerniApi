"""
Configuración de fixtures para tests de GerniBide API
"""

# ruff: noqa: E402
import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Configurar variables de entorno para testing ANTES de importar la app
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models.actividad import Actividad
from app.models.clase import Clase
from app.models.juego import Partida
from app.models.profesor import Profesor
from app.models.punto import Punto
from app.models.usuario import Usuario
from app.utils.security import generar_codigo_clase, hash_password

# API Key para tests
TEST_API_KEY = settings.API_KEY

# Database de test en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Crea una sesión de base de datos para tests"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Cliente de test con base de datos de prueba"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_usuario(db_session):
    """Crea un usuario de prueba"""
    usuario = Usuario(
        id=str(uuid.uuid4()),
        username="testuser",
        nombre="Test",
        apellido="User",
        password=hash_password("password123"),  # Hashear la contraseña
        top_score=0,
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def test_usuario_secundario(db_session):
    """Crea un segundo usuario de prueba para tests de ownership"""
    usuario = Usuario(
        id=str(uuid.uuid4()),
        username="otrouser",
        nombre="Otro",
        apellido="Usuario",
        password=hash_password("password123"),
        top_score=0,
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def test_profesor(db_session):
    """Crea un profesor de prueba"""
    profesor = Profesor(
        id=str(uuid.uuid4()),
        username="testprofesor",
        nombre="Profesor",
        apellido="Test",
        password=hash_password("password123"),  # Hashear la contraseña
    )
    db_session.add(profesor)
    db_session.commit()
    db_session.refresh(profesor)
    return profesor


@pytest.fixture
def test_clase(db_session, test_profesor):
    """Crea una clase de prueba"""
    clase = Clase(
        id=str(uuid.uuid4()),
        codigo=generar_codigo_clase(),
        id_profesor=test_profesor.id,
        nombre="1º ESO A",
    )
    db_session.add(clase)
    db_session.commit()
    db_session.refresh(clase)
    return clase


@pytest.fixture
def test_punto(db_session):
    """Crea un punto de prueba"""
    punto = Punto(id=str(uuid.uuid4()), nombre="Punto de Prueba")
    db_session.add(punto)
    db_session.commit()
    db_session.refresh(punto)
    return punto


@pytest.fixture
def test_actividades(db_session, test_punto):
    """Crea 3 actividades de prueba para un punto"""
    actividades = []
    for i in range(1, 4):
        actividad = Actividad(id=str(uuid.uuid4()), id_punto=test_punto.id, nombre=f"Actividad {i}")
        db_session.add(actividad)
        actividades.append(actividad)

    db_session.commit()
    for actividad in actividades:
        db_session.refresh(actividad)
    return actividades


@pytest.fixture
def test_partida(db_session, test_usuario):
    """Crea una partida de prueba"""
    from datetime import datetime

    partida = Partida(
        id=str(uuid.uuid4()),
        id_usuario=test_usuario.id,
        estado="en_progreso",
        fecha_inicio=datetime.now(),
    )
    db_session.add(partida)
    db_session.commit()
    db_session.refresh(partida)
    return partida


@pytest.fixture
def test_actividad_completada(db_session, test_partida, test_actividades):
    """Crea una actividad completada con progreso"""
    from app.models.actividad_progreso import ActividadProgreso

    actividad_progreso = ActividadProgreso(
        id=str(uuid.uuid4()),
        id_juego=test_partida.id,
        id_actividad=test_actividades[0].id,
        id_punto=test_actividades[0].id_punto,
        estado="completado",
        puntuacion=100.0,
    )
    db_session.add(actividad_progreso)
    db_session.commit()
    db_session.refresh(actividad_progreso)
    return actividad_progreso


@pytest.fixture
def auth_token(client, test_usuario):
    """Obtiene un token de autenticación"""
    response = client.post(
        "/api/v1/auth/login-app",
        json={"username": "testuser", "password": "password123"},
    )
    if response.status_code != 200:
        print(f"\n❌ Login failed: {response.status_code}")
        print(f"Response: {response.json()}")
        pytest.fail(f"Login failed with status {response.status_code}: {response.json()}")
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Headers con autenticación JWT"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def api_key_headers():
    """Headers con API Key para acceso administrativo"""
    return {"X-API-Key": TEST_API_KEY}


class TestClientWithApiKey:
    """Wrapper del TestClient que incluye API Key en todas las requests"""

    def __init__(self, client, api_key):
        self._client = client
        self._headers = {"X-API-Key": api_key}

    def _merge_headers(self, kwargs):
        headers = kwargs.get("headers", {})
        headers.update(self._headers)
        kwargs["headers"] = headers
        return kwargs

    def get(self, url, **kwargs):
        return self._client.get(url, **self._merge_headers(kwargs))

    def post(self, url, **kwargs):
        return self._client.post(url, **self._merge_headers(kwargs))

    def put(self, url, **kwargs):
        return self._client.put(url, **self._merge_headers(kwargs))

    def delete(self, url, **kwargs):
        return self._client.delete(url, **self._merge_headers(kwargs))

    def patch(self, url, **kwargs):
        return self._client.patch(url, **self._merge_headers(kwargs))


@pytest.fixture
def admin_client(client):
    """Cliente de test con API Key incluida en todas las requests"""
    return TestClientWithApiKey(client, TEST_API_KEY)
