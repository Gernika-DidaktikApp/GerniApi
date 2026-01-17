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
  "token_type": "bearer"
}
```

**Status: 401 Unauthorized**
```json
{
  "detail": "Username o contraseña incorrectos"
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
console.log(data.access_token);
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

### 1. Login

```javascript
async function login(username, password) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login-app`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  if (response.ok) {
    const { access_token } = await response.json();

    // Guardar token
    localStorage.setItem('token', access_token);

    return access_token;
  }

  throw new Error('Login failed');
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

**Última actualización:** Enero 2026
