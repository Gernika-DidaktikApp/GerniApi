# Scripts de Prueba - GerniBide API

## ⚠️ IMPORTANTE: Seguridad

**NUNCA ejecutes scripts de prueba contra producción.**

Todos los scripts en esta carpeta están diseñados para ejecutarse **SOLO en localhost**.

## Scripts Disponibles

### 🔒 `generar_datos_prueba.py` (RECOMENDADO)

Script seguro para generar datos de prueba en local.

**Características de seguridad:**
- ✅ Solo funciona con `localhost:8000`
- ✅ Valida que el servidor esté corriendo
- ✅ Bloquea ejecución contra producción
- ✅ Requiere confirmación antes de generar datos

**Uso:**
```bash
# 1. Asegúrate de tener el servidor corriendo
make dev

# 2. En otra terminal, ejecuta:
python3 scripts/generar_datos_prueba.py
```

**Opciones:**
1. Generar datos históricos (30 días, 50 usuarios) - Para probar estadísticas
2. Crear solo 10 usuarios de prueba - Para pruebas rápidas

### ⚠️ `test_flow.py`

Script para probar el flujo completo de la aplicación.

**IMPORTANTE:** Antes de ejecutar, verifica que `BASE_URL` apunte a `localhost`:

```python
BASE_URL = "http://localhost:8000"  # ✅ Correcto
# BASE_URL = "https://gernibide.up.railway.app"  # ❌ ¡NO USAR!
```

**Uso:**
```bash
python3 scripts/test_flow.py
```

### 📋 `listar_eventos.py`

Lista los eventos disponibles en el sistema.

**Uso:**
```bash
python3 scripts/listar_eventos.py
```

### ➕ `crear_eventos.py`

Crea eventos de prueba en el sistema.

**Uso:**
```bash
python3 scripts/crear_eventos.py
```

## Flujo de Trabajo Seguro

### Para Desarrollo Local:

```bash
# Terminal 1: Servidor
make dev

# Terminal 2: Generar datos de prueba
python3 scripts/generar_datos_prueba.py

# Ahora puedes ver las estadísticas en:
# http://localhost:8000/statistics
```

### Para Producción:

**NO uses estos scripts en producción.**

Los datos de producción deben venir de:
- Usuarios reales usando la app móvil
- Importación de datos vía endpoints autenticados
- Migraciones de datos controladas

## Verificar Entorno

Antes de ejecutar cualquier script, verifica:

```bash
# ¿Dónde está apuntando?
grep BASE_URL scripts/*.py

# Deberías ver:
# BASE_URL = "http://localhost:8000"  ✅

# Si ves Railway u otro dominio:
# BASE_URL = "https://gernibide.up.railway.app"  ❌ PELIGRO
```

## Solución de Problemas

### Error: "El servidor local no está corriendo"
```bash
# Inicia el servidor en otra terminal
make dev
```

### Error: "Este script solo puede ejecutarse contra localhost"
```bash
# Buena señal! El script está protegido.
# Verifica que BASE_URL = "http://localhost:8000"
```

### No veo datos en las estadísticas
```bash
# Ejecuta el generador de datos
python3 scripts/generar_datos_prueba.py
# Selecciona opción 1 (datos históricos)
```

## Limpieza

Para eliminar todos los datos de prueba de tu BD local:

```bash
# Opción 1: Resetear la base de datos (SQLite)
rm didaktikapp.db
make dev  # Recreará las tablas vacías

# Opción 2: Revertir y aplicar migraciones
alembic downgrade base
alembic upgrade head
```

## Contacto

Si encuentras problemas de seguridad en estos scripts, reporta inmediatamente.
