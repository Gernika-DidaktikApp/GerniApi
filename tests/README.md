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

# Un test específico
pytest tests/test_estados.py::TestEventoEstados::test_completar_evento_exitoso
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
└── README.md                   # Este archivo
```

## Fixtures Disponibles

### Fixtures de Base de Datos

- `db_session`: Sesión de base de datos en memoria (SQLite)
- `client`: Cliente de test con FastAPI TestClient

### Fixtures de Datos

- `test_usuario`: Usuario de prueba creado en BD
- `test_profesor`: Profesor de prueba
- `test_clase`: Clase de prueba
- `test_actividad`: Actividad de prueba
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

## Notas

- Los tests usan SQLite en memoria para mayor velocidad
- Cada test tiene su propia sesión de BD aislada
- Los fixtures se limpian automáticamente después de cada test
- No se requiere configurar PostgreSQL para los tests
