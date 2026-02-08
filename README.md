# GerniBide API

<div align="center">
  <img src="app/web/static/images/GernikaLogo.png" alt="Gernibide Logo" width="300"/>
</div>

<br/>

API REST con FastAPI para la aplicación móvil Gernibide. Gestiona autenticación de usuarios, juegos, puntos y actividades.

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📑 Índice

- [Quick Start](#-quick-start)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación Local](#️-instalación-local)
- [Testing](#-testing)
- [Endpoints Disponibles](#-endpoints-disponibles)
- [Modelos de Base de Datos](#-modelos-de-base-de-datos)
- [Estructura del Proyecto](#️-estructura-del-proyecto)
- [Documentación Adicional](#-documentación-adicional)
- [Características](#-características)

## 🚀 Quick Start

### Desarrollo Local

```bash
# 1. Configurar entorno
./deploy_local.sh

# 2. Acceder a la API
http://localhost:8000/docs
```

### Producción (Railway)

Ver [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) para instrucciones completas de despliegue.

### Para Desarrolladores

```bash
# 1. Ejecutar tests
pytest tests/ -v

# 2. Verificar linting
black --check app/ tests/
isort --check-only app/ tests/
ruff check app/ tests/

# 3. Formatear código automáticamente
black app/ tests/
isort app/ tests/
```

Ver [docs/TESTING.md](docs/TESTING.md) y [docs/LINTING.md](docs/LINTING.md) para guías completas.

---

## 📋 Requisitos Previos

- Python 3.11+ (testeado en 3.11, 3.12, 3.13)
- PostgreSQL 15+
- Git
- Redis (opcional, para rate limiting en producción)

---

## 🛠️ Instalación Local

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd GerniApi
```

### 2. Configurar PostgreSQL

```bash
# Crear base de datos
psql -U postgres
CREATE DATABASE didaktikapp;
\q
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:
```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/didaktikapp
SECRET_KEY=<genera-uno-seguro>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_PREFIX=/api/v1
PROJECT_NAME=GerniBide API
```

**Generar SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Crear entorno virtual e instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Crear tablas

```bash
python create_tables.py
```

### 6. Iniciar servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**La API estará disponible en:**
- API: http://localhost:8000
- Documentación: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## 🌐 Endpoints Disponibles

### Autenticación

#### POST `/api/v1/auth/login-app`
Inicia sesión con usuario y devuelve un token JWT.

**Request Body:**
```json
{
  "username": "test_user",
  "password": "test_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Ejemplo curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login-app" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test_password"}'
```

### Estados de Puntos y Actividades

#### POST `/api/v1/actividad-progreso/iniciar`
Inicia una actividad para un jugador. Registra automáticamente fecha de inicio y establece estado "en_progreso".

#### POST `/api/v1/punto-progreso/iniciar`
Inicia un punto. (Nota: Esto podría necesitar revisión si el endpoint cambió).

#### PUT `/api/v1/actividad-progreso/{id}/completar`
Completa una actividad con su puntuación. **Calcula automáticamente la duración** y si es la última actividad, **completa el punto automáticamente** sumando todas las puntuaciones.

**Ver [API_ENDPOINTS.md](docs/API_ENDPOINTS.md) para documentación completa de estos endpoints.**

### Health Check

#### GET `/health`
Verifica que la API está corriendo.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## 📊 Modelos de Base de Datos

### Usuario
- `id` (UUID)
- `username` (único)
- `nombre`
- `apellido`
- `password`
- `id_clase` (FK a Clase, opcional)
- `creation` (timestamp)
- `top_score` (integer)

### Clase
- `id` (UUID)
- `id_profesor` (FK a Profesor)
- `nombre`

### Profesor
- `id` (UUID)
- `username` (único)
- `nombre`
- `apellido`
- `password`
- `created` (timestamp)

### Partida (tabla: juego)
- `id` (UUID)
- `id_usuario` (FK a Usuario)
- `fecha_inicio`
- `fecha_fin` (opcional)
- `duracion`
- `estado` (en_progreso/finalizada)

### Punto
- `id` (UUID)
- `nombre`

### Actividad
- `id` (UUID)
- `id_punto` (FK a Punto)
- `nombre`

### PuntoResumen (antes ActividadEstado)
- `id` (UUID)
- `id_juego` (FK a Partida)
- `id_punto` (FK a Punto)
- `fecha_inicio` (timestamp)
- `fecha_fin` (timestamp, opcional)
- `duracion` (segundos, calculado automáticamente)
- `estado` (en_progreso/completado)
- `puntuacion_total` (float, suma de puntuaciones de actividades)

### ActividadProgreso (antes EventoEstado)
- `id` (UUID)
- `id_juego` (FK a Partida)
- `id_punto` (FK a Punto)
- `id_actividad` (FK a Actividad)
- `fecha_inicio` (timestamp)
- `fecha_fin` (timestamp, opcional)
- `duracion` (segundos, calculado automáticamente)
- `estado` (en_progreso/completado)
- `puntuacion` (float, puntuación obtenida)

### Sesion
- `id` (UUID)

---

## 🏗️ Estructura del Proyecto

```
GerniApi/
├── app/
│   ├── models/              # Modelos SQLAlchemy (ORM)
│   │   ├── usuario.py
│   │   ├── clase.py
│   │   ├── profesor.py
│   │   ├── juego.py (Partida)
│   │   ├── punto.py
│   │   ├── actividad.py
│   │   └── ...
│   ├── schemas/             # Esquemas Pydantic (validación)
│   │   ├── usuario.py
│   │   └── ...
│   ├── routers/             # Endpoints de la API
│   │   ├── auth.py
│   │   ├── usuarios.py
│   │   ├── i18n.py          # Endpoint para cambiar idioma
│   │   └── ...
│   ├── services/            # Lógica de negocio (Clean Architecture)
│   │   ├── usuario_service.py
│   │   └── usuario_stats_service.py
│   ├── repositories/        # Acceso a datos (Clean Architecture)
│   │   ├── usuario_repository.py
│   │   └── ...
│   ├── utils/               # Utilidades
│   │   ├── security.py      # JWT, autenticación
│   │   ├── dependencies.py  # Dependency injection
│   │   └── rate_limit.py    # Rate limiting con Redis
│   ├── logging/             # Sistema de logging estructurado
│   │   ├── logger.py
│   │   ├── middleware.py
│   │   └── exceptions.py
│   ├── i18n/                # Sistema de internacionalización
│   │   ├── es.json          # Traducciones en español
│   │   ├── eu.json          # Traducciones en euskera
│   │   ├── loader.py        # Carga de traducciones con cache
│   │   └── helpers.py       # Detección de idioma y helpers
│   ├── web/                 # Dashboard web para profesores
│   │   ├── static/          # CSS, JS
│   │   │   ├── js/
│   │   │   │   └── i18n.js  # Sistema de traducción JS
│   │   │   └── css/
│   │   └── templates/       # HTML templates (7 páginas traducidas)
│   ├── config.py            # Configuración (Pydantic Settings)
│   ├── database.py          # Conexión a PostgreSQL/SQLite
│   └── main.py              # Punto de entrada FastAPI
├── tests/
│   ├── conftest.py          # Fixtures y configuración de tests
│   ├── test_auth.py         # Tests de autenticación
│   ├── test_usuarios.py     # Tests de usuarios
│   ├── test_estados.py      # Tests de progreso
│   ├── test_health.py       # Tests de health checks
│   └── unit/                # Tests unitarios de servicios
│       ├── test_usuario_service.py
│       └── test_usuario_stats_service.py
├── docs/                    # Documentación
│   ├── TESTING.md           # Guía completa de testing
│   ├── CI_CD.md             # CI/CD con GitHub Actions
│   ├── LINTING.md           # Linting y formateo
│   ├── API_ENDPOINTS.md     # Documentación de endpoints
│   └── ...
├── .github/
│   └── workflows/
│       ├── tests.yml        # CI: Tests automáticos
│       └── lint.yml         # CI: Linting
├── logs/                    # Logs (solo local, no en git)
├── .env                     # Variables de entorno (NO subir a git)
├── .env.example             # Ejemplo de variables
├── requirements.txt         # Dependencias Python
├── pyproject.toml           # Configuración de linters
├── pytest.ini               # Configuración de pytest
├── Procfile                 # Comando de inicio (Railway)
├── railway.json             # Configuración Railway
├── create_tables.py         # Script para crear tablas
├── deploy_local.sh          # Script de despliegue local
└── README.md                # Este archivo
```

---

## 🌐 Sistema de Internacionalización (i18n)

La plataforma web para profesores está completamente traducida a **Español (ES)** y **Euskera (EU)**, cumpliendo con los requisitos educativos regionales del País Vasco.

### Características i18n

- ✅ **Sistema híbrido**: Backend (Jinja2) + Frontend (JavaScript)
- ✅ **7 páginas traducidas**: Home, Login, Estadísticas (3 páginas), Dashboard (2 páginas)
- ✅ **2 idiomas soportados**: Español (es) y Euskera (eu)
- ✅ **Persistencia**: Preferencia guardada en cookies (1 año)
- ✅ **Cache en memoria**: Traducciones cacheadas para mejor performance
- ✅ **Selector de idioma**: Disponible en todas las páginas
- ✅ **Detección automática**: Cookie → Query param → Accept-Language header
- ✅ **Fácil extensión**: Agregar nuevos idiomas solo requiere crear archivo JSON

### Arquitectura

**Backend (Python):**
```python
# app/i18n/loader.py - Carga traducciones con cache
def load_translations(lang: str) -> dict[str, Any]

# app/i18n/helpers.py - Detección de idioma
def get_language_from_request(request: Request) -> str
def get_translator(request: Request) -> tuple[callable, str]

# app/routers/i18n.py - Endpoint para cambiar idioma
POST /api/set-language {"language": "es"|"eu"}
```

**Frontend (JavaScript):**
```javascript
// app/web/static/js/i18n.js
function t(key) // Traduce claves (ej: t('errors.network'))
function getCurrentLanguage() // Detecta idioma actual
```

**Templates (Jinja2):**
```html
<!-- Sintaxis de traducción -->
<h1>{{ _('statistics.title') }}</h1>
<p>{{ _('statistics.description') }}</p>
```

### Archivos de Traducción

Las traducciones están organizadas jerárquicamente en JSON:

```json
// app/i18n/es.json
{
  "common": {
    "nav": {
      "home": "Inicio",
      "statistics": "Estadísticas"
    }
  },
  "statistics": {
    "users": {
      "summary": {
        "active_users_dau": "Usuarios Activos (DAU)"
      }
    }
  }
}
```

### Usar el Sistema i18n

**En templates HTML:**
```html
<!-- Traducir texto -->
{{ _('common.nav.home') }}

<!-- Con variables -->
{{ _('welcome.message', name=user.nombre) }}

<!-- Selector de idioma -->
<select id="languageSelect">
  <option value="es">ES</option>
  <option value="eu">EU</option>
</select>
```

**En JavaScript:**
```javascript
// Traducir mensaje de error
alert(t('errors.network'));

// Traducir labels de gráficos
const chartData = {
  labels: [t('charts.days'), t('charts.minutes')]
};

// Cambiar idioma (recarga la página)
await fetch('/api/set-language', {
  method: 'POST',
  body: JSON.stringify({ language: 'eu' })
});
window.location.reload();
```

### Agregar Nuevo Idioma

1. **Crear archivo de traducciones:**
   ```bash
   cp app/i18n/es.json app/i18n/fr.json
   # Traducir el contenido a francés
   ```

2. **Actualizar helpers.py:**
   ```python
   SUPPORTED_LANGUAGES = ["es", "eu", "fr"]
   ```

3. **Agregar al selector:**
   ```html
   <option value="fr">FR</option>
   ```

### Páginas Traducidas

1. **home.html** - Página de inicio con hero, stats, features
2. **login.html** - Formulario de inicio de sesión
3. **statistics.html** - Usuarios y Actividad
4. **statistics-gameplay.html** - Uso del Juego
5. **statistics-learning.html** - Rendimiento y Aprendizaje
6. **dashboard.html** - Vista Profesor (análisis de clase)
7. **dashboard-teacher.html** - Gestión de Clases

---

## 🎮 Sistema de Gestión de Progreso

El sistema permite rastrear el progreso de puntos y actividades de los jugadores con **cálculos automáticos** de tiempos y puntuaciones.

### Flujo de Juego

1. **Iniciar Actividad**: `POST /api/v1/actividad-progreso/iniciar`
   - Registra automáticamente la fecha de inicio de la actividad
   - Establece el estado como "en_progreso"

2. **Completar Actividad**: `PUT /api/v1/actividad-progreso/{id}/completar`
   - Recibe la puntuación obtenida por el jugador
   - **Calcula automáticamente** la duración (fecha_fin - fecha_inicio)
   - Actualiza el estado a "completado"
   - **Si es la última actividad** del punto:
     - Completa automáticamente el punto
     - **Suma todas las puntuaciones** de las actividades
     - Calcula la duración total del punto

### Ejemplo de Uso

```javascript
// 1. Iniciar actividad
const actividad = await iniciarActividad(partidaId, actividadId);

// 2. Para cada actividad del punto
for (const actividad of actividades) {
  // Iniciar actividad
  const actividadProgreso = await iniciarActividad(partidaId, puntoId, actividad.id);

  // Jugador completa la actividad
  const puntuacion = await jugarActividad(actividad);

  // Completar actividad (la API calcula duración automáticamente)
  await completarActividad(actividadProgreso.id, puntuacion);
}

// 3. Al completar la última actividad, el punto se completa automáticamente
// con la suma total de puntuaciones y duración calculada
```

### Características Automáticas

- ✅ **Cálculo de duraciones**: Se calcula automáticamente en segundos
- ✅ **Suma de puntuaciones**: El punto acumula puntos de todas las actividades
- ✅ **Auto-completado**: El punto se marca como completado automáticamente
- ✅ **Validaciones**: No se pueden duplicar actividades en progreso
- ✅ **Relaciones verificadas**: Se valida que las actividades pertenezcan al punto

---

## 📱 Uso desde la App Móvil

### 1. Login

```kotlin
// Kotlin/Android
val response = client.post("$baseUrl/api/v1/auth/login-app") {
    contentType(ContentType.Application.Json)
    setBody(LoginRequest("username", "password"))
}
```

```dart
// Flutter
final response = await http.post(
  Uri.parse('$baseUrl/api/v1/auth/login-app'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'username': 'username',
    'password': 'password'
  }),
);
```

### 2. Usar el Token

```
Authorization: Bearer <access_token>
```

---

## 🔒 Seguridad

### Implementado
- ✅ **Bcrypt** para hashear passwords (truncado automático a 72 bytes)
- ✅ **JWT** con tokens que expiran en 30 minutos
- ✅ **HTTPS** en Railway automáticamente
- ✅ **Logging estructurado** de eventos de seguridad
- ✅ **Validación de datos** con Pydantic

### Producción (Recomendaciones adicionales)
- ⚠️ Cambiar `SECRET_KEY` único y seguro (usar `secrets.token_urlsafe(32)`)
- ⚠️ Configurar CORS para solo tu app móvil (no usar `allow_origins=["*"]`)
- ⚠️ Implementar rate limiting para prevenir abuso
- ⚠️ Revisar logs regularmente para detectar actividad sospechosa

**Configurar CORS para producción:**
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-app-movil.com"],  # No usar "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚂 Despliegue en Railway

### Quick Deploy

1. **Push a GitHub:**
   ```bash
   git push origin main
   ```

2. **En Railway:**
   - New Project → Deploy from GitHub
   - Añadir PostgreSQL
   - Configurar variables de entorno

3. **Crear tablas:**
   ```bash
   railway run python create_tables.py
   ```

Ver [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) para guía completa.

---

## 🧪 Testing

El proyecto incluye una suite completa de tests automatizados con pytest y cobertura de código.

### Ejecutar Tests

```bash
# Instalar dependencias (si no están instaladas)
pip install -r requirements.txt

# Ejecutar todos los tests
pytest tests/ -v

# Tests con reporte de cobertura
pytest tests/ --cov=app --cov-report=html

# Ejecutar solo tests de integración
pytest tests/test_*.py -v

# Ejecutar solo tests unitarios
pytest tests/unit/ -v
```

### Suite de Tests (77 tests)

**Tests de Integración**:
- ✅ Autenticación (login, tokens, errores)
- ✅ CRUD de usuarios (crear, listar, actualizar, eliminar)
- ✅ Importación masiva de usuarios (bulk import)
- ✅ Estadísticas de usuarios (racha de días, actividades, puntos)
- ✅ Sistema de progreso de puntos y actividades
- ✅ Auto-completado de puntos
- ✅ Cálculo automático de duraciones
- ✅ Health checks y endpoints básicos

**Tests Unitarios** (tests/unit/):
- ✅ UsuarioService (lógica de negocio de usuarios)
- ✅ UsuarioStatsService (cálculo de estadísticas)
- ✅ Validaciones y casos edge

### Compatibilidad Python 3.11+

Los tests están configurados para funcionar en **Python 3.11, 3.12 y 3.13**:
- Mock mejorado de `fastapi_limiter` compatible con dependency injection
- Base de datos SQLite en memoria para tests (no requiere PostgreSQL)
- Fixtures completas para todos los modelos

Ver **[docs/TESTING.md](docs/TESTING.md)** para:
- Guía completa de fixtures disponibles
- Mejores prácticas de testing
- Debugging y troubleshooting
- Compatibilidad entre versiones de Python

### Linting y Formateo

El proyecto usa **Black**, **isort** y **Ruff** para mantener calidad de código:

```bash
# Verificar formato (sin modificar)
black --check app/ tests/
isort --check-only app/ tests/
ruff check app/ tests/

# Formatear automáticamente
black app/ tests/
isort app/ tests/

# Arreglar errores de Ruff (cuando sea posible)
ruff check --fix app/ tests/
```

Ver **[docs/LINTING.md](docs/LINTING.md)** para configuración detallada y solución de problemas.

### CI/CD con GitHub Actions

El proyecto incluye integración continua que ejecuta automáticamente:

- ✅ **Tests en múltiples versiones** (Python 3.11, 3.12)
- ✅ **Linting** (Black, isort, Ruff)
- ✅ **Reporte de cobertura** generado automáticamente
- ✅ **Cache de dependencias** para builds más rápidos
- ✅ **Tests automáticos** en cada push a `main` y `develop`
- ✅ **Tests en Pull Requests** antes de merge

**Archivos de configuración**:
- [.github/workflows/tests.yml](.github/workflows/tests.yml) - Tests
- [.github/workflows/lint.yml](.github/workflows/lint.yml) - Linting
- [pyproject.toml](pyproject.toml) - Configuración de linters

Ver **[docs/CI_CD.md](docs/CI_CD.md)** para:
- Configuración detallada del CI
- Troubleshooting de errores comunes
- Cómo ver reportes de cobertura
- Variables de entorno en CI

### Testing Manual

#### Crear Usuario de Prueba

```sql
INSERT INTO usuario (id, username, nombre, apellido, password, id_clase, creation, top_score)
VALUES (
    gen_random_uuid()::text,
    'test_user',
    'Test',
    'User',
    'test_password',
    NULL,
    NOW(),
    0
);
```

#### Probar Login

```bash
# Desde terminal
curl -X POST "http://localhost:8000/api/v1/auth/login-app" \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test_password"}'

# Desde navegador
http://localhost:8000/docs
```

---

## 📝 Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de PostgreSQL | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Clave secreta para JWT | `<genera-con-secrets>` |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del token | `30` |
| `API_V1_PREFIX` | Prefijo de la API | `/api/v1` |
| `PROJECT_NAME` | Nombre del proyecto | `GerniBide API` |

---

## 🔍 Solución de Problemas

### Error: "relation does not exist"
**Solución:** Las tablas no se han creado.
```bash
python create_tables.py
```

### Error: "could not connect to server"
**Solución:** PostgreSQL no está corriendo.
```bash
# macOS
brew services start postgresql@15

# Linux
sudo systemctl start postgresql
```

### Error 422 desde la app
**Solución:** Verifica que el body tenga exactamente:
```json
{
  "username": "...",
  "password": "..."
}
```

### Error 401 en login
**Solución:** Verifica que el usuario existe en la BD y las credenciales son correctas.

---

## 📚 Documentación Adicional

### Guías de Usuario
- **[API_ENDPOINTS.md](docs/API_ENDPOINTS.md)** - 📡 **Guía completa de uso de endpoints** (¡Empieza aquí!)
- **[GerniBide.postman_collection.json](GerniBide.postman_collection.json)** - 📮 **Colección de Postman** - Importa y usa todos los endpoints
- [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) - Guía completa de despliegue en Railway
- [QUICKSTART.md](QUICKSTART.md) - Inicio rápido en 5 pasos
- [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) - Guía detallada de despliegue

### Documentación para Desarrolladores
- **[docs/TESTING.md](docs/TESTING.md)** - 🧪 **Guía completa de testing** - Fixtures, compatibilidad Python 3.11+, mejores prácticas
- **[docs/CI_CD.md](docs/CI_CD.md)** - 🚀 **Integración continua con GitHub Actions** - Configuración, troubleshooting
- **[docs/LINTING.md](docs/LINTING.md)** - ✨ **Linting y formateo de código** - Black, isort, Ruff
- [docs/RATE_LIMITING.md](docs/RATE_LIMITING.md) - Rate limiting con Redis
- [tests/README.md](tests/README.md) - Documentación de tests

### 📮 Usando la Colección de Postman

1. **Importar en Postman:**
   - Abre Postman
   - Click en "Import" (esquina superior izquierda)
   - Arrastra `GerniBide.postman_collection.json` o selecciónalo
   - La colección "GerniBide API" aparecerá en tu sidebar

2. **Configurar variables:**
   - Click en la colección → pestaña "Variables"
   - Edita `base_url`:
     - Local: `http://localhost:8000`
     - Railway: `https://tu-api.railway.app`
   - Las demás variables se llenan automáticamente

3. **Usar:**
   - Ejecuta "Login App" primero (guarda el token automáticamente)
   - Los demás endpoints usan el token guardado en `{{auth_token}}`
   - Copia IDs de las respuestas a las variables cuando sea necesario

---

## 📄 Licencia

Este proyecto está bajo licencia MIT.

---

## 🆘 Soporte

¿Necesitas ayuda?
1. Revisa la [documentación completa](DEPLOY_GUIDE.md)
2. Consulta `/docs` en tu API corriendo
3. Revisa los logs en Railway o local

---

## ✨ Características

### Backend & API
- ✅ **FastAPI** con documentación automática (Swagger + ReDoc)
- ✅ **Clean Architecture** - Separación en capas (Router → Service → Repository)
- ✅ **PostgreSQL** con SQLAlchemy 2.0+ y migraciones con Alembic
- ✅ **Autenticación JWT** con tokens seguros y bcrypt para passwords
- ✅ **Rate Limiting** con Redis para protección contra abuso
- ✅ **CORS configurable** para apps móviles
- ✅ **Pool de conexiones** optimizado y compatible SQLite/PostgreSQL

### Logging & Monitoreo
- ✅ **Logging estructurado** con JSON, colores y niveles
- ✅ **Audit logs** para acciones administrativas
- ✅ **Manejo robusto de errores** con formato personalizado
- ✅ **Health checks** y métricas

### Desarrollo & Testing
- ✅ **Suite de 77 tests** automatizados con pytest
- ✅ **Tests unitarios** de servicios con mocks
- ✅ **Tests de integración** de endpoints completos
- ✅ **Cobertura de código** con reportes HTML
- ✅ **Compatibilidad Python 3.11, 3.12, 3.13**
- ✅ **Linting automático** (Black, isort, Ruff)
- ✅ **CI/CD con GitHub Actions** (tests + linting automáticos)

### Funcionalidades de Negocio
- ✅ **Sistema de progreso** de puntos y actividades con cálculos automáticos
- ✅ **Estadísticas de usuarios** (racha de días, puntos acumulados, módulos completados)
- ✅ **Importación masiva** de usuarios con validaciones transaccionales
- ✅ **Dashboard web** para profesores con gestión de clases
- ✅ **Auto-completado de puntos** cuando se completan todas las actividades
- ✅ **Tracking de progreso** con puntuaciones y tiempos calculados automáticamente
- ✅ **Internacionalización (i18n)** - Español y Euskera en toda la plataforma web
- ✅ **7 páginas traducidas** (Home, Login, Estadísticas×3, Dashboard×2)
- ✅ **Selector de idioma** con persistencia en cookies

### DevOps & Deploy
- ✅ **Compatible con Railway** (deploy automático)
- ✅ **Variables de entorno** con Pydantic Settings
- ✅ **Scripts de deployment** automatizados
- ✅ **Colección de Postman** lista para importar
- ✅ **Documentación completa** para desarrolladores

---
