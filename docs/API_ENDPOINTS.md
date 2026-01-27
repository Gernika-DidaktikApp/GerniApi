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

### Actividades
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/actividades` | Crear actividad | 🔑 |
| GET | `/api/v1/actividades` | Listar actividades | 🔑🎫 |
| GET | `/api/v1/actividades/{id}` | Obtener actividad | 🔑🎫 |
| PUT | `/api/v1/actividades/{id}` | Actualizar actividad | 🔑 |
| DELETE | `/api/v1/actividades/{id}` | Eliminar actividad | 🔑 |

### Eventos
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/eventos` | Crear evento | 🔑 |
| GET | `/api/v1/eventos` | Listar eventos | 🔑🎫 |
| GET | `/api/v1/eventos/{id}` | Obtener evento | 🔑🎫 |
| PUT | `/api/v1/eventos/{id}` | Actualizar evento | 🔑 |
| DELETE | `/api/v1/eventos/{id}` | Eliminar evento | 🔑 |

### Partidas
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/partidas` | Crear partida | 🔑🎫 |
| GET | `/api/v1/partidas` | Listar partidas | 🔑 |
| GET | `/api/v1/partidas/{id}` | Obtener partida | 🔑🎫 |
| PUT | `/api/v1/partidas/{id}` | Actualizar partida | 🔑🎫 |
| DELETE | `/api/v1/partidas/{id}` | Eliminar partida | 🔑 |

### Estados de Eventos
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/evento-estados/iniciar` | Iniciar evento | 🔑🎫 |
| PUT | `/api/v1/evento-estados/{id}/completar` | Completar evento | 🔑🎫 |
| GET | `/api/v1/evento-estados/actividad/{id_juego}/{id_actividad}/resumen` | Resumen de actividad (calculado) | 🔑🎫 |
| POST | `/api/v1/evento-estados` | Crear estado | 🔑🎫 |
| GET | `/api/v1/evento-estados` | Listar estados | 🔑 |
| GET | `/api/v1/evento-estados/{id}` | Obtener estado | 🔑🎫 |
| PUT | `/api/v1/evento-estados/{id}` | Actualizar estado | 🔑🎫 |
| DELETE | `/api/v1/evento-estados/{id}` | Eliminar estado | 🔑 |

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
  "id_clase": "uuid (opcional)"
}
```

| Campo | Tipo | Requerido | Validación |
|-------|------|-----------|------------|
| `username` | string | sí | 3-45 caracteres, único |
| `nombre` | string | sí | 1-45 caracteres |
| `apellido` | string | sí | 1-45 caracteres |
| `password` | string | sí | 4-100 caracteres |
| `id_clase` | string | no | UUID de clase existente |

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

**curl:**
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

**JavaScript/Fetch:**
```javascript
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

if (response.status === 201) {
  const usuario = await response.json();
  console.log('Usuario creado:', usuario.id);
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
| `actividades_completadas` | int | Número de sub-actividades (eventos) completadas |
| `racha_dias` | int | Días consecutivos de juego (desde hoy hacia atrás) |
| `modulos_completados` | string[] | Nombres de módulos/actividades completadas |
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

Crea una nueva clase.

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
  "nombre": "4º ESO A",
  "id_profesor": "uuid-del-profesor"
}
```

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

## 📝 Actividades

### POST `/api/v1/actividades`

Crea una nueva actividad. **Requiere API Key.**

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
  "nombre": "Actividad 1 - Introducción"
}
```

---

### GET `/api/v1/actividades`

Lista todas las actividades. **Requiere API Key o Token.**

---

### GET `/api/v1/actividades/{actividad_id}`

Obtiene una actividad por ID. **Requiere API Key o Token.**

---

### PUT `/api/v1/actividades/{actividad_id}`

Actualiza una actividad. **Requiere API Key.**

---

### DELETE `/api/v1/actividades/{actividad_id}`

Elimina una actividad. **Requiere API Key.** **Response: 204 No Content**

---

## 📅 Eventos

Los eventos son sub-elementos dentro de cada actividad.

### POST `/api/v1/eventos`

Crea un nuevo evento. **Requiere API Key.**

**Body:**
```json
{
  "nombre": "string",
  "id_actividad": "uuid"
}
```

**Response: 201 Created**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Evento 1",
  "id_actividad": "uuid-de-la-actividad"
}
```

---

### GET `/api/v1/eventos`

Lista todos los eventos. **Requiere API Key o Token.**

---

### GET `/api/v1/eventos/{evento_id}`

Obtiene un evento por ID. **Requiere API Key o Token.**

---

### PUT `/api/v1/eventos/{evento_id}`

Actualiza un evento. **Requiere API Key.**

---

### DELETE `/api/v1/eventos/{evento_id}`

Elimina un evento. **Requiere API Key.** **Response: 204 No Content**

---

## 🎮 Partidas

Las partidas representan sesiones de juego de un usuario.

### POST `/api/v1/partidas`

Crea una nueva partida. **Requiere API Key o Token.**

- Con API Key: Puede crear partidas para cualquier usuario
- Con Token: Solo puede crear partidas para sí mismo

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
  "fecha_inicio": "2026-01-23T10:30:00"
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

## 📊 Estados de Eventos

El sistema de gestión de estados permite rastrear el progreso de los eventos de los jugadores, calculando automáticamente tiempos y puntuaciones.

### Flujo de Trabajo Simplificado

1. **Jugador inicia evento** → POST `/api/v1/evento-estados/iniciar`
2. **Jugador completa evento** → PUT `/api/v1/evento-estados/{id}/completar`
3. **Consultar resumen de actividad** → GET `/api/v1/evento-estados/actividad/{id_juego}/{id_actividad}/resumen`

> **Nota:** El resumen de actividad (puntuación total, estado, duración) se calcula automáticamente desde los eventos.

---

### POST `/api/v1/evento-estados/iniciar`

Inicia un evento dentro de una actividad. Registra automáticamente la fecha de inicio.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "id_juego": "uuid-de-la-partida",
  "id_actividad": "uuid-de-la-actividad",
  "id_evento": "uuid-del-evento"
}
```

#### Response

**Status: 201 Created**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "id_juego": "uuid-de-la-partida",
  "id_actividad": "uuid-de-la-actividad",
  "id_evento": "uuid-del-evento",
  "fecha_inicio": "2026-01-18T10:35:00",
  "duracion": null,
  "fecha_fin": null,
  "estado": "en_progreso",
  "puntuacion": null
}
```

**Status: 400 Bad Request**
```json
{
  "detail": "Ya existe un evento en progreso para este juego y evento"
}
```

**Status: 404 Not Found**
```json
{
  "detail": "El evento especificado no existe o no pertenece a esta actividad"
}
```

#### Ejemplos

**curl:**
```bash
curl -X POST "https://tu-api.up.railway.app/api/v1/evento-estados/iniciar" \
  -H "Content-Type: application/json" \
  -d '{
    "id_juego": "uuid-partida",
    "id_actividad": "uuid-actividad",
    "id_evento": "uuid-evento"
  }'
```

**JavaScript:**
```javascript
const response = await fetch(`${API_BASE_URL}/api/v1/evento-estados/iniciar`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    id_juego: partidaId,
    id_actividad: actividadId,
    id_evento: eventoId
  })
});

const eventoEstado = await response.json();
// Guardar el ID para completar después
localStorage.setItem('evento_estado_id', eventoEstado.id);
```

**Flutter:**
```dart
final response = await http.post(
  Uri.parse('$baseUrl/api/v1/evento-estados/iniciar'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'id_juego': partidaId,
    'id_actividad': actividadId,
    'id_evento': eventoId
  }),
);

if (response.statusCode == 201) {
  final eventoEstado = jsonDecode(response.body);
  // Guardar ID para completar después
  await prefs.setString('evento_estado_id', eventoEstado['id']);
}
```

---

### PUT `/api/v1/evento-estados/{estado_id}/completar`

Completa un evento y registra su puntuación. **Calcula automáticamente**:
- Duración del evento (fecha_fin - fecha_inicio)
- Actualiza el estado a "completado"

#### Request

**Headers:**
```
Content-Type: application/json
```

**URL Parameters:**
- `estado_id`: UUID del estado del evento (obtenido al iniciar el evento)

**Body:**
```json
{
  "puntuacion": 85.5
}
```

#### Response

**Status: 200 OK**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "id_juego": "uuid-de-la-partida",
  "id_actividad": "uuid-de-la-actividad",
  "id_evento": "uuid-del-evento",
  "fecha_inicio": "2026-01-18T10:35:00",
  "fecha_fin": "2026-01-18T10:40:30",
  "duracion": 330,
  "estado": "completado",
  "puntuacion": 85.5
}
```

**Status: 400 Bad Request**
```json
{
  "detail": "El evento no está en progreso. Estado actual: completado"
}
```

**Status: 404 Not Found**
```json
{
  "detail": "Estado de evento no encontrado"
}
```

#### Ejemplos

**curl:**
```bash
# Completar evento con puntuación
curl -X PUT "https://tu-api.up.railway.app/api/v1/evento-estados/660e8400.../completar" \
  -H "Content-Type: application/json" \
  -d '{
    "puntuacion": 85.5
  }'
```

**JavaScript:**
```javascript
// Completar evento
const eventoEstadoId = localStorage.getItem('evento_estado_id');

const response = await fetch(
  `${API_BASE_URL}/api/v1/evento-estados/${eventoEstadoId}/completar`,
  {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      puntuacion: playerScore
    })
  }
);

const eventoCompletado = await response.json();
console.log('Evento completado con', eventoCompletado.puntuacion, 'puntos');
console.log('Duración:', eventoCompletado.duracion, 'segundos');
```

**Kotlin:**
```kotlin
val eventoEstadoId = prefs.getString("evento_estado_id", "")

val response = client.put("$baseUrl/api/v1/evento-estados/$eventoEstadoId/completar") {
    contentType(ContentType.Application.Json)
    setBody(mapOf("puntuacion" to 85.5))
}

val eventoCompletado = response.body<EventoEstadoResponse>()
println("Duración: ${eventoCompletado.duracion} segundos")
```

**Flutter:**
```dart
final eventoEstadoId = await prefs.getString('evento_estado_id');

final response = await http.put(
  Uri.parse('$baseUrl/api/v1/evento-estados/$eventoEstadoId/completar'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({'puntuacion': playerScore}),
);

if (response.statusCode == 200) {
  final evento = jsonDecode(response.body);
  print('Evento completado: ${evento['puntuacion']} puntos');
  print('Duración: ${evento['duracion']} segundos');
}
```

---

### GET `/api/v1/evento-estados/actividad/{id_juego}/{id_actividad}/resumen`

Obtiene el resumen calculado de una actividad basado en los eventos completados.

#### URL Parameters
- `id_juego`: UUID de la partida
- `id_actividad`: UUID de la actividad

#### Response

**Status: 200 OK**
```json
{
  "id_juego": "uuid-de-la-partida",
  "id_actividad": "uuid-de-la-actividad",
  "nombre_actividad": "Bunkers",
  "eventos_totales": 5,
  "eventos_completados": 3,
  "eventos_en_progreso": 1,
  "puntuacion_total": 256.5,
  "duracion_total": 450,
  "fecha_inicio": "2026-01-18T10:30:00",
  "fecha_fin": null,
  "estado": "en_progreso"
}
```

| Campo | Descripción |
|-------|-------------|
| `eventos_totales` | Total de eventos en la actividad |
| `eventos_completados` | Eventos ya completados |
| `puntuacion_total` | Suma de puntuaciones de eventos completados |
| `duracion_total` | Suma de duraciones en segundos |
| `estado` | "no_iniciada", "en_progreso" o "completada" |

#### Ejemplos

**curl:**
```bash
curl -X GET "https://tu-api.up.railway.app/api/v1/evento-estados/actividad/{id_juego}/{id_actividad}/resumen" \
  -H "Authorization: Bearer <token>"
```

**JavaScript:**
```javascript
const resumen = await fetch(
  `${API_BASE_URL}/api/v1/evento-estados/actividad/${partidaId}/${actividadId}/resumen`,
  { headers: { 'Authorization': `Bearer ${token}` } }
).then(r => r.json());

console.log('Estado:', resumen.estado);
console.log('Puntuación:', resumen.puntuacion_total);
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

// 2. Para cada evento de la actividad
for (const eventoId of eventosIds) {
  // 2a. Iniciar evento
  const eventoInicioResponse = await fetch(
    `${API_BASE_URL}/api/v1/evento-estados/iniciar`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        id_juego: partidaId,
        id_actividad: actividadId,
        id_evento: eventoId
      })
    }
  );
  const { id: eventoEstadoId } = await eventoInicioResponse.json();

  // 2b. Jugador completa el evento
  // ... lógica del juego ...

  // 2c. Completar evento con puntuación
  await fetch(
    `${API_BASE_URL}/api/v1/evento-estados/${eventoEstadoId}/completar`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ puntuacion: score })
    }
  );
}

// 3. Obtener resumen de la actividad
const resumen = await fetch(
  `${API_BASE_URL}/api/v1/evento-estados/actividad/${partidaId}/${actividadId}/resumen`,
  { headers: { 'Authorization': `Bearer ${token}` } }
).then(r => r.json());

console.log('Actividad:', resumen.estado);
console.log('Puntuación total:', resumen.puntuacion_total);
console.log('Tiempo total:', resumen.duracion_total, 'segundos');
```

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

**Última actualización:** 24 de Enero 2026

---

## 📊 Estadísticas de la API

| Categoría | Endpoints |
|-----------|-----------|
| Autenticación | 2 |
| Usuarios | 5 |
| Profesores | 5 |
| Clases | 5 |
| Actividades | 5 |
| Eventos | 5 |
| Partidas | 5 |
| Estados de Eventos | 8 |
| **Total** | **40 endpoints**
