# GerniBide API

API REST con FastAPI para la aplicación móvil Gernibide. Gestiona autenticación de usuarios, juegos, actividades y sesiones.

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

---

## 📋 Requisitos Previos

- Python 3.8+
- PostgreSQL 15+
- Git

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

### Actividad
- `id` (UUID)
- `nombre`

### Eventos
- `id` (UUID)
- `id_actividad` (FK a Actividad)
- `nombre`

### Sesion
- `id` (UUID)

---

## 🏗️ Estructura del Proyecto

```
GerniApi/
├── app/
│   ├── models/          # Modelos SQLAlchemy (ORM)
│   │   ├── usuario.py
│   │   ├── clase.py
│   │   ├── profesor.py
│   │   ├── juego.py
│   │   ├── actividad.py
│   │   ├── eventos.py
│   │   └── sesion.py
│   ├── schemas/         # Esquemas Pydantic (validación)
│   │   ├── usuario.py
│   │   └── ...
│   ├── routers/         # Endpoints de la API
│   │   └── auth.py
│   ├── utils/           # Utilidades
│   │   ├── security.py  # JWT, autenticación
│   │   └── dependencies.py
│   ├── logging/         # Sistema de logging
│   │   ├── logger.py
│   │   └── middleware.py
│   ├── config.py        # Configuración (Pydantic Settings)
│   ├── database.py      # Conexión a PostgreSQL
│   └── main.py          # Punto de entrada FastAPI
├── logs/                # Logs (solo local)
├── .env                 # Variables de entorno (NO subir a git)
├── .env.example         # Ejemplo de variables
├── requirements.txt     # Dependencias Python
├── Procfile             # Comando de inicio (Railway)
├── railway.json         # Configuración Railway
├── create_tables.py     # Script para crear tablas
├── deploy_local.sh      # Script de despliegue local
├── README.md            # Este archivo
├── RAILWAY_DEPLOY.md    # Guía de despliegue en Railway
└── QUICKSTART.md        # Inicio rápido
```

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

### Crear Usuario de Prueba

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

### Probar Login

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

- **[API_ENDPOINTS.md](API_ENDPOINTS.md)** - 📡 **Guía completa de uso de endpoints** (¡Empieza aquí!)
- **[GerniBide.postman_collection.json](GerniBide.postman_collection.json)** - 📮 **Colección de Postman** - Importa y usa todos los endpoints
- [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) - Guía completa de despliegue en Railway
- [QUICKSTART.md](QUICKSTART.md) - Inicio rápido en 5 pasos
- [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) - Guía detallada de despliegue

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

## 📐 Diagramas

### Arquitectura del Sistema

Diagrama de capas de la arquitectura de GerniBide API, desde la capa cliente hasta la persistencia de datos y servicios externos.

![Diagrama de Arquitectura](diagramas/arquitectura.png)

### Casos de Uso

Diagrama de casos de uso que muestra las interacciones de los distintos actores (Estudiante, Profesor, Administrador) con el sistema.

![Diagrama de Casos de Uso](diagramas/casos_de_uso.png)

### Modelo Entidad-Relación

Diagrama entidad-relación que detalla las tablas de la base de datos (Profesor, Clase, Usuario, Juego, Puntos, Actividad, Actividad Progreso, Asset Log) y sus relaciones.

![Diagrama Entidad-Relación](diagramas/entidad_relacion.png)

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

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

- ✅ **Autenticación JWT** con tokens seguros
- ✅ **Bcrypt nativo** para hash de contraseñas
- ✅ **PostgreSQL** con SQLAlchemy 2.0+
- ✅ **FastAPI** con documentación automática (Swagger + ReDoc)
- ✅ **Logging estructurado** con colores y niveles
- ✅ **Compatible con Railway** (deploy automático)
- ✅ **Pool de conexiones** optimizado
- ✅ **CORS configurable** para apps móviles
- ✅ **Health check** y endpoints de test
- ✅ **Manejo robusto de errores** con mensajes descriptivos
- ✅ **Colección de Postman** lista para importar
- ✅ **Validación automática** con Pydantic schemas

---

**Desarrollado con ❤️ usando FastAPI y PostgreSQL**
