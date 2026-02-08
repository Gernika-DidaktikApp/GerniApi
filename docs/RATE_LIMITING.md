# Rate Limiting con Redis

## 📋 Descripción

El proyecto ahora incluye **rate limiting basado en IP** usando Redis para proteger la API contra:
- Ataques de fuerza bruta en endpoints de login
- Abuso de la API
- Tráfico excesivo de un mismo cliente

## 🚀 Instalación

### 1. Instalar Dependencias

```bash
pip install redis fastapi-limiter
```

O instalar desde requirements.txt actualizado:

```bash
pip install -r requirements.txt
```

### 2. Instalar Redis

#### macOS (con Homebrew)
```bash
brew install redis
brew services start redis
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

#### Docker
```bash
docker run -d -p 6379:6379 redis:alpine
```

#### Windows
Descarga Redis desde: https://github.com/microsoftarchive/redis/releases

### 3. Verificar que Redis está funcionando

```bash
redis-cli ping
# Debería responder: PONG
```

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
# Redis
REDIS_URL=redis://localhost:6379/0

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=10
```

### Para Producción (Railway, Heroku, etc.)

Si tu servicio de Redis en producción requiere contraseña:

```env
REDIS_URL=redis://:tu-password@redis-host:6379/0
```

## 🎯 Límites Configurados

### Por Endpoint

| Endpoint | Límite | Descripción |
|----------|--------|-------------|
| `/api/v1/auth/login-app` | 5 req/min | Login de usuarios |
| `/api/v1/auth/login-profesor` | 5 req/min | Login de profesores |
| Otros endpoints | 10 req/min | Rate limit general |

### Tipos de Rate Limit Disponibles

En `app/utils/rate_limit.py` están definidos:

- **`rate_limit_strict`**: 5 peticiones/minuto (para login)
- **`rate_limit_default`**: 10 peticiones/minuto (general)
- **`rate_limit_permissive`**: 60 peticiones/minuto (lectura)

## 📝 Uso en Nuevos Endpoints

### Ejemplo: Aplicar rate limiting a un endpoint

```python
from fastapi import APIRouter, Depends
from app.utils.rate_limit import rate_limit_default, rate_limit_strict

router = APIRouter()

# Rate limit estricto (5 req/min)
@router.post("/sensitive-operation", dependencies=[Depends(rate_limit_strict)])
def sensitive_operation():
    return {"message": "Operación sensible"}

# Rate limit por defecto (10 req/min)
@router.get("/data", dependencies=[Depends(rate_limit_default)])
def get_data():
    return {"data": "..."}
```

## 🔧 Personalizar Límites

Edita `app/utils/rate_limit.py` para crear nuevos límites:

```python
from fastapi_limiter.depends import RateLimiter

# Rate limit personalizado: 3 peticiones cada 30 segundos
rate_limit_custom = RateLimiter(
    times=3,
    seconds=30,
    identifier=ip_based_identifier,
)
```

## 🧪 Probar el Rate Limiting

### Con curl

```bash
# Hacer 6 peticiones rápidas (debería rechazar la 6ta)
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/v1/auth/login-app \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test"}'
  echo "\nPetición $i completada"
done
```

### Respuesta cuando se excede el límite

```json
{
  "detail": "Rate limit exceeded: 5 per 1 minute"
}
```

HTTP Status: **429 Too Many Requests**

## 🐛 Solución de Problemas

### Error: "Could not connect to Redis"

1. Verificar que Redis está corriendo:
   ```bash
   redis-cli ping
   ```

2. Verificar la URL en `.env`:
   ```env
   REDIS_URL=redis://localhost:6379/0
   ```

3. Si no quieres usar Redis temporalmente:
   ```env
   RATE_LIMIT_ENABLED=False
   ```

### Rate limiting no funciona

- Verifica que `RATE_LIMIT_ENABLED=True` en `.env`
- Verifica que Redis está corriendo
- Revisa los logs de la aplicación al iniciar

## 🔒 Seguridad Adicional

### Recomendaciones

1. **Ajusta los límites** según tu caso de uso
2. **Monitorea** los intentos bloqueados en los logs
3. **Considera** implementar baneos temporales para IPs abusivas
4. **Usa HTTPS** en producción para proteger las credenciales

### Headers de Rate Limit

La API devuelve estos headers en cada respuesta:

```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 1234567890
```

## 📊 Monitoreo

Los intentos bloqueados se registran en los logs:

```
[INFO] Rate limit exceeded for IP: 192.168.1.100 on endpoint /api/v1/auth/login-app
```

## 🚀 Despliegue

### Railway

Railway detecta automáticamente Redis si lo añades como servicio:

1. Añade Redis en Railway Dashboard
2. La variable `REDIS_URL` se configura automáticamente
3. Despliega tu aplicación

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

---

**Autor: Gernibide**
