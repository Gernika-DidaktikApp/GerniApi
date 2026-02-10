# 📡 Guía de Endpoints - GerniBide API

Esta guía te ayudará a integrar la API de GerniBide en tu aplicación móvil o web.

## 🌐 URL Base

### Producción (Railway)
```
https://tu-dominio.up.railway.app
```

### Desarrollo Local
```
http://localhost:8000
```

---

## 🔑 Sistema de Autenticación

La API utiliza un sistema de autenticación dual:

| Tipo | Descripción | Header |
|------|-------------|--------|
| **API Key** | Para operaciones administrativas | `X-API-Key: <tu_api_key>` |
| **JWT Token** | Para operaciones de usuario | `Authorization: Bearer <token>` |

### Leyenda de Permisos
- 🔓 **Público**: No requiere autenticación
- 🔑 **API Key**: Requiere API Key (operaciones administrativas)
- 🎫 **Token**: Requiere Token JWT (operaciones de usuario)
- 🔑🎫 **API Key o Token**: Acepta cualquiera de los dos

---

## 📋 Resumen de Endpoints

### Autenticación
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/login-app` | Login de usuario | 🔓 |
| POST | `/api/v1/auth/login-profesor` | Login de profesor | 🔓 |

### Usuarios
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/usuarios` | Registrar usuario | 🔓 |
| GET | `/api/v1/usuarios` | Listar usuarios | 🔑 |
| GET | `/api/v1/usuarios/{id}` | Obtener usuario | 🔑🎫 |
| GET | `/api/v1/usuarios/{id}/estadisticas` | Obtener estadísticas del usuario | 🔑🎫 |
| PUT | `/api/v1/usuarios/{id}` | Actualizar usuario | 🔑🎫 |
| DELETE | `/api/v1/usuarios/{id}` | Eliminar usuario | 🔑 |

### Profesores
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/profesores` | Crear profesor | 🔑 |
| GET | `/api/v1/profesores` | Listar profesores | 🔑 |
| GET | `/api/v1/profesores/{id}` | Obtener profesor | 🔑 |
| PUT | `/api/v1/profesores/{id}` | Actualizar profesor | 🔑 |
| DELETE | `/api/v1/profesores/{id}` | Eliminar profesor | 🔑 |

### Clases
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/clases` | Crear clase | 🔑 |
| GET | `/api/v1/clases` | Listar clases | 🔑 |
| GET | `/api/v1/clases/{id}` | Obtener clase | 🔑 |
| PUT | `/api/v1/clases/{id}` | Actualizar clase | 🔑 |
| DELETE | `/api/v1/clases/{id}` | Eliminar clase | 🔑 |

### Puntos
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/puntos` | Crear punto | 🔑 |
| GET | `/api/v1/puntos` | Listar puntos | 🔑🎫 |
| GET | `/api/v1/puntos/{id}` | Obtener punto | 🔑🎫 |
| PUT | `/api/v1/puntos/{id}` | Actualizar punto | 🔑 |
| DELETE | `/api/v1/puntos/{id}` | Eliminar punto | 🔑 |

### Actividades
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/actividades` | Crear actividad | 🔑 |
| GET | `/api/v1/actividades` | Listar actividades | 🔑🎫 |
| GET | `/api/v1/actividades/{id}` | Obtener actividad | 🔑🎫 |
| GET | `/api/v1/actividades/{id}/respuestas-publicas` | Obtener respuestas públicas (message wall) | 🎫 |
| PUT | `/api/v1/actividades/{id}` | Actualizar actividad | 🔑 |
| DELETE | `/api/v1/actividades/{id}` | Eliminar actividad | 🔑 |

### Partidas
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/partidas/activa/usuario/{id}` | Obtener partida activa del usuario | 🔑🎫 |
| POST | `/api/v1/partidas/activa/usuario/{id}/obtener-o-crear` | Obtener o crear partida activa | 🔑🎫 |
| POST | `/api/v1/partidas` | Crear partida (⚠️ solo una activa por usuario) | 🔑🎫 |
| GET | `/api/v1/partidas` | Listar partidas | 🔑 |
| GET | `/api/v1/partidas/{id}` | Obtener partida | 🔑🎫 |
| PUT | `/api/v1/partidas/{id}` | Actualizar partida | 🔑🎫 |
| DELETE | `/api/v1/partidas/{id}` | Eliminar partida | 🔑 |

### Progreso de Actividades
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/actividad-progreso/iniciar` | Iniciar actividad | 🔑🎫 |
| PUT | `/api/v1/actividad-progreso/{id}/completar` | Completar actividad | 🔑🎫 |
| GET | `/api/v1/actividad-progreso/punto/{id_juego}/{id_punto}/resumen` | Resumen de punto (calculado) | 🔑🎫 |
| POST | `/api/v1/actividad-progreso` | Crear progreso | 🔑🎫 |
| GET | `/api/v1/actividad-progreso` | Listar progresos | 🔑 |
| GET | `/api/v1/actividad-progreso/{id}` | Obtener progreso | 🔑🎫 |
| PUT | `/api/v1/actividad-progreso/{id}` | Actualizar progreso | 🔑🎫 |
| DELETE | `/api/v1/actividad-progreso/{id}` | Eliminar progreso | 🔑 |

### Audit Logs (Solo lectura)
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/audit-logs` | Listar audit logs (con filtros) | 🔑🎫 |
| GET | `/api/v1/audit-logs/{id}` | Obtener audit log | 🔑🎫 |

> **Nota:** Los audit logs se crean automáticamente por el sistema (login, completar actividades, etc.). Son **solo lectura** - no se pueden crear, actualizar ni eliminar manualmente.

---

## 🔐 Autenticación

### POST `/api/v1/auth/login-app`

Autentica un usuario y devuelve un token JWT.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

#### Response

**Status: 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "juan",
  "nombre": "Juan",
  "apellido": "García"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `access_token` | string | Token JWT para autenticación |
| `token_type` | string | Tipo de token (siempre "bearer") |
| `user_id` | string | UUID del usuario (usar para crear partidas) |
| `username` | string | Nombre de usuario |
| `nombre` | string | Nombre del usuario |
| `apellido` | string | Apellido del usuario |

**Status: 401 Unauthorized - Usuario no existe**
```json
{
  "detail": "El usuario no existe"
}
```

**Status: 401 Unauthorized - Contraseña incorrecta**
```json
{
  "detail": "Contraseña incorrecta"
}
```

**Status: 422 Unprocessable Entity**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "username"],
      "msg": "Field required"
    }
  ]
}
```

#### Ejemplos

**curl:**
```bash
curl -X POST "https://tu-api.up.railway.app/api/v1/auth/login-app" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan",
    "password": "password123"
  }'
```

**JavaScript/Fetch:**
```javascript
const response = await fetch('https://tu-api.up.railway.app/api/v1/auth/login-app', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'juan',
    password: 'password123'
  })
});

const data = await response.json();
// Guardar token y user_id
localStorage.setItem('token', data.access_token);
localStorage.setItem('user_id', data.user_id);
console.log('Bienvenido', data.nombre);
```

**Kotlin/Android (Ktor):**
```kotlin
val client = HttpClient()
val response: HttpResponse = client.post("$baseUrl/api/v1/auth/login-app") {
    contentType(ContentType.Application.Json)
    setBody(mapOf(
        "username" to "juan",
        "password" to "password123"
    ))
}
val token = response.body<TokenResponse>()
```

**Flutter/Dart:**
```dart
final response = await http.post(
  Uri.parse('$baseUrl/api/v1/auth/login-app'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'username': 'juan',
    'password': 'password123'
  }),
);

if (response.statusCode == 200) {
  final data = jsonDecode(response.body);
  final token = data['access_token'];
}
```

**Python/Requests:**
```python
import requests

response = requests.post(
    'https://tu-api.up.railway.app/api/v1/auth/login-app',
    json={
        'username': 'juan',
        'password': 'password123'
    }
)

if response.status_code == 200:
    token = response.json()['access_token']
```

---

### POST `/api/v1/auth/login-profesor`

Autentica un profesor y devuelve un token JWT para acceso a la interfaz web.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

#### Response

**Status: 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status: 401 Unauthorized**
```json
{
  "detail": "Username o contraseña incorrectos"
}
```

#### Ejemplos

**curl:**
```bash
curl -X POST "https://tu-api.up.railway.app/api/v1/auth/login-profesor" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "profesor1",
    "password": "password123"
  }'
```

**JavaScript/Fetch:**
```javascript
const response = await fetch('https://tu-api.up.railway.app/api/v1/auth/login-profesor', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'profesor1',
    password: 'password123'
  })
});

const data = await response.json();
console.log(data.access_token);
```

> **Nota:** El token del profesor incluye el campo `type: "profesor"` en el payload JWT para diferenciarlo de los tokens de usuario.

---

## 🏥 Health Check

### GET `/health`

Verifica que la API está funcionando correctamente.

#### Request

**Headers:** Ninguno requerido

#### Response

**Status: 200 OK**
```json
{
  "status": "healthy"
}
```

#### Ejemplos

**curl:**
```bash
curl https://tu-api.up.railway.app/health
```

**JavaScript:**
```javascript
const response = await fetch('https://tu-api.up.railway.app/health');
const data = await response.json();
console.log(data.status); // "healthy"
```

---

## 👥 Usuarios

### POST `/api/v1/usuarios` (Registro)

Registra un nuevo usuario en el sistema. **Endpoint público** - no requiere autenticación.

Puedes asignar al usuario a una clase usando **código de clase** (6 caracteres, ej: `A3X9K2`) o UUID.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "username": "string",
  "nombre": "string",
  "apellido": "string",
  "password": "string",
  "codigo_clase": "string (opcional, 6 chars)",
  "id_clase": "uuid (opcional)"
}
```

| Campo | Tipo | Requerido | Validación |
|-------|------|-----------|------------|
| `username` | string | sí | 3-45 caracteres, único |
| `nombre` | string | sí | 1-45 caracteres |
| `apellido` | string | sí | 1-45 caracteres |
| `password` | string | sí | 4-100 caracteres |
| `codigo_clase` | string | no | 6 caracteres (ej: A3X9K2) |
| `id_clase` | string | no | UUID de clase existente |

> **Nota:** Si se proporciona `codigo_clase`, tiene prioridad sobre `id_clase`. Esto facilita el registro de estudiantes que solo necesitan ingresar 6 caracteres en vez de un UUID largo.

#### Response

**Status: 201 Created**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "juan",
  "nombre": "Juan",
  "apellido": "García",
  "id_clase": null,
  "creation": "2026-01-23T10:30:00",
  "top_score": 0
}
```

**Status: 400 Bad Request**
```json
{
  "detail": "El username ya está en uso"
}
```

**Status: 422 Unprocessable Entity**
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "String should have at least 3 characters",
      "type": "string_too_short"
    }
  ]
}
```

#### Ejemplos

**curl (sin clase):**
```bash
curl -X POST "https://tu-api.up.railway.app/api/v1/usuarios" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevo_usuario",
    "nombre": "Juan",
    "apellido": "García",
    "password": "password123"
  }'
```

**curl (con código de clase):**
```bash
curl -X POST "https://tu-api.up.railway.app/api/v1/usuarios" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevo_usuario",
    "nombre": "Juan",
    "apellido": "García",
    "password": "password123",
    "codigo_clase": "A3X9K2"
  }'
```

**JavaScript/Fetch:**
```javascript
// Registro sin clase
const response = await fetch('https://tu-api.up.railway.app/api/v1/usuarios', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'nuevo_usuario',
    nombre: 'Juan',
    apellido: 'García',
    password: 'password123'
  })
});

// Registro con código de clase (más fácil para estudiantes)
const response = await fetch('https://tu-api.up.railway.app/api/v1/usuarios', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'estudiante1',
    nombre: 'María',
    apellido: 'López',
    password: 'password123',
    codigo_clase: 'A3X9K2'  // Código proporcionado por el profesor
  })
});

if (response.status === 201) {
  const usuario = await response.json();
  console.log('Usuario creado:', usuario.id);
  console.log('Asignado a clase:', usuario.id_clase);
}
```

**Kotlin/Android:**
```kotlin
val response = client.post("$baseUrl/api/v1/usuarios") {
    contentType(ContentType.Application.Json)
    setBody(mapOf(
        "username" to "nuevo_usuario",
        "nombre" to "Juan",
        "apellido" to "García",
        "password" to "password123"
    ))
}
val usuario = response.body<UsuarioResponse>()
```

---

### GET `/api/v1/usuarios`

Obtiene lista paginada de usuarios. **Requiere API Key.**

#### Query Parameters

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Registros a saltar |
| `limit` | int | 100 | Máximo de registros (max: 1000) |

#### Ejemplo

```bash
curl -X GET "https://tu-api.up.railway.app/api/v1/usuarios?skip=0&limit=10" \
  -H "X-API-Key: <tu_api_key>"
```

---

### GET `/api/v1/usuarios/{usuario_id}`

Obtiene un usuario por ID. **Requiere API Key o Token.**

- Con API Key: Puede ver cualquier usuario
- Con Token: Solo puede ver su propio perfil

---

### GET `/api/v1/usuarios/{usuario_id}/estadisticas`

Obtiene estadísticas detalladas del usuario para mostrar en el perfil de la app móvil. **Requiere API Key o Token.**

- Con API Key: Puede ver estadísticas de cualquier usuario
- Con Token: Solo puede ver sus propias estadísticas

#### Response

**Status: 200 OK**
```json
{
  "actividades_completadas": 12,
  "racha_dias": 5,
  "modulos_completados": [
    "Árbol del Gernika",
    "Museo de la Paz",
    "Plaza"
  ],
  "ultima_partida": "2026-01-20T15:30:00",
  "total_puntos_acumulados": 1850.5
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `actividades_completadas` | int | Número de actividades completadas |
| `racha_dias` | int | Días consecutivos de juego (desde hoy hacia atrás) |
| `modulos_completados` | string[] | Nombres de puntos completados |
| `ultima_partida` | datetime? | Fecha de la última partida jugada (null si no ha jugado) |
| `total_puntos_acumulados` | float | Suma de todos los puntos obtenidos |

#### Ejemplos

**curl con API Key:**
```bash
curl -X GET "https://tu-api.up.railway.app/api/v1/usuarios/{usuario_id}/estadisticas" \
  -H "X-API-Key: <tu_api_key>"
```

**curl con Token (usuario autenticado):**
```bash
curl -X GET "https://tu-api.up.railway.app/api/v1/usuarios/{usuario_id}/estadisticas" \
  -H "Authorization: Bearer <token_jwt>"
```

**Kotlin/Android (con Token JWT):**
```kotlin
// En tu ApiService
@GET("api/v1/usuarios/{usuario_id}/estadisticas")
suspend fun obtenerEstadisticasUsuario(
    @Path("usuario_id") usuarioId: String,
    @Header("Authorization") token: String
): UsuarioStatsResponse

// Uso en ProfileActivity
val stats = apiService.obtenerEstadisticasUsuario(
    usuarioId = userId,
    token = "Bearer $authToken"
)

// Actualizar UI
tvActivitiesCompleted.text = stats.actividadesCompletadas.toString()
tvStreak.text = stats.rachaDias.toString()

// Desbloquear logros por módulo
stats.modulosCompletados.forEach { modulo ->
    when (modulo) {
        "Árbol del Gernika" -> unlockAchievement(ivArbol)
        "Museo de la Paz" -> unlockAchievement(ivBunkers)
        "Plaza" -> unlockAchievement(ivPlaza)
        // etc...
    }
}
```

**JavaScript/Fetch:**
```javascript
const response = await fetch(`${baseUrl}/api/v1/usuarios/${userId}/estadisticas`, {
  headers: {
    'Authorization': `Bearer ${authToken}`
  }
});

const stats = await response.json();
console.log('Actividades completadas:', stats.actividades_completadas);
console.log('Racha de días:', stats.racha_dias);
```

---

### PUT `/api/v1/usuarios/{usuario_id}`

Actualiza un usuario. **Requiere API Key o Token.**

- Con API Key: Puede actualizar cualquier usuario
- Con Token: Solo puede actualizar su propio perfil

**Body (todos los campos son opcionales):**
```json
{
  "username": "string",
  "nombre": "string",
  "apellido": "string",
  "password": "string",
  "id_clase": "uuid"
}
```

---

### DELETE `/api/v1/usuarios/{usuario_id}`

Elimina un usuario. **Requiere API Key.**

**Response: 204 No Content**

---

## 👨‍🏫 Profesores

Todos los endpoints de profesores **requieren API Key**.

### POST `/api/v1/profesores`

Crea un nuevo profesor.

**Body:**
```json
{
  "username": "string",
  "nombre": "string",
  "apellido": "string",
  "password": "string"
}
```

**Response: 201 Created**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "profesor1",
  "nombre": "María",
  "apellido": "López"
}
```

---

### GET `/api/v1/profesores`

Lista todos los profesores con paginación.

---

### GET `/api/v1/profesores/{profesor_id}`

Obtiene un profesor por ID.

---

### PUT `/api/v1/profesores/{profesor_id}`

Actualiza un profesor.

---

### DELETE `/api/v1/profesores/{profesor_id}`

Elimina un profesor. **Response: 204 No Content**

---

## 🏫 Clases

Todos los endpoints de clases **requieren API Key**.

### POST `/api/v1/clases`

Crea una nueva clase y genera automáticamente un **código compartible** de 6 caracteres (ej: `A3X9K2`).

Este código facilita que los estudiantes se registren sin necesitar el UUID largo.

**Body:**
```json
{
  "nombre": "string",
  "id_profesor": "uuid"
}
```

**Response: 201 Created**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "codigo": "A3X9K2",
  "nombre": "4º ESO A",
  "id_profesor": "uuid-del-profesor"
}
```

> **Nota:** El campo `codigo` se genera automáticamente evitando caracteres ambiguos (0/O, 1/I/l) para facilitar su escritura.

---

### GET `/api/v1/clases`

Lista todas las clases.

---

### GET `/api/v1/clases/{clase_id}`

Obtiene una clase por ID.

---

### PUT `/api/v1/clases/{clase_id}`

Actualiza una clase.

---

### DELETE `/api/v1/clases/{clase_id}`

Elimina una clase. **Response: 204 No Content**

---

## 📍 Puntos

### POST `/api/v1/puntos`

Crea un nuevo punto. **Requiere API Key.**

**Body:**
```json
{
  "nombre": "string"
}
```

**Response: 201 Created**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Punto 1 - Introducción"
}
```

---

### GET `/api/v1/puntos`

Lista todos los puntos. **Requiere API Key o Token.**

---

### GET `/api/v1/puntos/{punto_id}`

Obtiene un punto por ID. **Requiere API Key o Token.**

---

### PUT `/api/v1/puntos/{punto_id}`

Actualiza un punto. **Requiere API Key.**

---

### DELETE `/api/v1/puntos/{punto_id}`

Elimina un punto. **Requiere API Key.** **Response: 204 No Content**

---

## 📝 Actividades

Las actividades son sub-elementos dentro de cada punto.

### POST `/api/v1/actividades`

Crea una nueva actividad. **Requiere API Key.**

#### Request

**Body:**
```json
{
  "nombre": "string",
  "id_punto": "uuid"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `nombre` | string | ✅ | Nombre de la actividad (1-100 caracteres) |
| `id_punto` | uuid | ✅ | ID del punto padre |

#### Response

**Status: 201 Created**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Inicio del nivel",
  "id_punto": "uuid-punto"
}
```

#### Ejemplos

**curl:**
```bash
curl -X POST "https://tu-api.up.railway.app/api/v1/actividades" \
  -H "X-API-Key: <tu_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Inicio del nivel",
    "id_punto": "uuid-punto"
  }'
```

---

### GET `/api/v1/actividades`

Lista todas las actividades. **Requiere API Key o Token.**

#### Query Parameters

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Registros a saltar (paginación) |
| `limit` | int | 100 | Máximo de registros a retornar |

#### Response

**Status: 200 OK**
```json
[
  {
    "id": "uuid-1",
    "nombre": "Inicio",
    "id_punto": "uuid-punto"
  },
  {
    "id": "uuid-2",
    "nombre": "Mensaje",
    "id_punto": "uuid-punto"
  }
]
```

---

### GET `/api/v1/actividades/{actividad_id}`

Obtiene una actividad específica por ID. **Requiere API Key o Token.**

#### Response

**Status: 200 OK**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Medalla de oro",
  "id_punto": "uuid-punto"
}
```

---

### PUT `/api/v1/actividades/{actividad_id}`

Actualiza una actividad existente. **Requiere API Key o Token de usuario.**

**Body (todos los campos son opcionales):**
```json
{
  "id_punto": "uuid-del-punto",
  "nombre": "Nuevo nombre de la actividad"
}
```

**Response: 200 OK**
```json
{
  "id": "uuid-de-la-actividad",
  "id_punto": "uuid-del-punto",
  "nombre": "Nuevo nombre de la actividad"
}
```

**Ejemplos:**

**curl:**
```bash
curl -X PUT "https://tu-api.up.railway.app/api/v1/actividades/{actividad_id}" \
  -H "X-API-Key: tu-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Actividad actualizada"
  }'
```

**JavaScript:**
```javascript
const response = await fetch(`${API_BASE_URL}/api/v1/actividades/${actividadId}`, {
  method: 'PUT',
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    nombre: 'Actividad actualizada'
  })
});
```

---

### DELETE `/api/v1/actividades/{actividad_id}`

Elimina una actividad. **Requiere API Key.**

**Response: 204 No Content**

---

### GET `/api/v1/actividades/{actividad_id}/respuestas-publicas`

Obtiene respuestas públicas de estudiantes que completaron una actividad específica. **Requiere autenticación JWT.**

Ideal para crear "muros de mensajes" o galerías comunitarias donde los estudiantes pueden ver las respuestas de otros compañeros.

#### Query Parameters

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `limit` | int | 20 | Máximo de respuestas a retornar (max: 100) |

#### Response

**Status: 200 OK**
```json
{
  "actividad_id": "9a5bbb72-827a-4b7e-bd3b-1e010dff191b",
  "actividad_nombre": "Mi mensaje para el mundo",
  "total_respuestas": 4,
  "respuestas": [
    {
      "mensaje": "Hola desde Gernika!",
      "fecha": "2026-02-10T01:35:08.272533",
      "usuario": "Julieta"
    },
    {
      "mensaje": "La paz es importante",
      "fecha": "2026-02-10T01:27:39.923924",
      "usuario": "Pablo"
    }
  ]
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `actividad_id` | string | UUID de la actividad |
| `actividad_nombre` | string | Nombre de la actividad |
| `total_respuestas` | int | Número total de respuestas públicas |
| `respuestas` | array | Lista de respuestas (ordenadas por fecha desc) |
| `respuestas[].mensaje` | string | Contenido de la respuesta del estudiante |
| `respuestas[].fecha` | datetime | Fecha de completado |
| `respuestas[].usuario` | string | Nombre del estudiante (opcional) |

**Status: 404 Not Found**
```json
{
  "success": false,
  "error": {
    "code": 404,
    "message": "Actividad no encontrada",
    "type": "http_error"
  }
}
```

**Status: 401 Unauthorized** (sin token)
```json
{
  "success": false,
  "error": {
    "code": 401,
    "message": "Autenticación requerida",
    "type": "http_error"
  }
}
```

#### Ejemplos

**curl:**
```bash
curl -X GET "https://gernibide.up.railway.app/api/v1/actividades/9a5bbb72.../respuestas-publicas?limit=10" \
  -H "Authorization: Bearer <token>"
```

**JavaScript:**
```javascript
const response = await fetch(
  `${API_URL}/api/v1/actividades/${actividadId}/respuestas-publicas?limit=20`,
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);

const data = await response.json();
console.log(`${data.total_respuestas} mensajes públicos`);
data.respuestas.forEach(r => {
  console.log(`${r.usuario}: ${r.mensaje}`);
});
```

**Flutter:**
```dart
final response = await http.get(
  Uri.parse('$baseUrl/api/v1/actividades/$actividadId/respuestas-publicas?limit=20'),
  headers: {'Authorization': 'Bearer $token'},
);

if (response.statusCode == 200) {
  final data = jsonDecode(response.body);
  for (var respuesta in data['respuestas']) {
    print('${respuesta['usuario']}: ${respuesta['mensaje']}');
  }
}
```

**Caso de uso típico:**
1. Usuario completa actividad "Mi mensaje para el mundo" escribiendo un mensaje
2. El mensaje se guarda en el campo `respuesta_contenido` de ActividadProgreso
3. Otros usuarios llaman a este endpoint para ver todos los mensajes públicos
4. Se muestra un "muro de mensajes" con las contribuciones de la comunidad

---

## 🎮 Partidas

Las partidas representan sesiones de juego de un usuario.

### GET `/api/v1/partidas/activa/usuario/{usuario_id}`

Obtiene la partida activa del usuario. **Requiere API Key o Token.**

- Con API Key: Puede ver la partida activa de cualquier usuario
- Con Token: Solo puede ver su propia partida activa

**Response: 200 OK**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "id_usuario": "uuid-del-usuario",
  "fecha_inicio": "2026-01-23T10:30:00",
  "fecha_fin": null,
  "duracion": null,
  "estado": "en_progreso"
}
```

**Response: 404 Not Found** (si no hay partida activa)
```json
{
  "detail": "El usuario no tiene una partida activa"
}
```

---

### POST `/api/v1/partidas/activa/usuario/{usuario_id}/obtener-o-crear`

Obtiene la partida activa del usuario, o crea una nueva si no existe. **Requiere API Key o Token.**

Este es el endpoint **RECOMENDADO** para la app móvil, ya que simplifica la lógica:
- Si existe una partida activa, la retorna
- Si no existe, crea una automáticamente

**Response: 200 OK**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "id_usuario": "uuid-del-usuario",
  "fecha_inicio": "2026-01-23T10:30:00",
  "fecha_fin": null,
  "duracion": null,
  "estado": "en_progreso"
}
```

---

### POST `/api/v1/partidas`

Crea una nueva partida. **Requiere API Key o Token.**

- Con API Key: Puede crear partidas para cualquier usuario
- Con Token: Solo puede crear partidas para sí mismo

**⚠️ RESTRICCIÓN IMPORTANTE:** Un usuario solo puede tener **una partida activa** a la vez.
Si el usuario ya tiene una partida con estado "en_progreso", este endpoint retornará error 400.

**Recomendación:** Usa `/partidas/activa/usuario/{id}/obtener-o-crear` en su lugar.

**Body:**
```json
{
  "id_usuario": "uuid"
}
```

**Response: 201 Created**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "id_usuario": "uuid-del-usuario",
  "fecha_inicio": "2026-01-23T10:30:00",
  "fecha_fin": null,
  "duracion": null,
  "estado": "en_progreso"
}
```

**Response: 400 Bad Request** (si ya hay partida activa)
```json
{
  "detail": "El usuario ya tiene una partida activa (ID: 550e8400-...). Debe finalizarla antes de crear una nueva."
}
```

---

### GET `/api/v1/partidas`

Lista todas las partidas. **Requiere API Key.**

---

### GET `/api/v1/partidas/{partida_id}`

Obtiene una partida por ID. **Requiere API Key o Token.**

- Con API Key: Puede ver cualquier partida
- Con Token: Solo puede ver sus propias partidas

---

### PUT `/api/v1/partidas/{partida_id}`

Actualiza una partida. **Requiere API Key o Token.**

---

### DELETE `/api/v1/partidas/{partida_id}`

Elimina una partida. **Requiere API Key.** **Response: 204 No Content**

---

## 📊 Progreso de Actividades

El sistema de gestión de progreso permite rastrear el progreso de las actividades de los jugadores, calculando automáticamente tiempos y puntuaciones.

### Flujo de Trabajo Simplificado

1. **Jugador inicia actividad** → POST `/api/v1/actividad-progreso/iniciar`
2. **Jugador completa actividad** → PUT `/api/v1/actividad-progreso/{id}/completar`
3. **Consultar resumen de punto** → GET `/api/v1/actividad-progreso/punto/{id_juego}/{id_punto}/resumen`

> **Nota:** El resumen de punto (puntuación total, estado, duración) se calcula automáticamente desde las actividades.

---

### POST `/api/v1/actividad-progreso/iniciar`

Inicia una actividad dentro de un punto. Registra automáticamente la fecha de inicio.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "id_juego": "uuid-de-la-partida",
  "id_punto": "uuid-del-punto",
  "id_actividad": "uuid-de-la-actividad"
}
```

#### Response

**Status: 201 Created**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "id_juego": "uuid-de-la-partida",
  "id_punto": "uuid-del-punto",
  "id_actividad": "uuid-de-la-actividad",
  "fecha_inicio": "2026-01-18T10:35:00",
  "duracion": null,
  "fecha_fin": null,
  "estado": "en_progreso",
  "puntuacion": null,
  "respuesta_contenido": null
}
```

**Status: 400 Bad Request**
```json
{
  "detail": "Ya existe una actividad en progreso para este juego y actividad"
}
```

**Status: 404 Not Found**
```json
{
  "detail": "La actividad especificada no existe o no pertenece a este punto"
}
```

#### Ejemplos

**curl:**
```bash
curl -X POST "https://tu-api.up.railway.app/api/v1/actividad-progreso/iniciar" \
  -H "Content-Type: application/json" \
  -d '{
    "id_juego": "uuid-partida",
    "id_punto": "uuid-punto",
    "id_actividad": "uuid-actividad"
  }'
```

**JavaScript:**
```javascript
const response = await fetch(`${API_BASE_URL}/api/v1/actividad-progreso/iniciar`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    id_juego: partidaId,
    id_punto: puntoId,
    id_actividad: actividadId
  })
});

const actividadProgreso = await response.json();
// Guardar el ID para completar después
localStorage.setItem('actividad_progreso_id', actividadProgreso.id);
```

**Flutter:**
```dart
final response = await http.post(
  Uri.parse('$baseUrl/api/v1/actividad-progreso/iniciar'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'id_juego': partidaId,
    'id_punto': puntoId,
    'id_actividad': actividadId
  }),
);

if (response.statusCode == 201) {
  final actividadProgreso = jsonDecode(response.body);
  // Guardar ID para completar después
  await prefs.setString('actividad_progreso_id', actividadProgreso['id']);
}
```

---

### PUT `/api/v1/actividad-progreso/{progreso_id}/completar`

Completa una actividad y registra su puntuación. **Calcula automáticamente**:
- Duración de la actividad (fecha_fin - fecha_inicio)
- Actualiza el estado a "completado"

#### Request

**Headers:**
```
Content-Type: application/json
```

**URL Parameters:**
- `progreso_id`: UUID del progreso de la actividad (obtenido al iniciar la actividad)

**Body:**
```json
{
  "puntuacion": 85.5,
  "respuesta_contenido": "string (opcional) - Texto o URL de la respuesta del usuario",
  "device_type": "string (opcional) - Tipo de dispositivo (ej: iOS, Android)",
  "app_version": "string (opcional) - Versión de la aplicación (ej: 1.0.0)"
}
```

#### Response

**Status: 200 OK**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "id_juego": "uuid-de-la-partida",
  "id_punto": "uuid-del-punto",
  "id_actividad": "uuid-de-la-actividad",
  "fecha_inicio": "2026-01-18T10:35:00",
  "fecha_fin": "2026-01-18T10:40:30",
  "duracion": 330,
  "estado": "completado",
  "puntuacion": 85.5,
  "respuesta_contenido": "Respuesta del usuario"
}
```

**Status: 400 Bad Request**
```json
{
  "detail": "La actividad no está en progreso. Estado actual: completado"
}
```

**Status: 404 Not Found**
```json
{
  "detail": "Progreso de actividad no encontrado"
}
```

#### Ejemplos

**curl:**
```bash
# Completar actividad con puntuación
curl -X PUT "https://tu-api.up.railway.app/api/v1/actividad-progreso/660e8400.../completar" \
  -H "Content-Type: application/json" \
  -d '{
    "puntuacion": 85.5,
    "respuesta_contenido": "Respuesta del usuario"
  }'
```

**JavaScript:**
```javascript
// Completar actividad
const actividadProgresoId = localStorage.getItem('actividad_progreso_id');

const response = await fetch(
  `${API_BASE_URL}/api/v1/actividad-progreso/${actividadProgresoId}/completar`,
  {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      puntuacion: playerScore,
      respuesta_contenido: userAnswer
    })
  }
);

const actividadCompletada = await response.json();
console.log('Actividad completada con', actividadCompletada.puntuacion, 'puntos');
console.log('Duración:', actividadCompletada.duracion, 'segundos');
```

**Kotlin:**
```kotlin
val actividadProgresoId = prefs.getString("actividad_progreso_id", "")

val response = client.put("$baseUrl/api/v1/actividad-progreso/$actividadProgresoId/completar") {
    contentType(ContentType.Application.Json)
    setBody(mapOf(
        "puntuacion" to 85.5,
        "respuesta_contenido" to "Respuesta del usuario"
    ))
}

val actividadCompletada = response.body<ActividadProgresoResponse>()
println("Duración: ${actividadCompletada.duracion} segundos")
```

**Flutter:**
```dart
final actividadProgresoId = await prefs.getString('actividad_progreso_id');

final response = await http.put(
  Uri.parse('$baseUrl/api/v1/actividad-progreso/$actividadProgresoId/completar'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'puntuacion': playerScore,
    'respuesta_contenido': userAnswer
  }),
);

if (response.statusCode == 200) {
  final actividad = jsonDecode(response.body);
  print('Actividad completada: ${actividad['puntuacion']} puntos');
  print('Duración: ${actividad['duracion']} segundos');
}
```

---

### GET `/api/v1/actividad-progreso/punto/{id_juego}/{id_punto}/resumen`

Obtiene el resumen calculado de un punto basado en las actividades completadas.

#### URL Parameters
- `id_juego`: UUID de la partida
- `id_punto`: UUID del punto

#### Response

**Status: 200 OK**
```json
{
  "id_juego": "uuid-de-la-partida",
  "id_punto": "uuid-del-punto",
  "nombre_punto": "Bunkers",
  "actividades_totales": 5,
  "actividades_completadas": 3,
  "actividades_en_progreso": 1,
  "puntuacion_total": 256.5,
  "duracion_total": 450,
  "fecha_inicio": "2026-01-18T10:30:00",
  "fecha_fin": null,
  "estado": "en_progreso"
}
```

| Campo | Descripción |
|-------|-------------|
| `actividades_totales` | Total de actividades en el punto |
| `actividades_completadas` | Actividades ya completadas |
| `puntuacion_total` | Suma de puntuaciones de actividades completadas |
| `duracion_total` | Suma de duraciones en segundos |
| `estado` | "no_iniciada", "en_progreso" o "completada" |

#### Ejemplos

**curl:**
```bash
curl -X GET "https://tu-api.up.railway.app/api/v1/actividad-progreso/punto/{id_juego}/{id_punto}/resumen" \
  -H "Authorization: Bearer <token>"
```

**JavaScript:**
```javascript
const resumen = await fetch(
  `${API_BASE_URL}/api/v1/actividad-progreso/punto/${partidaId}/${puntoId}/resumen`,
  { headers: { 'Authorization': `Bearer ${token}` } }
).then(r => r.json());

console.log('Estado:', resumen.estado);
console.log('Puntuación:', resumen.puntuacion_total);
```

---

### PUT `/api/v1/actividad-progreso/{progreso_id}`

Actualiza un progreso de actividad existente.

**⚠️ RESTRICCIÓN IMPORTANTE:** Solo se puede actualizar `respuesta_contenido` cuando la actividad está **completada**.

#### Request

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <token>
```

**URL Parameters:**
- `progreso_id`: UUID del progreso de la actividad

**Body (todos los campos son opcionales):**
```json
{
  "duracion": 120,
  "fecha_fin": "2026-02-07T15:30:00",
  "estado": "completado",
  "puntuacion": 9.0,
  "respuesta_contenido": "Solo se puede actualizar si estado=completado"
}
```

#### Response

**Status: 200 OK**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "id_juego": "uuid-de-la-partida",
  "id_punto": "uuid-del-punto",
  "id_actividad": "uuid-de-la-actividad",
  "fecha_inicio": "2026-01-18T10:35:00",
  "fecha_fin": "2026-01-18T10:40:30",
  "duracion": 120,
  "estado": "completado",
  "puntuacion": 9.0,
  "respuesta_contenido": "Respuesta actualizada"
}
```

**Status: 400 Bad Request** (intentando actualizar respuesta_contenido sin estar completada)
```json
{
  "detail": "Solo se puede actualizar respuesta_contenido cuando la actividad está completada"
}
```

#### Ejemplos

**JavaScript - Actualizar respuesta después de completar:**
```javascript
// Primero completar la actividad
await fetch(`${API_URL}/actividad-progreso/${id}/completar`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    puntuacion: 8.5,
    respuesta_contenido: "Respuesta inicial"
  })
});

// Luego actualizar la respuesta (solo funciona si está completada)
await fetch(`${API_URL}/actividad-progreso/${id}`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    respuesta_contenido: "Respuesta corregida o mejorada"
  })
});
```

**curl - Actualizar puntuación:**
```bash
curl -X PUT "https://tu-api.up.railway.app/api/v1/actividad-progreso/660e8400.../
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"puntuacion": 9.5}'
```

---

### Ejemplo de Flujo Completo

```javascript
// 0. Obtener user_id del login guardado
const userId = localStorage.getItem('user_id');
const token = localStorage.getItem('token');

// 1. Iniciar partida (usando user_id del login)
const partidaResponse = await fetch(`${API_BASE_URL}/api/v1/partidas`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({ id_usuario: userId })
});
const { id: partidaId } = await partidaResponse.json();

// 2. Para cada actividad del punto
for (const actividadId of actividadesIds) {
  // 2a. Iniciar actividad
  const actividadInicioResponse = await fetch(
    `${API_BASE_URL}/api/v1/actividad-progreso/iniciar`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        id_juego: partidaId,
        id_punto: puntoId,
        id_actividad: actividadId
      })
    }
  );
  const { id: actividadProgresoId } = await actividadInicioResponse.json();

  // 2b. Jugador completa la actividad
  // ... lógica del juego ...

  // 2c. Completar actividad con puntuación
  await fetch(
    `${API_BASE_URL}/api/v1/actividad-progreso/${actividadProgresoId}/completar`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        puntuacion: score,
        respuesta_contenido: userAnswer
      })
    }
  );
}

// 3. Obtener resumen del punto
const resumen = await fetch(
  `${API_BASE_URL}/api/v1/actividad-progreso/punto/${partidaId}/${puntoId}/resumen`,
  { headers: { 'Authorization': `Bearer ${token}` } }
).then(r => r.json());

console.log('Punto:', resumen.estado);
console.log('Puntuación total:', resumen.puntuacion_total);
console.log('Tiempo total:', resumen.duracion_total, 'segundos');
```

---

### POST `/api/v1/actividad-progreso/punto/{id_juego}/{id_punto}/reset`

Resetea un punto completado para permitir que el usuario lo repita desde cero.

Este endpoint elimina todos los progreso de actividades del punto especificado para la partida dada, permitiendo al usuario volver a iniciar y completar las actividades como si nunca las hubiera hecho.

**Autenticación:**
- Con API Key: Puede resetear puntos de cualquier partida
- Con Token: Solo puede resetear puntos de sus propias partidas

#### URL Parameters
- `id_juego`: UUID de la partida
- `id_punto`: UUID del punto a resetear

#### Response

**Status: 200 OK**
```json
{
  "mensaje": "Punto reseteado exitosamente",
  "id_juego": "uuid-de-la-partida",
  "id_punto": "uuid-del-punto",
  "actividades_reseteadas": 5
}
```

**Status: 404 Not Found**
```json
{
  "detail": "No hay progreso de actividades para este punto en esta partida"
}
```

o

```json
{
  "detail": "Punto no encontrado"
}
```

#### Ejemplos

**curl:**
```bash
curl -X POST "https://tu-api.up.railway.app/api/v1/actividad-progreso/punto/{id_juego}/{id_punto}/reset" \
  -H "Authorization: Bearer <token>"
```

**JavaScript:**
```javascript
const response = await fetch(
  `${API_BASE_URL}/api/v1/actividad-progreso/punto/${partidaId}/${puntoId}/reset`,
  {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  }
);

const result = await response.json();
console.log(`Punto reseteado: ${result.actividades_reseteadas} actividades eliminadas`);
// Ahora el usuario puede volver a iniciar las actividades desde cero
```

**Flutter:**
```dart
final response = await http.post(
  Uri.parse('$baseUrl/api/v1/actividad-progreso/punto/$partidaId/$puntoId/reset'),
  headers: {'Authorization': 'Bearer $token'},
);

if (response.statusCode == 200) {
  final result = jsonDecode(response.body);
  print('Punto reseteado: ${result['actividades_reseteadas']} actividades');
  // Volver a la pantalla inicial del punto
  Navigator.pushReplacement(context, PuntoScreen(puntoId));
}
```

**Uso típico:**
1. Usuario completa un punto
2. Usuario quiere repetir el punto para mejorar su puntuación
3. Se llama a este endpoint para resetear todas las actividades
4. Usuario puede volver a llamar `/iniciar` para cada actividad y jugar de nuevo

---

## 📚 Documentación Interactiva

### GET `/docs`

Accede a la documentación interactiva de Swagger UI.

**URL:** `https://tu-api.up.railway.app/docs`

Esta interfaz te permite:
- Ver todos los endpoints disponibles
- Probar endpoints directamente desde el navegador
- Ver schemas de request/response
- Copiar ejemplos de código

---

## 🔑 Usando el Token JWT

Una vez que obtengas el token del login, debes incluirlo en las peticiones protegidas.

### Header de Autorización

```
Authorization: Bearer <tu_access_token>
```

### Ejemplos con Token

**curl:**
```bash
curl -X GET "https://tu-api.up.railway.app/api/v1/protected-endpoint" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**JavaScript:**
```javascript
const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';

const response = await fetch('https://tu-api.up.railway.app/api/v1/protected-endpoint', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

**Kotlin:**
```kotlin
client.get("$baseUrl/api/v1/protected-endpoint") {
    bearerAuth(token)
}
```

**Flutter:**
```dart
final response = await http.get(
  Uri.parse('$baseUrl/api/v1/protected-endpoint'),
  headers: {
    'Authorization': 'Bearer $token'
  },
);
```

---

## ⚠️ Manejo de Errores

### Códigos de Estado HTTP

| Código | Significado | Acción |
|--------|-------------|--------|
| 200 | OK | Petición exitosa |
| 401 | Unauthorized | Credenciales inválidas o token expirado |
| 422 | Unprocessable Entity | Datos de entrada inválidos |
| 404 | Not Found | Endpoint no existe |
| 500 | Internal Server Error | Error del servidor |

### Formato de Error

```json
{
  "detail": "Descripción del error"
}
```

### Validación de Datos (422)

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "username"],
      "msg": "Field required"
    }
  ]
}
```

### Ejemplo de Manejo de Errores

**JavaScript:**
```javascript
try {
  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.json();
    console.error(`Error ${response.status}:`, error.detail);

    if (response.status === 401) {
      // Token expirado o inválido - redirigir al login
      redirectToLogin();
    }
  }

  const data = await response.json();
  return data;
} catch (error) {
  console.error('Network error:', error);
}
```

**Kotlin:**
```kotlin
try {
    val response = client.post(url) { ... }
    // Procesar respuesta exitosa
} catch (e: ClientRequestException) {
    when (e.response.status.value) {
        401 -> {
            // Token expirado - redirigir al login
        }
        422 -> {
            // Datos inválidos
            val error = e.response.body<ErrorResponse>()
            println(error.detail)
        }
    }
}
```

---

## 🔄 Flujo de Autenticación Completo

### 0. Registro (si es nuevo usuario)

```javascript
async function register(username, nombre, apellido, password) {
  const response = await fetch(`${API_BASE_URL}/api/v1/usuarios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, nombre, apellido, password })
  });

  if (response.status === 201) {
    const usuario = await response.json();
    console.log('Usuario creado:', usuario.id);
    return usuario;
  }

  const error = await response.json();
  throw new Error(error.detail);
}
```

### 1. Login

```javascript
async function login(username, password) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login-app`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  if (response.ok) {
    const data = await response.json();

    // Guardar token y datos del usuario
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user_id', data.user_id);
    localStorage.setItem('username', data.username);
    localStorage.setItem('nombre', data.nombre);

    return data;
  }

  const error = await response.json();
  throw new Error(error.detail); // "El usuario no existe" o "Contraseña incorrecta"
}
```

### 2. Guardar Token

**Web (localStorage):**
```javascript
localStorage.setItem('token', access_token);
```

**Android (SharedPreferences):**
```kotlin
val prefs = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
prefs.edit().putString("token", accessToken).apply()
```

**Flutter (SharedPreferences):**
```dart
final prefs = await SharedPreferences.getInstance();
await prefs.setString('token', accessToken);
```

### 3. Usar Token en Peticiones

```javascript
async function apiRequest(endpoint) {
  const token = localStorage.getItem('token');

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (response.status === 401) {
    // Token expirado - hacer login nuevamente
    redirectToLogin();
    return;
  }

  return await response.json();
}
```

### 4. Logout

```javascript
function logout() {
  localStorage.removeItem('token');
  redirectToLogin();
}
```

---

## 📊 Datos de Prueba

Para testing, puedes crear usuarios con este SQL:

```sql
INSERT INTO usuario (id, username, nombre, apellido, password, creation, top_score)
VALUES
  (gen_random_uuid()::text, 'juan', 'Juan', 'García', 'password123', NOW(), 0),
  (gen_random_uuid()::text, 'maria', 'María', 'López', 'password456', NOW(), 50),
  (gen_random_uuid()::text, 'test', 'Test', 'User', 'test', NOW(), 100);
```

**Credenciales de prueba:**
- Username: `juan`, Password: `password123`
- Username: `maria`, Password: `password456`
- Username: `test`, Password: `test`

---

## 🧪 Testing con Postman

### 1. Importar Collection

Crea una nueva colección en Postman con:

**Variables:**
- `base_url`: `https://tu-api.up.railway.app`
- `token`: (se establecerá automáticamente)

### 2. Request de Login

```
POST {{base_url}}/api/v1/auth/login-app
Content-Type: application/json

{
  "username": "test",
  "password": "test"
}
```

**Test Script (para guardar token):**
```javascript
if (pm.response.code === 200) {
    const jsonData = pm.response.json();
    pm.collectionVariables.set("token", jsonData.access_token);
}
```

### 3. Request Protegido

```
GET {{base_url}}/api/v1/protected-endpoint
Authorization: Bearer {{token}}
```

---

## 🔒 Seguridad y Mejores Prácticas

### ✅ DO - Hacer

1. **Siempre usar HTTPS en producción**
   ```javascript
   const API_BASE_URL = 'https://tu-api.up.railway.app';
   ```

2. **Guardar tokens de forma segura**
   - Web: localStorage/sessionStorage
   - Mobile: Keychain (iOS) / KeyStore (Android)

3. **Manejar expiración de tokens**
   ```javascript
   if (response.status === 401) {
     // Token expirado - hacer login de nuevo
     redirectToLogin();
   }
   ```

4. **Validar responses**
   ```javascript
   if (!response.ok) {
     throw new Error(`HTTP ${response.status}`);
   }
   ```

5. **Usar Content-Type correcto**
   ```javascript
   headers: {
     'Content-Type': 'application/json'
   }
   ```

### ❌ DON'T - No hacer

1. **No hardcodear credenciales**
   ```javascript
   // ❌ MAL
   const password = "password123";

   // ✅ BIEN
   const password = userInput.password;
   ```

2. **No guardar passwords**
   ```javascript
   // ❌ MAL
   localStorage.setItem('password', password);

   // ✅ BIEN
   localStorage.setItem('token', access_token);
   ```

3. **No ignorar errores**
   ```javascript
   // ❌ MAL
   fetch(url).then(r => r.json()).catch(() => {});

   // ✅ BIEN
   try {
     const response = await fetch(url);
     if (!response.ok) throw new Error();
   } catch (error) {
     showErrorToUser(error);
   }
   ```

4. **No usar HTTP en producción**
   ```javascript
   // ❌ MAL en producción
   const API_URL = 'http://tu-api.com';

   // ✅ BIEN
   const API_URL = 'https://tu-api.up.railway.app';
   ```

---

## 📱 Ejemplos de Integración Completa

### React App

```jsx
import { useState } from 'react';

const API_BASE_URL = 'https://tu-api.up.railway.app';

function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login-app`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const { access_token } = await response.json();
      localStorage.setItem('token', access_token);

      // Redirigir al dashboard
      window.location.href = '/dashboard';
    } catch (err) {
      setError('Usuario o contraseña incorrectos');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">Login</button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
```

### Android (Jetpack Compose)

```kotlin
@Composable
fun LoginScreen() {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var error by remember { mutableStateOf("") }
    val scope = rememberCoroutineScope()

    Column {
        TextField(
            value = username,
            onValueChange = { username = it },
            label = { Text("Username") }
        )
        TextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            visualTransformation = PasswordVisualTransformation()
        )
        Button(onClick = {
            scope.launch {
                try {
                    val response = apiClient.post("$baseUrl/api/v1/auth/login-app") {
                        contentType(ContentType.Application.Json)
                        setBody(LoginRequest(username, password))
                    }
                    val token = response.body<TokenResponse>()

                    // Guardar token
                    saveToken(token.access_token)

                    // Navegar al home
                    navController.navigate("home")
                } catch (e: Exception) {
                    error = "Login fallido"
                }
            }
        }) {
            Text("Login")
        }
        if (error.isNotEmpty()) {
            Text(error, color = Color.Red)
        }
    }
}
```

---

## 🆘 Soporte

### Documentación
- [README.md](README.md) - Información general
- [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) - Despliegue en Railway
- [QUICKSTART.md](QUICKSTART.md) - Inicio rápido

### Swagger UI
Accede a `/docs` en tu API para ver la documentación interactiva completa.

### Health Check
Verifica que la API está corriendo: `GET /health`

---

**Última actualización:** 10 de Febrero 2026

---

## 📊 Estadísticas de la API

| Categoría | Endpoints |
|-----------|-----------|
| Autenticación | 2 |
| Usuarios | 5 |
| Profesores | 5 |
| Clases | 5 |
| Puntos | 5 |
| Actividades | 6 (+1 respuestas públicas) |
| Partidas | 5 |
| Progreso de Actividades | 8 |
| Audit Logs (solo lectura) | 2 |
| **Total** | **43 endpoints**
