# 📦 Scripts Legacy (Acceso Directo a BBDD)

**⚠️ IMPORTANTE:** Estos scripts usan acceso directo a la base de datos.

## ¿Por qué están aquí?

Estos son scripts antiguos que fueron reemplazados por el **nuevo CLI** (`../cli.py`) que usa la API.

## ⚠️ NO uses estos scripts a menos que:

1. **El CLI no ofrece la funcionalidad** que necesitas
2. **Has verificado** que no se puede hacer vía API
3. **Tienes credenciales de BBDD** (solicítalas al administrador)
4. **Sabes lo que estás haciendo** (riesgo de romper datos)

## Alternativa Recomendada

**Usa el CLI principal en su lugar:**

```bash
# En lugar de estos scripts legacy:
python scripts/legacy/crear_profesor.py

# Usa el CLI nuevo:
python scripts/cli.py users create-profesor
```

Ver [../README.md](../README.md) para documentación completa del CLI.

## Contenido

### Scripts de Creación de Datos

- **`crear_clase_alumnos.py`** - Crear clase con alumnos (acceso directo BBDD)
  - ✅ Alternativa CLI: `cli.py users import-csv --clase`

- **`crear_profesor.py`** - Crear profesor (acceso directo BBDD)
  - ✅ Alternativa CLI: `cli.py users create-profesor`

- **`generar_datos_directos.py`** - Generar datos de prueba (acceso directo BBDD)
  - ✅ Alternativa CLI: `cli.py users import-csv` + API endpoints

- **`generar_datos_prueba.py`** - Generar datos de prueba (acceso directo BBDD)
  - ✅ Alternativa CLI: `cli.py users import-csv` + API endpoints

### Scripts de Gestión

- **`crear_eventos.py`** - Crear eventos (acceso directo BBDD)
  - ⚠️ No hay alternativa CLI aún - usar endpoint API si existe

- **`listar_eventos.py`** - Listar eventos (acceso directo BBDD)
  - ⚠️ No hay alternativa CLI aún - usar endpoint API si existe

### Scripts de Migración

- **`migrar_codigos_clases.py`** - Migración de códigos de clase
  - ⚠️ Migración única ya ejecutada

- **`migrate_complete_partidas.py`** - Migración de partidas completas
  - ⚠️ Migración única ya ejecutada

## Requisitos para usar estos scripts

```bash
# Necesitas configurar credenciales de BBDD
export DATABASE_URL="postgresql://user:password@host:port/database"

# O configurar en .env del proyecto principal:
DATABASE_URL=postgresql://user:password@host:port/database
```

## ⚠️ Advertencias

- **Sin auditoría:** Estos scripts no registran en `audit_logs`
- **Sin validación:** Pueden romper la integridad de datos
- **Riesgo alto:** Pueden causar problemas en producción
- **Difícil debug:** No hay trazabilidad de errores

## 🎯 Filosofía

> **"Si puedes hacerlo vía API, hazlo vía API"**

Estos scripts solo deberían usarse en casos excepcionales de emergencia.
