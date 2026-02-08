# Tests de GerniBide API

Suite completa de tests para la API de GerniBide.

## Instalación

Instalar dependencias de testing:

```bash
pip install -r requirements.txt
```

## Ejecutar Tests

### Todos los tests

```bash
pytest
```

### Tests con mayor detalle

```bash
pytest -v
```

### Tests con cobertura

```bash
pytest --cov=app --cov-report=html
```

### Tests específicos

```bash
# Solo tests de autenticación
pytest tests/test_auth.py

# Solo tests de estados
pytest tests/test_estados.py

# Solo tests de usuarios (integración)
pytest tests/test_usuarios.py

# Solo tests unitarios
pytest tests/unit/

# Tests unitarios del servicio de usuarios
pytest tests/unit/test_usuario_service.py

# Tests unitarios de estadísticas
pytest tests/unit/test_usuario_stats_service.py

# Un test específico
pytest tests/test_estados.py::TestEventoEstados::test_completar_evento_exitoso

# Tests de una clase específica
pytest tests/test_usuarios.py::TestUsuariosBulk
```

### Tests por categoría

```bash
# Tests de integración
pytest -m integration

# Tests unitarios
pytest -m unit

# Tests lentos
pytest -m slow
```

## Estructura de Tests

```
tests/
├── __init__.py                 # Inicializador
├── conftest.py                 # Fixtures compartidos
├── test_auth.py                # Tests de autenticación
├── test_estados.py             # Tests del sistema de estados
├── test_health.py              # Tests de health check
├── test_usuarios.py            # Tests de endpoints de usuarios (NUEVO)
├── unit/                       # Tests unitarios (NUEVO)
│   ├── __init__.py
│   ├── test_usuario_service.py         # Tests unitarios de UsuarioService
│   └── test_usuario_stats_service.py   # Tests unitarios de UsuarioStatsService
└── README.md                   # Este archivo
```

## Fixtures Disponibles

### Fixtures de Base de Datos

- `db_session`: Sesión de base de datos en memoria (SQLite)
- `client`: Cliente de test con FastAPI TestClient

### Fixtures de Datos

- `test_usuario`: Usuario de prueba creado en BD
- `test_usuario_secundario`: Segundo usuario para tests de ownership (NUEVO)
- `test_profesor`: Profesor de prueba
- `test_clase`: Clase de prueba
- `test_actividad`: Actividad de prueba
- `test_actividades`: Lista de 3 actividades de prueba
- `test_actividad_completada`: Actividad completada con progreso (NUEVO)
- `test_eventos`: Lista de 3 eventos de prueba
- `test_partida`: Partida de prueba

### Fixtures de Autenticación

- `auth_token`: Token JWT de autenticación
- `auth_headers`: Headers con Bearer token

## Cobertura de Tests

Los tests cubren:

- ✅ Autenticación (login, tokens, errores)
- ✅ Health checks y endpoints básicos
- ✅ Sistema de estados de actividades
- ✅ Sistema de estados de eventos
- ✅ Auto-completado de actividades
- ✅ Cálculo automático de duraciones
- ✅ Suma de puntuaciones
- ✅ Validaciones de datos
- ✅ Manejo de errores

### Tests de Usuarios (NUEVO - Clean Architecture)

#### Tests de Integración (`test_usuarios.py`)
- ✅ CRUD completo de usuarios
- ✅ Validaciones de autenticación (token vs API Key)
- ✅ Validaciones de ownership (usuarios propios vs ajenos)
- ✅ Validaciones de datos (username duplicado, clase inexistente)
- ✅ Importación masiva transaccional (bulk import)
- ✅ Estadísticas de usuarios
- **Total: 35+ tests de integración**

#### Tests Unitarios de Servicios (`unit/test_usuario_service.py`)
- ✅ Lógica de negocio de UsuarioService (con mocks)
- ✅ Validaciones sin base de datos
- ✅ Creación, actualización, eliminación
- ✅ Importación bulk transaccional
- ✅ Manejo de errores y edge cases
- **Total: 15+ tests unitarios**

#### Tests Unitarios de Estadísticas (`unit/test_usuario_stats_service.py`)
- ✅ Cálculo de racha de días consecutivos
- ✅ Conteo de actividades completadas
- ✅ Suma de puntos acumulados
- ✅ Listado de módulos completados
- ✅ Edge cases (sin datos, rachas interrumpidas)
- **Total: 12+ tests unitarios**

## Casos de Prueba Importantes

### Tests de Estados

1. **Flujo completo de actividad:**
   - Iniciar actividad
   - Iniciar eventos secuencialmente
   - Completar eventos con puntuación
   - Verificar auto-completado de actividad
   - Verificar suma de puntuaciones

2. **Validaciones:**
   - No permitir duplicados
   - Validar relaciones entre entidades
   - Verificar estados correctos

3. **Cálculos automáticos:**
   - Duración en segundos
   - Suma de puntuaciones
   - Timestamps correctos

## Continuous Integration

Los tests se pueden integrar en CI/CD:

```yaml
# Ejemplo para GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest -v
```

### Tests para CI/CD (ejecución en push)

Los tests están diseñados para ejecutarse en CI/CD sin configuración adicional:

**Tests rápidos (unitarios):**
```bash
# Solo tests unitarios (rápidos, sin BD real)
pytest tests/unit/ -v --tb=short
```
- ✅ **Duración**: <1 segundo
- ✅ **Sin dependencias externas**: No requieren BD PostgreSQL
- ✅ **Ideales para pre-commit hooks**

**Tests completos (integración):**
```bash
# Todos los tests (unitarios + integración)
DATABASE_URL="sqlite:///:memory:" SECRET_KEY="test-key" API_KEY="test-api-key" pytest -v
```
- ✅ **Duración**: <5 segundos
- ✅ **BD en memoria**: No requieren PostgreSQL instalado
- ✅ **Ideales para CI/CD en push**

**Ejemplo de configuración CI/CD:**
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run unit tests (fast)
        run: |
          pytest tests/unit/ -v

      - name: Run integration tests
        env:
          DATABASE_URL: "sqlite:///:memory:"
          SECRET_KEY: "test-secret-key-ci-cd"
          API_KEY: "test-api-key-ci-cd"
        run: |
          pytest tests/ -v --ignore=tests/unit/

      - name: Generate coverage report
        env:
          DATABASE_URL: "sqlite:///:memory:"
          SECRET_KEY: "test-secret-key"
          API_KEY: "test-api-key"
        run: |
          pytest --cov=app --cov-report=xml --cov-report=html
```

## Ventajas de la Nueva Arquitectura para Testing

### Antes de la Refactorización (sin servicios)
```python
# ❌ Solo tests de integración (lentos, requieren BD)
def test_crear_usuario():
    response = client.post("/usuarios", json={...})
    assert response.status_code == 201
    # Difícil testear lógica de negocio aislada
```

### Después de la Refactorización (con servicios)
```python
# ✅ Tests unitarios rápidos (sin BD)
def test_servicio_valida_username():
    mock_repo = Mock()
    mock_repo.exists_by_username.return_value = True

    service = UsuarioService(mock_repo, Mock())

    with pytest.raises(HTTPException):
        service.crear_usuario(data)

    # Testea solo la lógica de negocio

# ✅ Tests de integración (verifican todo el flujo)
def test_endpoint_crear_usuario(client):
    response = client.post("/api/v1/usuarios", json={...})
    assert response.status_code == 201
```

### Beneficios
- 🚀 **Tests unitarios 100x más rápidos** (sin BD)
- 🎯 **Mejor cobertura** de lógica de negocio
- 🔧 **Fácil debugging** (tests aislados)
- 🤖 **Ideales para CI/CD** (ejecución rápida en push)
- 📊 **Mayor confianza** en refactorings

## Notas

- Los tests usan SQLite en memoria para mayor velocidad
- Cada test tiene su propia sesión de BD aislada
- Los fixtures se limpian automáticamente después de cada test
- No se requiere configurar PostgreSQL para los tests
- **NUEVO**: Tests unitarios no requieren BD (usan mocks)
