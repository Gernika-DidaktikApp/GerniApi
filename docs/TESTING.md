# Testing - Guía de Pruebas

Esta guía documenta la configuración de tests, fixtures y mejores prácticas para el proyecto GerniBide API.

## 📋 Contenido

- [Estructura de Tests](#estructura-de-tests)
- [Configuración de Fixtures](#configuración-de-fixtures)
- [Compatibilidad Python 3.11+](#compatibilidad-python-311)
- [Ejecutar Tests](#ejecutar-tests)
- [Mejores Prácticas](#mejores-prácticas)

## 🏗️ Estructura de Tests

```
tests/
├── conftest.py              # Fixtures compartidos y configuración global
├── test_auth.py             # Tests de autenticación
├── test_usuarios.py         # Tests de endpoints de usuarios
├── test_estados.py          # Tests de progreso de actividades
├── test_health.py           # Tests de health checks
└── unit/                    # Tests unitarios de servicios
    ├── test_usuario_service.py
    └── test_usuario_stats_service.py
```

## 🔧 Configuración de Fixtures

### Fixtures de Base de Datos

**`db_session`**: Sesión de SQLite en memoria para tests
```python
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
```

**Características**:
- Scope: `function` (nueva BD para cada test)
- Base de datos: SQLite en memoria (`:memory:`)
- Cleanup: Se destruye automáticamente después de cada test

### Fixtures de Modelos

**Fixtures disponibles**:
- `test_usuario`: Usuario básico (username: "testuser")
- `test_usuario_secundario`: Segundo usuario para tests de ownership
- `test_profesor`: Profesor de prueba
- `test_clase`: Clase asociada al profesor
- `test_punto`: Punto/módulo de aprendizaje
- `test_actividades`: Lista de 3 actividades
- `test_partida`: Partida en progreso
- `test_actividad_completada`: Actividad con progreso completado

**Ejemplo de uso**:
```python
def test_crear_partida(db_session, test_usuario):
    partida = Partida(
        id=str(uuid.uuid4()),
        id_usuario=test_usuario.id,
        estado="en_progreso"
    )
    db_session.add(partida)
    db_session.commit()
    assert partida.id_usuario == test_usuario.id
```

### Fixtures de Autenticación

**`auth_token`**: Token JWT para autenticación
```python
@pytest.fixture
def auth_token(client, test_usuario):
    """Obtiene un token de autenticación"""
    response = client.post(
        "/api/v1/auth/login-app",
        json={"username": "testuser", "password": "password123"},
    )
    if response.status_code != 200:
        pytest.fail(f"Login failed: {response.json()}")
    return response.json()["access_token"]
```

**`auth_headers`**: Headers con Bearer token
```python
@pytest.fixture
def auth_headers(auth_token):
    """Headers con autenticación JWT"""
    return {"Authorization": f"Bearer {auth_token}"}
```

**`api_key_headers`**: Headers con API Key para admin
```python
@pytest.fixture
def api_key_headers():
    """Headers con API Key para acceso administrativo"""
    return {"X-API-Key": TEST_API_KEY}
```

### Fixtures de Cliente HTTP

**`client`**: TestClient básico con dependency injection
```python
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
```

**`admin_client`**: Cliente con API Key incluida automáticamente
```python
@pytest.fixture
def admin_client(client):
    """Cliente de test con API Key incluida en todas las requests"""
    return TestClientWithApiKey(client, TEST_API_KEY)
```

**Ejemplo de uso**:
```python
def test_listar_usuarios(admin_client):
    # API Key ya incluida automáticamente
    response = admin_client.get("/api/v1/usuarios/")
    assert response.status_code == 200
```

## 🐍 Compatibilidad Python 3.11+

### Problema de Rate Limiting en Tests

**Contexto**: El proyecto usa `fastapi-limiter` para rate limiting en producción, pero en tests esto debe ser mockeado para evitar dependencias de Redis.

**Problema anterior**: En Python 3.11, el mock simple de `RateLimiter` causaba errores de validación:
```
{'field': 'query.args', 'message': 'Field required'}
{'field': 'query.kwargs', 'message': 'Field required'}
```

**Solución implementada** (en `tests/conftest.py`):
```python
# Mock de fastapi_limiter para tests (antes de importar app)
fastapi_limiter_mock = MagicMock()
fastapi_limiter_depends_mock = MagicMock()

def dummy_rate_limiter(*args, **kwargs):
    """Dependency dummy que no hace nada"""
    return lambda: None

fastapi_limiter_depends_mock.RateLimiter = dummy_rate_limiter

sys.modules["fastapi_limiter"] = fastapi_limiter_mock
sys.modules["fastapi_limiter.depends"] = fastapi_limiter_depends_mock
```

**Por qué funciona**:
- `RateLimiter` en producción retorna una dependencia de FastAPI
- El mock debe retornar también una dependencia válida (`lambda: None`)
- Esto evita que FastAPI intente validar parámetros inexistentes
- Compatible con Python 3.11, 3.12 y 3.13

### Orden de Imports en conftest.py

**Importante**: Los mocks deben configurarse ANTES de importar la aplicación:

```python
# ruff: noqa: E402
import sys
from unittest.mock import MagicMock

# 1. Configurar mocks PRIMERO
sys.modules["fastapi_limiter"] = fastapi_limiter_mock
sys.modules["fastapi_limiter.depends"] = fastapi_limiter_depends_mock

# 2. DESPUÉS importar la app
from app.main import app
from app.database import Base, get_db
# ...
```

**Nota**: El comentario `# ruff: noqa: E402` desactiva el linter que se queja de imports no al inicio del archivo. Esto es necesario y correcto en este caso.

## 🚀 Ejecutar Tests

### Tests Completos

```bash
# Todos los tests
pytest tests/ -v

# Con reporte de cobertura
pytest tests/ --cov=app --cov-report=html

# Tests específicos
pytest tests/test_auth.py -v
pytest tests/test_usuarios.py::TestUsuariosEndpoints::test_crear_usuario_exitoso -v
```

### Tests Unitarios de Servicios

```bash
# Todos los tests unitarios
pytest tests/unit/ -v

# Test específico de servicio
pytest tests/unit/test_usuario_service.py -v
pytest tests/unit/test_usuario_stats_service.py -v
```

### Tests con Output Detallado

```bash
# Mostrar prints y logs
pytest tests/ -v -s

# Mostrar traceback completo en fallos
pytest tests/ -v --tb=long

# Solo el primer fallo
pytest tests/ -v -x
```

### Tests en Modo Watch (desarrollo)

```bash
# Instalar pytest-watch
pip install pytest-watch

# Ejecutar tests automáticamente al guardar archivos
ptw tests/ -- -v
```

## ✅ Mejores Prácticas

### 1. Estructura de Tests (AAA Pattern)

```python
def test_crear_usuario_exitoso(client, admin_client):
    # Arrange (Preparar)
    usuario_data = {
        "username": "nuevouser",
        "nombre": "Nuevo",
        "apellido": "Usuario",
        "password": "password123"
    }

    # Act (Actuar)
    response = admin_client.post("/api/v1/usuarios/", json=usuario_data)

    # Assert (Afirmar)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "nuevouser"
    assert data["nombre"] == "Nuevo"
    assert "password" not in data  # No exponer password
```

### 2. Nombres Descriptivos

```python
# ❌ Mal
def test_1(client):
    ...

# ✅ Bien
def test_crear_usuario_con_username_duplicado_debe_fallar(client, admin_client):
    ...
```

### 3. Un Concepto por Test

```python
# ❌ Mal - test hace demasiadas cosas
def test_usuario(client, admin_client):
    # Crear usuario
    response = admin_client.post(...)
    assert response.status_code == 201

    # Actualizar usuario
    response = client.put(...)
    assert response.status_code == 200

    # Eliminar usuario
    response = admin_client.delete(...)
    assert response.status_code == 200

# ✅ Bien - tests separados
def test_crear_usuario_exitoso(admin_client):
    ...

def test_actualizar_usuario_exitoso(client, auth_headers):
    ...

def test_eliminar_usuario_exitoso(admin_client):
    ...
```

### 4. Usar Fixtures para Setup Común

```python
# ❌ Mal - duplicar código de setup
def test_estadisticas_usuario(client, db_session):
    # Crear usuario
    usuario = Usuario(...)
    db_session.add(usuario)
    db_session.commit()

    # Test...

def test_partida_usuario(client, db_session):
    # Crear usuario (duplicado)
    usuario = Usuario(...)
    db_session.add(usuario)
    db_session.commit()

    # Test...

# ✅ Bien - usar fixture test_usuario
def test_estadisticas_usuario(client, test_usuario):
    # test_usuario ya está creado
    ...

def test_partida_usuario(client, test_usuario):
    # test_usuario ya está creado
    ...
```

### 5. Verificar Formato de Error Correcto

El proyecto usa un formato de error personalizado:

```python
# ❌ Mal - asumir formato estándar de FastAPI
def test_login_fallido(client):
    response = client.post(...)
    assert response.status_code == 401
    assert "detail" in response.json()  # ❌ No existe

# ✅ Bien - usar formato personalizado
def test_login_fallido(client):
    response = client.post(...)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert "message" in data["error"]
```

### 6. Tests Unitarios vs Integración

**Tests de Integración** (usan BD y HTTP):
```python
def test_crear_usuario_endpoint(client, admin_client):
    """Test de integración: endpoint completo"""
    response = admin_client.post("/api/v1/usuarios/", json={...})
    assert response.status_code == 201
```

**Tests Unitarios** (mockan dependencias):
```python
def test_usuario_service_crear():
    """Test unitario: lógica de negocio sin BD"""
    mock_repo = MagicMock()
    mock_repo.get_by_username.return_value = None

    service = UsuarioService(mock_repo)
    usuario = service.crear_usuario(UsuarioCreate(...))

    mock_repo.create.assert_called_once()
```

### 7. Limpieza de Datos

**No es necesario** limpiar manualmente la BD:
```python
# ❌ Innecesario - la fixture ya limpia
def test_algo(db_session, test_usuario):
    # Test...

    # Cleanup manual innecesario
    db_session.query(Usuario).delete()
    db_session.commit()
```

La fixture `db_session` tiene `scope="function"` y destruye la BD automáticamente.

## 📊 Cobertura de Tests

### Generar Reporte

```bash
# HTML (más legible)
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html

# Terminal
pytest tests/ --cov=app --cov-report=term-missing

# Solo porcentaje
pytest tests/ --cov=app --cov-report=term
```

### Objetivos de Cobertura

- **Mínimo aceptable**: 70%
- **Objetivo**: 85%
- **Ideal**: 95%+

**Áreas críticas** (deben tener 95%+ cobertura):
- Autenticación y autorización
- Validaciones de datos
- Lógica de negocio en servicios
- Operaciones de base de datos transaccionales

**Áreas menos críticas** (pueden tener <70%):
- Código de configuración (`config.py`)
- Scripts de inicialización
- Archivos de logging

## 🐛 Debugging Tests

### Print Debugging

```python
def test_algo(client, test_usuario):
    response = client.post(...)

    # Ver respuesta completa
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
```

```bash
# Ejecutar con output de prints
pytest tests/test_auth.py::test_algo -v -s
```

### Usar Debugger

```python
def test_algo(client, test_usuario):
    import pdb; pdb.set_trace()  # Breakpoint

    response = client.post(...)
    assert response.status_code == 200
```

### Ver Queries SQL

```python
# En conftest.py, temporalmente
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # ← Mostrar queries SQL
    ...
)
```

## 🔄 Actualizar Tests

### Cuando Cambias un Schema

```python
# Si cambias app/schemas/usuario.py
class UsuarioCreate(BaseModel):
    nuevo_campo: str  # ← Campo nuevo

# Actualizar tests afectados
def test_crear_usuario_exitoso(admin_client):
    usuario_data = {
        "username": "user",
        "nombre": "Test",
        "apellido": "User",
        "password": "pass",
        "nuevo_campo": "valor"  # ← Añadir
    }
    response = admin_client.post("/api/v1/usuarios/", json=usuario_data)
    assert response.status_code == 201
```

### Cuando Cambias un Endpoint

```python
# Si cambias ruta: /api/v1/usuarios → /api/v2/usuarios
def test_listar_usuarios(admin_client):
    response = admin_client.get("/api/v2/usuarios/")  # ← Actualizar ruta
    assert response.status_code == 200
```

### Cuando Cambias Lógica de Negocio

```python
# Si cambias validación: username mínimo 3 caracteres
def test_crear_usuario_username_muy_corto(admin_client):
    response = admin_client.post("/api/v1/usuarios/", json={
        "username": "ab",  # Solo 2 caracteres
        ...
    })
    assert response.status_code == 422  # Debe fallar validación
```

## 📚 Recursos

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)
- [Coverage.py](https://coverage.readthedocs.io/)

## ✅ Checklist antes de Commit

- [ ] Todos los tests pasan: `pytest tests/ -v`
- [ ] Cobertura adecuada: `pytest tests/ --cov=app --cov-report=term`
- [ ] Tests unitarios para nueva lógica de negocio
- [ ] Tests de integración para nuevos endpoints
- [ ] Tests de casos edge y errores
- [ ] Nombres de tests descriptivos
- [ ] Sin código comentado o prints de debug
- [ ] Fixtures reutilizadas apropiadamente

---

**Última actualización**: 2026-02-08 - Añadida documentación de compatibilidad Python 3.11+ con rate limiting mocks
