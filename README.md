# GernikApp API

API REST con FastAPI para gestionar la autenticación de la aplicación móvil Gernibide.

## Requisitos Previos

- Python 3.8+
- MariaDB con la base de datos configurada
- Tabla `alumno` creada en la base de datos

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales de base de datos
```

4. Asegúrate de que la tabla `alumno` existe en tu base de datos.

## Ejecución

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en:
- **API**: http://localhost:8000
- **Documentación interactiva (Swagger)**: http://localhost:8000/docs
- **Documentación alternativa (ReDoc)**: http://localhost:8000/redoc

## Endpoints Disponibles

### Autenticación

#### POST `/api/v1/auth/login`
Inicia sesión y devuelve un token JWT.

**Request Body:**
```json
{
  "usuario": "nombre_usuario",
  "contrasenya": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET `/api/v1/auth/me`
Obtiene la información del alumno autenticado.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "usuario": "nombre_usuario",
  "nombre": "Nombre Completo",
  "idioma": "es"
}
```

## Estructura del Proyecto

```
gerniapi/
├── app/
│   ├── models/          # Modelos SQLAlchemy (tabla alumno)
│   ├── schemas/         # Esquemas Pydantic (validación)
│   ├── routers/         # Endpoints de la API
│   ├── utils/           # Utilidades (JWT, seguridad)
│   ├── config.py        # Configuración
│   ├── database.py      # Conexión a BD
│   └── main.py          # Punto de entrada
├── .env                 # Variables de entorno (NO subir a git)
├── .env.example         # Ejemplo de variables
├── requirements.txt     # Dependencias
└── README.md
```

## Uso desde la App Móvil

1. Hacer POST a `/api/v1/auth/login` con usuario y contraseña
2. Guardar el `access_token` recibido
3. Incluir el token en las siguientes peticiones:
   ```
   Authorization: Bearer <access_token>
   ```

## Seguridad

- Los tokens JWT expiran en 30 minutos (configurable en `.env`)
- Cambiar `SECRET_KEY` en producción por una clave segura
- En producción, configurar CORS para permitir solo orígenes específicos
