# GerniBide API - Colección de Postman

Esta colección incluye todos los endpoints de la API GerniBide organizados por categorías.

## Archivos Incluidos

- **GerniBide_API.postman_collection.json** - Colección completa con todos los endpoints
- **GerniBide_API.postman_environment.json** - Archivo de entorno con variables configurables

## Cómo Importar en Postman

### 1. Importar la Colección

1. Abre Postman
2. Click en **Import** (esquina superior izquierda)
3. Selecciona el archivo `GerniBide_API.postman_collection.json`
4. La colección aparecerá en tu sidebar

### 2. Importar el Entorno

1. Click en **Import** nuevamente
2. Selecciona el archivo `GerniBide_API.postman_environment.json`
3. El entorno aparecerá en el selector de entornos (esquina superior derecha)
4. Selecciona "GerniBide API - Local" como entorno activo

### 3. Configurar Variables de Entorno

Antes de empezar a usar la colección, configura las siguientes variables:

#### Variables Obligatorias:

- **base_url**: URL base de tu API (default: `http://localhost:8000`)
- **api_key**: Tu API Key (obtenerla desde `app/config.py`)

#### Variables Opcionales (se obtienen automáticamente):

- **token**: Token JWT de usuario (obtenido al hacer login con `/api/v1/auth/login-app`)
- **token_profesor**: Token JWT de profesor (obtenido al hacer login con `/api/v1/auth/login-profesor`)
- **usuario_id**, **profesor_id**, **clase_id**, etc.: UUIDs para testing

Para editar las variables:
1. Click en el icono de ojo (👁️) junto al selector de entornos
2. Click en **Edit** junto a "GerniBide API - Local"
3. Actualiza los valores en la columna "CURRENT VALUE"
4. Click en **Save**

## Estructura de la Colección

La colección está organizada en las siguientes carpetas:

### 🔐 Auth - Autenticación
- Login Usuario (App)
- Login Profesor

### 👥 Usuarios
- CRUD completo de usuarios
- Estadísticas del usuario

### 👨‍🏫 Profesores
- CRUD completo de profesores

### 🏫 Clases
- CRUD completo de clases

### 📝 Actividades
- CRUD completo de actividades

### 📅 Eventos
- CRUD completo de eventos

### 🎮 Partidas
- CRUD completo de partidas (juegos)

### 📊 Estados de Eventos
- Iniciar evento
- Completar evento
- Resumen de actividad
- CRUD completo de estados

### 📊 Estadísticas - Usuarios
- Resumen de usuarios
- Timeline de usuarios activos (DAU/WAU/MAU)
- Nuevos usuarios por día
- Ratio de usuarios activos
- Logins por día

### 📊 Estadísticas - Gameplay
- Resumen de gameplay
- Partidas por día
- Partidas por estado
- Eventos por estado
- Tasa de completación

### 📊 Estadísticas - Learning
- Resumen de aprendizaje
- Puntuación media por actividad
- Distribución de puntuaciones
- Boxplot de tiempo

### 👨‍🏫 Teacher Dashboard
- Clases del profesor
- Resumen de clase
- Progreso por estudiante
- Tiempo por estudiante
- Actividades por clase
- Evolución de la clase

### 🌐 Health & Info
- Root endpoint
- Health check

## Tipos de Autenticación

La API utiliza dos mecanismos de autenticación:

### 1. API Key (Acceso Administrativo)
Para endpoints administrativos, agrega el header:
```
X-API-Key: tu-api-key
```

### 2. Token JWT (Acceso de Usuario)
Para endpoints de usuario/profesor, agrega el header:
```
Authorization: Bearer tu-token-jwt
```

Los tokens se obtienen de los endpoints de login y son válidos por **30 minutos**.

## Flujo de Trabajo Recomendado

### Para Usuarios:
1. **Login**: POST `/api/v1/auth/login-app` → Copiar el `access_token`
2. **Guardar Token**: Pegar el token en la variable `token` del entorno
3. **Usar Endpoints**: Ahora puedes usar endpoints que requieren `Bearer {{token}}`

### Para Profesores:
1. **Login**: POST `/api/v1/auth/login-profesor` → Copiar el `access_token`
2. **Guardar Token**: Pegar el token en la variable `token_profesor` del entorno
3. **Usar Dashboard**: Ahora puedes acceder a los endpoints del Teacher Dashboard

### Para Administración:
1. **Configurar API Key**: Obtener de `app/config.py` y guardar en variable `api_key`
2. **Usar Endpoints Admin**: Los endpoints con API Key funcionarán automáticamente

## Ejemplos de Uso

### Crear y usar un usuario:

1. **Registro**: POST `/api/v1/usuarios`
   ```json
   {
     "username": "test_user",
     "nombre": "Test",
     "apellido": "User",
     "password": "password123"
   }
   ```

2. **Login**: POST `/api/v1/auth/login-app`
   ```json
   {
     "username": "test_user",
     "password": "password123"
   }
   ```
   → Copiar `access_token` a variable `token`

3. **Ver Perfil**: GET `/api/v1/usuarios/:usuario_id`
   (Usar el `user_id` del response del login)

### Iniciar y completar una partida:

1. **Crear Partida**: POST `/api/v1/partidas`
   ```json
   {
     "id_usuario": "uuid-del-usuario"
   }
   ```

2. **Iniciar Evento**: POST `/api/v1/evento-estados/iniciar`
   ```json
   {
     "id_juego": "uuid-de-la-partida",
     "id_actividad": "uuid-de-actividad",
     "id_evento": "uuid-de-evento"
   }
   ```

3. **Completar Evento**: PUT `/api/v1/evento-estados/:estado_id/completar`
   ```json
   {
     "puntuacion": 85.5
   }
   ```

4. **Ver Resumen**: GET `/api/v1/evento-estados/actividad/:id_juego/:id_actividad/resumen`

## Notas Importantes

- **UUIDs**: Todos los IDs son UUIDs (v4). Guarda los IDs de las responses para usar en otras requests.
- **Paginación**: Los endpoints de listado soportan `skip` y `limit` (default: skip=0, limit=100).
- **Timestamps**: Todas las fechas están en formato ISO 8601.
- **Passwords**: Las contraseñas se hashean con bcrypt antes de guardarse.
- **Validación**: Los endpoints validan ownership cuando se usa Token JWT (un usuario solo puede acceder a sus propios recursos).
- **Cache**: Los endpoints de estadísticas tienen cache que se puede limpiar con los endpoints `/cache/clear`.

## Solución de Problemas

### Error 401 - Unauthorized
- Verifica que el token esté configurado correctamente en las variables de entorno
- Asegúrate de que el token no haya expirado (válido por 30 minutos)
- Verifica que estés usando el header correcto (`Authorization: Bearer {{token}}` o `X-API-Key: {{api_key}}`)

### Error 403 - Forbidden
- Estás intentando acceder a un recurso que no te pertenece
- Verifica que el `usuario_id` de la URL coincida con el usuario del token

### Error 404 - Not Found
- El recurso con ese ID no existe
- Verifica que el UUID esté correcto

### Error 422 - Validation Error
- El body de la request tiene campos faltantes o inválidos
- Revisa la estructura del JSON en los ejemplos de la colección

## Obtener la API Key

La API Key se encuentra en el archivo de configuración:

```bash
cat app/config.py | grep API_KEY
```

O puedes ver directamente el valor en el código fuente.

## Soporte

Para más información sobre la API, consulta:
- Documentación automática: `http://localhost:8000/docs` (Swagger UI)
- Documentación alternativa: `http://localhost:8000/redoc` (ReDoc)

---

**Versión**: 1.0.0
**Última actualización**: 2026-01-28
**Framework**: FastAPI 0.115.0
