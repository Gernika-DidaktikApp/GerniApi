# Sistema de Autenticación - GerniBide API

Documentación completa del sistema de login y autenticación para la interfaz web de GerniBide.

## 📋 Índice

- [Características](#características)
- [Configuración Inicial](#configuración-inicial)
- [Uso del Sistema](#uso-del-sistema)
- [Arquitectura Técnica](#arquitectura-técnica)
- [Endpoints API](#endpoints-api)
- [Scripts de Gestión](#scripts-de-gestión)
- [Seguridad](#seguridad)

## ✨ Características

- ✅ Autenticación con JWT (JSON Web Tokens)
- ✅ Login para profesores con username/password
- ✅ Tokens con expiración de 30 minutos
- ✅ Protección de rutas privadas (dashboard, dashboard-teacher)
- ✅ Logout con limpieza de sesión
- ✅ Hash seguro de contraseñas con bcrypt
- ✅ Validación de formularios en frontend
- ✅ Mensajes de error claros
- ✅ Persistencia de sesión en localStorage

## 🚀 Configuración Inicial

### Opción 1: Script Automático (Recomendado)

```bash
# Desde el directorio raíz del proyecto
./scripts/setup_login.sh
```

Este script:
1. Crea un profesor de prueba (admin/admin123)
2. Verifica la configuración
3. Muestra instrucciones de uso

### Opción 2: Manual

```bash
# Crear profesor con credenciales por defecto
python3 scripts/crear_profesor.py

# Crear profesor con credenciales personalizadas
python3 scripts/crear_profesor.py <username> <password>

# Ejemplo completo
python3 scripts/crear_profesor.py maria garcia123 María García
```

## 📱 Uso del Sistema

### 1. Página de Login

Accede a: `http://localhost:8000/login`

**Credenciales por defecto:**
- Username: `admin`
- Password: `admin123`

### 2. Proceso de Login

1. Ingresa username y password
2. El formulario valida los campos
3. Se envía petición a `/api/v1/auth/login-profesor`
4. Si es exitoso:
   - Se guarda el token JWT en localStorage
   - Se guardan datos del usuario (nombre, username)
   - Redirección automática a `/dashboard`

### 3. Páginas Protegidas

Las siguientes páginas requieren autenticación:
- `/dashboard` - Dashboard general
- `/dashboard/teacher` - Dashboard de profesor

Si intentas acceder sin autenticación, serás redirigido automáticamente a `/login`.

### 4. Logout

Haz clic en "Cerrar Sesión" en la navbar:
- Se eliminan el token y datos del localStorage
- Redirección automática a `/login`

## 🏗️ Arquitectura Técnica

### Frontend

**Archivos principales:**
```
app/web/
├── templates/
│   ├── login.html                  # Página de login
│   ├── dashboard.html              # Dashboard protegido
│   └── dashboard-teacher.html      # Dashboard profesor protegido
└── static/js/
    ├── login.js                    # Lógica de login
    ├── dashboard.js                # Protección + logout
    └── dashboard-teacher.js        # Protección + logout
```

**Flujo de autenticación (login.js):**

```javascript
// 1. Validación de formulario
validateUsername() && validatePassword()

// 2. Petición de login
POST /api/v1/auth/login-profesor
Body: { username, password }

// 3. Almacenar datos
localStorage.setItem('authToken', data.access_token)
localStorage.setItem('userUsername', data.username)
localStorage.setItem('userName', data.nombre)

// 4. Redirigir
window.location.href = '/dashboard'
```

**Protección de páginas (dashboard.js, dashboard-teacher.js):**

```javascript
function checkAuthentication() {
    const authToken = localStorage.getItem('authToken');
    if (!authToken) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Llamar en init()
if (!checkAuthentication()) return;
```

**Logout:**

```javascript
function handleLogout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userName');
    localStorage.removeItem('userUsername');
    window.location.href = '/login';
}
```

### Backend

**Endpoint de Login:**

```python
# app/routers/auth.py

@router.post("/login-profesor", response_model=LoginProfesorResponse)
def login_profesor(login_data: LoginAppRequest, db: Session = Depends(get_db)):
    # 1. Buscar profesor por username
    profesor = db.query(Profesor).filter(Profesor.username == login_data.username).first()

    # 2. Verificar contraseña con bcrypt
    if not profesor or not verify_password(login_data.password, profesor.password):
        raise HTTPException(status_code=401, detail="Username o contraseña incorrectos")

    # 3. Generar token JWT
    access_token = create_access_token(
        data={"sub": profesor.username, "type": "profesor"},
        expires_delta=timedelta(minutes=30)
    )

    # 4. Devolver token y datos
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "profesor_id": profesor.id,
        "username": profesor.username,
        "nombre": profesor.nombre,
        "apellido": profesor.apellido
    }
```

**Modelo de Profesor:**

```python
# app/models/profesor.py

class Profesor(Base):
    __tablename__ = "profesor"

    id = Column(String(36), primary_key=True)
    username = Column(String(45), unique=True, nullable=False)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    password = Column(String(255), nullable=False)  # Hash bcrypt
    created = Column(DateTime, default=datetime.now)
```

## 🔌 Endpoints API

### POST `/api/v1/auth/login-profesor`

Autentica un profesor y devuelve un token JWT.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "profesor_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "admin",
  "nombre": "Profesor",
  "apellido": "Admin"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Username o contraseña incorrectos"
}
```

**Uso del Token:**

Para endpoints protegidos, incluye el token en el header:
```
Authorization: Bearer <access_token>
```

## 🛠️ Scripts de Gestión

### crear_profesor.py

Script para crear profesores en la base de datos.

**Uso básico:**
```bash
# Crear profesor por defecto (admin/admin123)
python3 scripts/crear_profesor.py

# Crear con credenciales personalizadas
python3 scripts/crear_profesor.py username password

# Crear con todos los datos
python3 scripts/crear_profesor.py maria garcia123 María García
```

**Características:**
- Hash automático de contraseñas con bcrypt
- Verifica si el username ya existe
- Permite actualizar contraseña de usuarios existentes
- Genera UUID automático para el ID
- Muestra credenciales creadas al finalizar

### setup_login.sh

Script de configuración completa del sistema de login.

**Uso:**
```bash
./scripts/setup_login.sh
```

**Qué hace:**
- Verifica que estás en el directorio correcto
- Crea un profesor de prueba
- Muestra instrucciones de uso
- Proporciona URLs de acceso

## 🔒 Seguridad

### Almacenamiento de Contraseñas

Las contraseñas se almacenan usando **bcrypt** con salt automático:

```python
from app.utils.security import get_password_hash, verify_password

# Al crear usuario
hashed_password = get_password_hash("password123")

# Al verificar login
is_valid = verify_password("password123", hashed_password)
```

### JWT Tokens

- **Algoritmo**: HS256
- **Expiración**: 30 minutos
- **Claims**: `sub` (username), `type` (profesor), `exp` (timestamp)

Configuración en `app/config.py`:
```python
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### Almacenamiento en Frontend

Los tokens se almacenan en `localStorage`:

**Ventajas:**
- Persiste entre sesiones del navegador
- Fácil acceso desde JavaScript
- No se envía automáticamente con peticiones (previene CSRF)

**Consideraciones:**
- Vulnerable a XSS (Cross-Site Scripting)
- No usar en sitios con contenido de terceros sin sanitizar
- Los tokens expiran en 30 minutos

### Protección CSRF

Las peticiones usan `Content-Type: application/json` y no credentials, lo que previene ataques CSRF básicos.

### Validación Frontend

El formulario valida:
- Username mínimo 3 caracteres
- Password mínimo 6 caracteres
- Campos requeridos

### Logging

Todos los intentos de login se registran:
```python
log_auth("login_profesor_attempt", username=username, client_ip=client_ip)
log_auth("login_profesor_success", username=username, profesor_id=id)
log_auth("login_profesor_failed", username=username, reason="Credenciales inválidas")
```

## 🐛 Troubleshooting

### Error: "Username o contraseña incorrectos"

1. Verifica que el profesor existe:
   ```bash
   python3 scripts/crear_profesor.py admin admin123
   ```

2. Si existe, intenta actualizar la contraseña cuando el script lo pregunte

### No redirige al dashboard tras login

1. Abre la consola del navegador (F12)
2. Verifica que no hay errores de JavaScript
3. Verifica que el token se guardó:
   ```javascript
   localStorage.getItem('authToken')
   ```

### Redirige a login desde el dashboard

1. Verifica que el token existe en localStorage
2. Verifica que el servidor está corriendo
3. El token puede haber expirado (30 minutos)

### Error de base de datos

1. Verifica que la base de datos existe:
   ```bash
   ls didaktikapp.db
   ```

2. Verifica las tablas:
   ```bash
   sqlite3 didaktikapp.db ".tables"
   ```

3. Si falta la tabla profesor, ejecuta las migraciones:
   ```bash
   make dev  # Las tablas se crean automáticamente al iniciar
   ```

## 📚 Recursos Adicionales

- **API Documentation**: http://localhost:8000/docs
- **Configuración JWT**: `app/config.py`
- **Utilidades de Seguridad**: `app/utils/security.py`
- **Modelos**: `app/models/profesor.py`
- **Schemas**: `app/schemas/usuario.py`

## 🔄 Próximas Mejoras

- [ ] Refresh tokens para sesiones largas
- [ ] Recordar usuario (checkbox "Recordarme")
- [ ] Recuperación de contraseña por email
- [ ] Autenticación de dos factores (2FA)
- [ ] Rate limiting en login endpoint
- [ ] Captcha tras múltiples intentos fallidos
- [ ] Historial de sesiones activas
- [ ] Logout de todas las sesiones
- [ ] Blacklist de tokens revocados
