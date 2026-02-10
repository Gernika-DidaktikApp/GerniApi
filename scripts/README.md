# 🔧 GerniBide CLI - Herramienta Administrativa

CLI completo para la gestión administrativa de GerniBide que usa **exclusivamente la API REST**.

**No requiere acceso directo a la base de datos**, solo necesitas una API Key.

## 📋 Tabla de Contenidos

- [¿Por qué este CLI?](#-por-qué-este-cli)
- [Estructura del Directorio](#-estructura-del-directorio)
- [Configuración Inicial](#-configuración-inicial)
- [Comandos Disponibles](#-comandos-disponibles)
- [Casos de Uso Comunes](#-casos-de-uso-comunes)
- [Seguridad](#-seguridad)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 ¿Por qué este CLI?

### Problema: Acceso Directo a Base de Datos

❌ **Riesgos del acceso directo:**
- Requiere credenciales de base de datos (inseguro compartirlas)
- Sin auditoría de quién hizo qué
- Sin validación de permisos
- Fácil cometer errores en producción
- Difícil de compartir entre equipo

### Solución: CLI vía API REST

✅ **Ventajas de usar la API:**
- **Solo requiere API Key** - No necesitas credenciales de BD
- **Auditoría completa** - Todo queda registrado en audit_logs
- **Respeta permisos** - La API valida cada operación
- **Seguro** - No puedes romper la BD por error
- **Compartible** - Cualquiera con API Key puede usarlo

### Comparación

| Característica | Acceso Directo BD | CLI vía API ✅ |
|----------------|-------------------|----------------|
| Requiere credenciales BD | ✅ Sí (inseguro) | ❌ No |
| Requiere API Key | ❌ No | ✅ Sí |
| Auditoría de operaciones | ❌ No | ✅ Sí (audit_logs) |
| Respeta permisos API | ❌ No | ✅ Sí |
| Riesgo en producción | ⚠️ ALTO | ✅ BAJO |
| Puede usarse remotamente | ❌ No (necesitas VPN/SSH) | ✅ Sí |

### ⚠️ Casos Excepcionales (Acceso Directo a BBDD)

**Este CLI NO usa acceso directo a la base de datos.** Sin embargo, puede haber casos excepcionales donde la API no ofrezca la funcionalidad necesaria.

**Si necesitas hacer algo que la API no permite:**

1. **Primero pregunta:** ¿Debería existir un endpoint de API para esto?
   - Si la respuesta es "sí", mejor crear el endpoint en la API
   - Mantiene la auditoría y seguridad consistentes

2. **Solo si es verdaderamente excepcional:**
   - Usa un script SQL separado (no este CLI)
   - **Requiere credenciales de base de datos** (solicítalas al administrador)
   - Documenta claramente qué hiciste y por qué
   - Ejemplo: migraciones de datos complejas, operaciones de mantenimiento de BBDD

**Filosofía:** Si puedes hacerlo vía API, hazlo vía API. El acceso directo a BBDD debe ser la última opción.

---

## 📁 Estructura del Directorio

```
scripts/
├── cli.py                    # 🎯 CLI principal (usa solo API)
├── .env.example              # Plantilla de configuración
├── README.md                 # Esta documentación
│
├── commands/                 # Comandos del CLI
│   ├── users_commands.py     # Gestión de usuarios/profesores
│   └── export_commands.py    # Exportación de datos
│
├── utils/                    # Utilidades compartidas
│   └── api_client.py         # Cliente HTTP para la API
│
└── legacy/                   # ⚠️ Scripts antiguos (acceso directo BBDD)
    ├── README.md             # Documentación de scripts legacy
    ├── crear_*.py            # Scripts de creación de datos
    ├── generar_*.py          # Generadores de datos de prueba
    └── migrar_*.py           # Scripts de migración única
```

### ¿Qué usar?

| Necesitas | Usa | Ubicación |
|-----------|-----|-----------|
| Gestión diaria de usuarios/datos | **CLI principal** | `cli.py` |
| Exportar datos | **CLI principal** | `cli.py export` |
| Crear profesores/alumnos | **CLI principal** | `cli.py users` |
| Scripts antiguos con BBDD directa | ⚠️ Legacy (evitar) | `legacy/` |

---

## ⚙️ Configuración Inicial

### 1. Instalar Dependencias

```bash
cd /path/to/GerniApi
pip install httpx rich click pandas python-dotenv
```

O usando requirements:

```bash
pip install -r requirements-dev.txt
```

### 2. Crear Archivo de Configuración

```bash
cd scripts
cp .env.example .env
```

### 3. Configurar `.env`

Edita el archivo `scripts/.env`:

**Para desarrollo local:**
```bash
# URL de la API (local)
API_URL=http://localhost:8000

# API Key (misma que en .env principal del servidor)
# NOTA: Solo necesitas esto, NO necesitas credenciales de base de datos
API_KEY=tu-api-key-de-desarrollo

# Opcional: Modo solo lectura
CLI_READ_ONLY=false

# Entorno
ENVIRONMENT=development
```

**Para producción:**
```bash
# URL de la API (Railway u otro hosting)
API_URL=https://tu-api.railway.app

# API Key de producción (solicítala al administrador)
# IMPORTANTE: Solo necesitas la API Key, NO credenciales de BBDD
API_KEY=prod-api-key-super-secreta

# ⚠️ IMPORTANTE: Modo solo lectura por defecto en producción
CLI_READ_ONLY=true

# Entorno
ENVIRONMENT=production
```

> 💡 **Nota Importante:** Este CLI solo requiere la API Key. **No necesitas** credenciales de base de datos (usuario, contraseña, host, etc.). Todo se hace vía API.

### 4. Verificar Configuración

```bash
python scripts/cli.py config
```

Deberías ver algo como:

```
⚙️  Configuración Actual

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Variable           ┃ Valor                                        ┃  Estado  ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ API_URL            │ http://localhost:8000                        │    ✅    │
│ API_KEY            │ dev-key-1...                                 │    ✅    │
│ CLI_READ_ONLY      │ false                                        │    ✏️    │
│ ENVIRONMENT        │ development                                  │    🟢    │
└────────────────────┴──────────────────────────────────────────────┴──────────┘
```

### 5. Verificar Conexión con API

```bash
python scripts/cli.py users check-api
```

Si todo está bien, verás:

```
🔍 Verificando conexión con la API...

╭──────────────── Conexión OK ─────────────────╮
│ 🌐 URL:     http://localhost:8000            │
│ 🔑 API Key: dev-key-1...                     │
│ ✅ Estado:  healthy                          │
╰───────────────────────────────────────────────╯
```

---

## 📋 Comandos Disponibles

### 🔍 Configuración y Diagnóstico

#### Ver configuración actual

```bash
python scripts/cli.py config
```

Muestra todas las variables de entorno configuradas y su estado.

#### Verificar conexión con API

```bash
python scripts/cli.py users check-api
```

Prueba la conexión y autenticación con la API.

---

### 👥 Gestión de Usuarios y Profesores

#### Listar usuarios

```bash
# Listar primeros 20 usuarios
python scripts/cli.py users list

# Listar solo usuarios
python scripts/cli.py users list --type usuarios --limit 50

# Listar solo profesores
python scripts/cli.py users list --type profesores

# Listar todos
python scripts/cli.py users list --type all --limit 100
```

**Salida:**
```
👥 Listado de usuarios

┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┓
┃ Username   ┃ Nombre             ┃ Clase   ┃   Score ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━┩
│ alumno01   │ Juan Pérez         │ ABC123  │     150 │
│ alumno02   │ María García       │ ABC123  │     200 │
│ alumno03   │ Pedro López        │ DEF456  │     100 │
└────────────┴────────────────────┴─────────┴─────────┘

Mostrando primeros 20 usuarios
```

#### Crear profesor

**Interactivo:**
```bash
python scripts/cli.py users create-profesor
```

Te pedirá los datos paso a paso:
```
👨‍🏫 Creando profesor...

Username: prof.garcia
Password: 
Repeat for confirmation: 
Nombre: María
Apellido: García
```

**Con parámetros:**
```bash
python scripts/cli.py users create-profesor \
  --username prof.garcia \
  --password SecurePass123 \
  --nombre María \
  --apellido García \
  --admin
```

**Salida:**
```
👨‍🏫 Creando profesor...

╭────────── ✅ Profesor Creado ───────────╮
│ 👤 Username: prof.garcia                │
│ 📝 Nombre:   María García               │
│ 🔑 ID:       550e8400-e29b-41d4-a716... │
│ ⭐ Admin:    Sí                         │
╰─────────────────────────────────────────╯
```

#### Crear usuario estudiante

```bash
# Con código de clase
python scripts/cli.py users create-usuario \
  --username alumno01 \
  --nombre Juan \
  --apellido Pérez \
  --clase ABC123

# Sin clase
python scripts/cli.py users create-usuario \
  --username alumno02 \
  --nombre María \
  --apellido García

# Con password personalizado
python scripts/cli.py users create-usuario \
  --username alumno03 \
  --password MiPassword123 \
  --nombre Pedro \
  --apellido López
```

> 💡 **Nota:** Si no se especifica `--password`, se usa el username como contraseña.

#### Eliminar usuario

```bash
python scripts/cli.py users delete <usuario-id>
```

Ejemplo:
```bash
python scripts/cli.py users delete 550e8400-e29b-41d4-a716-446655440000
```

Te pedirá confirmación:
```
⚠️  Eliminar usuario: 550e8400-e29b-41d4-a716-446655440000

¿Estás seguro de eliminar el usuario '550e8400-e29b-41d4-a716-446655440000'? [y/N]:
```

#### Importar usuarios desde CSV

**1. Crear archivo CSV:**

Crea un archivo `usuarios.csv`:
```csv
username,nombre,apellido,password
alumno01,Juan,Pérez,password123
alumno02,María,García,password123
alumno03,Pedro,López,password123
alumno04,Ana,Martínez,password123
alumno05,Luis,Rodríguez,password123
```

> 💡 **Nota:** Si no incluyes la columna `password`, se usará el username como contraseña.

**2. Importar:**

```bash
# Importar sin clase
python scripts/cli.py users import-csv usuarios.csv

# Importar asignando a una clase
python scripts/cli.py users import-csv usuarios.csv --clase ABC123
```

**Salida:**
```
📥 Importando usuarios desde usuarios.csv...

Usuarios a importar: 5
Clase asignada: ABC123

✅ 5 usuarios importados exitosamente
```

> ⚠️ **Importante:** La importación es transaccional. Si un usuario falla (ej: username duplicado), **ninguno** se crea.

---

### 📤 Exportación de Datos

#### Exportar un modelo específico

```bash
# Exportar usuarios a CSV
python scripts/cli.py export data usuarios --format csv

# Exportar profesores a JSON
python scripts/cli.py export data profesores --format json

# Exportar partidas con límite
python scripts/cli.py export data partidas --limit 500

# Exportar a archivo específico
python scripts/cli.py export data usuarios \
  --format csv \
  --output ./mis-datos/usuarios.csv
```

**Modelos disponibles:**
- `usuarios` - Usuarios estudiantes
- `profesores` - Profesores/docentes
- `clases` - Clases asignadas
- `actividades` - Actividades educativas
- `partidas` - Partidas de juego
- `puntos` - Puntos del mapa

**Salida:**
```
📤 Exportando usuarios...

✓ 150 registros obtenidos

Exportando a CSV...

╭──────── ✅ Exportación Completada ─────────╮
│ 📁 Archivo:   exports/usuarios_20260210... │
│ 📊 Registros: 150                          │
│ 📦 Tamaño:    45.32 KB                     │
│ 📄 Formato:   CSV                          │
╰────────────────────────────────────────────╯
```

#### Exportar todos los modelos

```bash
# Exportar todo a CSV
python scripts/cli.py export all --format csv

# Exportar todo a JSON en directorio específico
python scripts/cli.py export all \
  --format json \
  --output ./backup-completo
```

**Salida:**
```
📤 Exportando todos los modelos...

Exportando usuarios...
Exportando profesores...
Exportando clases...
Exportando actividades...
Exportando partidas...
Exportando puntos...

┏━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Modelo      ┃ Registros ┃ Archivo                  ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ usuarios    │       150 │ usuarios_20260210...     │
│ profesores  │        10 │ profesores_20260210...   │
│ clases      │         5 │ clases_20260210...       │
│ actividades │        45 │ actividades_20260210...  │
│ partidas    │       200 │ partidas_20260210...     │
│ puntos      │        15 │ puntos_20260210...       │
└─────────────┴───────────┴──────────────────────────┘

✅ Exportación completada
Directorio: /path/to/exports
```

---

## 🎯 Casos de Uso Comunes

### Caso 1: Crear una nueva clase con alumnos

**Escenario:** Inicio de curso, necesitas crear una clase nueva con 30 alumnos.

**Tiempo estimado:** 5 minutos

**Pasos:**

1. **Crear el profesor (si no existe):**
```bash
python scripts/cli.py users create-profesor \
  --username prof.garcia \
  --password Garcia2024! \
  --nombre María \
  --apellido García
```

**Salida:**
```
👨‍🏫 Creando profesor...

╭────────── ✅ Profesor Creado ───────────╮
│ 👤 Username: prof.garcia                │
│ 📝 Nombre:   María García               │
│ 🔑 ID:       abc123...                  │
│ ⭐ Admin:    No                         │
╰─────────────────────────────────────────╯
```

2. **Crear la clase en la web** (por el profesor):
   - El profesor inicia sesión en el dashboard web con `prof.garcia`
   - Va a "Clases" → "Nueva Clase"
   - Crea la clase "1º ESO A"
   - Obtiene el código de clase (ej: `ABC123`)

3. **Preparar CSV de alumnos:**

Crea un archivo `alumnos_1eso_a.csv`:
```csv
username,nombre,apellido,password
alu2024001,Juan,Pérez,
alu2024002,María,García,
alu2024003,Pedro,López,
... (27 alumnos más)
```

> 💡 Si omites la columna `password`, se usará el username como contraseña.

4. **Importar alumnos:**
```bash
python scripts/cli.py users import-csv alumnos_1eso_a.csv --clase ABC123
```

**Salida:**
```
📥 Importando usuarios desde alumnos_1eso_a.csv...

Usuarios a importar: 30
Clase asignada: ABC123

✅ 30 usuarios importados exitosamente
```

5. **Verificar** (opcional):
```bash
python scripts/cli.py users list --type usuarios --limit 50
```

✅ **Resultado:** 30 alumnos creados, asignados a la clase y listos para usar. Total: **menos de 5 minutos**.

---

### Caso 2: Exportar datos para análisis

**Escenario:** Fin de trimestre, necesitas analizar el rendimiento de los alumnos.

**Pasos:**

1. **Exportar todo a CSV:**
```bash
python scripts/cli.py export all --format csv --output ./analisis-trimestre1
```

2. **Abrir en Excel/Google Sheets:**
   - `usuarios.csv` - Datos de alumnos
   - `partidas.csv` - Partidas jugadas
   - `progreso.csv` - Progreso en actividades

3. **Crear gráficos y análisis** directamente en Excel.

✅ **Resultado:** Datos listos para analizar sin tocar la base de datos.

---

### Caso 3: Backup antes de cambios importantes

**Escenario:** Vas a hacer cambios importantes en producción.

**Pasos:**

1. **Exportar todo antes del cambio:**
```bash
# Configurar producción en .env
API_URL=https://api-prod.railway.app
API_KEY=prod-api-key

# Exportar
python scripts/cli.py export all \
  --format json \
  --output ./backup-pre-cambio-$(date +%Y%m%d)
```

2. **Realizar los cambios** con confianza.

3. **Si algo sale mal**, tienes todos los datos exportados.

✅ **Resultado:** Respaldo completo de datos antes de cambios críticos.

---

### Caso 4: Migrar usuarios entre clases

**Escenario:** Necesitas pasar alumnos de una clase a otra.

**Pasos:**

1. **Exportar usuarios de la clase origen:**
```bash
python scripts/cli.py export data usuarios --format csv
```

2. **Filtrar en Excel** los usuarios que quieres migrar.

3. **Actualizar** via web o API los usuarios necesarios.

✅ **Resultado:** Control total sobre la migración con datos exportados.

---

## 🛡️ Seguridad

### Protección de Entorno

#### Modo Solo Lectura

Para prevenir modificaciones accidentales en producción:

**En `.env`:**
```bash
CLI_READ_ONLY=true
```

Con esto activado:
- ✅ **Permitido:** `list`, `export`, `check-api`, `config`
- ❌ **Bloqueado:** `create-*`, `delete`, `import-csv`

**Uso:**
```bash
# Exportar datos (permitido)
python scripts/cli.py export data usuarios

# Intentar crear usuario (bloqueado)
python scripts/cli.py users create-usuario
# Error: Operación bloqueada en modo solo lectura
```

#### Variables de Entorno Requeridas

```bash
# OBLIGATORIAS
API_URL=<url-de-tu-api>
API_KEY=<tu-api-key-secreta>

# OPCIONALES (recomendadas)
CLI_READ_ONLY=true              # true para producción
ENVIRONMENT=production          # development o production
```

### Buenas Prácticas

#### ✅ DO (Hacer)

1. **Usar diferentes API Keys para desarrollo y producción**
   ```bash
   # .env desarrollo
   API_KEY=dev-key-123
   
   # .env producción
   API_KEY=prod-key-super-secreta-456
   ```

2. **Habilitar modo solo lectura en producción por defecto**
   ```bash
   CLI_READ_ONLY=true
   ```

3. **Exportar datos regularmente**
   ```bash
   # Cron job semanal
   0 0 * * 0 cd /path && python scripts/cli.py export all --format json
   ```

4. **Rotar API Keys regularmente** (cada 3-6 meses)

5. **Documentar quién tiene acceso** a cada API Key

#### ❌ DON'T (No hacer)

1. **Nunca** compartir el archivo `.env` en Git
   ```bash
   # Ya está en .gitignore
   scripts/.env
   ```

2. **Nunca** usar la misma API Key para desarrollo y producción

3. **Nunca** ejecutar operaciones destructivas sin confirmación
   ```bash
   # Mal ❌
   python scripts/cli.py users delete $ID --force
   
   # Bien ✅
   python scripts/cli.py users delete $ID
   # (te pedirá confirmación)
   ```

4. **Nunca** deshabilitar read-only en producción sin razón válida

---

## 🐛 Troubleshooting

### Error: "API_KEY no configurada"

**Causa:** No existe el archivo `.env` o la variable `API_KEY` está vacía.

**Solución:**
```bash
cd scripts

# Verificar si existe .env
ls -la .env

# Si no existe, copiar desde ejemplo
cp .env.example .env

# Editar y agregar API_KEY
nano .env
```

---

### Error: "Connection refused"

**Causa:** La API no está corriendo o la URL es incorrecta.

**Diagnóstico:**
```bash
# Verificar URL configurada
cat scripts/.env | grep API_URL

# Probar conexión manual
curl http://localhost:8000/health
```

**Soluciones:**

1. **Si es local:** Levantar la API
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Si es producción:** Verificar que la URL sea correcta
   ```bash
   # En .env
   API_URL=https://tu-api.railway.app  # Sin barra final
   ```

---

### Error: "401 Unauthorized"

**Causa:** La API Key es incorrecta o no tiene permisos.

**Diagnóstico:**
```bash
# Ver API Key configurada en CLI
cat scripts/.env | grep API_KEY

# Ver API Key del servidor
cat .env | grep API_KEY

# Deben coincidir
```

**Solución:**
```bash
# Copiar la API Key correcta del .env principal al .env del CLI
nano scripts/.env
# Pegar la API_KEY correcta
```

---

### Error: "No module named 'httpx'"

**Causa:** Dependencias no instaladas.

**Solución:**
```bash
pip install httpx rich click pandas python-dotenv

# O instalar todo
pip install -r requirements-dev.txt
```

---

### Datos exportados están vacíos

**Causa:** El límite por defecto es 1000 registros.

**Diagnóstico:**
```bash
# Ver cuántos registros hay
python scripts/cli.py users list --limit 5
```

**Solución:**
```bash
# Aumentar límite en la exportación
python scripts/cli.py export data usuarios --limit 5000
```

---

### Import CSV falla con "username duplicado"

**Causa:** Algún username ya existe en la base de datos.

**Diagnóstico:**
El error te dirá qué username está duplicado:
```
Error: El username 'alumno01' ya existe
```

**Solución:**
1. Verificar en el CSV que no haya duplicados
2. Cambiar los usernames duplicados
3. O eliminar las filas de usuarios que ya existen

---

### La API no ofrece la funcionalidad que necesito

**Escenario:** Necesitas hacer una operación que no está disponible en la API.

**Opciones:**

1. **Opción Preferida - Crear el endpoint en la API:**
   - Abre un issue describiendo la funcionalidad necesaria
   - Si tienes acceso al código, implementa el endpoint
   - Beneficios: mantiene auditoría, seguridad y puede reutilizarse

2. **Opción Temporal - Script SQL separado:**
   - Solo para casos excepcionales de emergencia
   - Requiere credenciales de BBDD (solicítalas al administrador)
   - Documenta qué hiciste, cuándo y por qué
   - Crea un ticket para añadir la funcionalidad a la API después

**Ejemplos de casos legítimos para acceso directo:**
- Migraciones de datos complejas (renombrar columnas, cambiar tipos)
- Operaciones de mantenimiento de BBDD (VACUUM, REINDEX)
- Debug de problemas de corrupción de datos
- Operaciones SQL avanzadas no disponibles vía ORM

**Recuerda:** El acceso directo a BBDD debe ser la **última opción**, no la primera.

---

## 📚 Referencia Rápida

### Tabla de Comandos

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| **Configuración** |
| `config` | Ver configuración actual | `python scripts/cli.py config` |
| `users check-api` | Verificar conexión con API | `python scripts/cli.py users check-api` |
| **Usuarios** |
| `users list` | Listar usuarios/profesores | `python scripts/cli.py users list --type all --limit 50` |
| `users create-profesor` | Crear nuevo profesor | `python scripts/cli.py users create-profesor` |
| `users create-usuario` | Crear nuevo estudiante | `python scripts/cli.py users create-usuario --clase ABC123` |
| `users import-csv` | Importar usuarios desde CSV | `python scripts/cli.py users import-csv alumnos.csv --clase ABC123` |
| `users delete` | Eliminar usuario por ID | `python scripts/cli.py users delete <usuario-id>` |
| **Exportación** |
| `export data` | Exportar un modelo | `python scripts/cli.py export data usuarios --format csv` |
| `export all` | Exportar todos los modelos | `python scripts/cli.py export all --format json` |

### Comandos por Frecuencia de Uso

**Uso Diario:**
```bash
# Verificar estado
python scripts/cli.py users check-api

# Listar usuarios
python scripts/cli.py users list --limit 50
```

**Inicio de Curso:**
```bash
# Crear profesores
python scripts/cli.py users create-profesor

# Importar alumnos masivamente
python scripts/cli.py users import-csv alumnos_1eso.csv --clase ABC123
```

**Fin de Trimestre:**
```bash
# Exportar todo para análisis
python scripts/cli.py export all --format csv --output ./analisis-trim1
```

**Backup Regular:**
```bash
# Exportar todo a JSON
python scripts/cli.py export all --format json --output ./backup-$(date +%Y%m%d)
```

### Ayuda Integrada

```bash
# Ayuda general
python scripts/cli.py --help

# Ayuda de usuarios
python scripts/cli.py users --help

# Ayuda de exportación
python scripts/cli.py export --help

# Ayuda de comando específico
python scripts/cli.py users create-profesor --help
```

### Argumentos Comunes

| Argumento | Descripción | Valores |
|-----------|-------------|---------|
| `--type` / `-t` | Tipo de usuarios | `usuarios`, `profesores`, `all` |
| `--limit` / `-l` | Límite de registros | Número (ej: `50`, `100`, `1000`) |
| `--format` / `-f` | Formato de exportación | `csv`, `json` |
| `--output` / `-o` | Archivo/directorio de salida | Ruta (ej: `./backups/datos.csv`) |
| `--clase` | Código de clase | Código (ej: `ABC123`) |
| `--admin` | Marcar como admin (profesores) | Flag (sin valor) |

---

## 🏗️ Arquitectura y Funcionamiento

### Flujo de Operaciones

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│             │      │              │      │              │      │              │
│  CLI User   │─────▶│  API Client  │─────▶│   API REST   │─────▶│   Database   │
│  (tu)       │      │  (httpx)     │      │  (FastAPI)   │      │  (Postgres)  │
│             │      │              │      │              │      │              │
└─────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
      │                     │                      │                     │
      │                     │                      │                     │
      │  1. Comando         │                      │                     │
      │─────────────────────▶                      │                     │
      │                     │                      │                     │
      │                     │  2. HTTP Request     │                     │
      │                     │      + API Key       │                     │
      │                     │─────────────────────▶                      │
      │                     │                      │                     │
      │                     │                      │  3. SQL Query       │
      │                     │                      │─────────────────────▶
      │                     │                      │                     │
      │                     │                      │  4. SQL Result      │
      │                     │                      │◀─────────────────────
      │                     │                      │                     │
      │                     │  5. JSON Response    │                     │
      │                     │◀─────────────────────│                     │
      │                     │                      │                     │
      │  6. Pretty Output   │                      │                     │
      │◀─────────────────────                      │                     │
      │                     │                      │                     │
```

### Componentes

**1. CLI (`cli.py`)**
- Interfaz de línea de comandos con Click
- Muestra información bonita con Rich (tablas, paneles, colores)
- Maneja entrada del usuario y confirmaciones

**2. API Client (`utils/api_client.py`)**
- Wrapper sobre `httpx` para llamadas HTTP
- Maneja autenticación con API Key (header `X-API-Key`)
- Convierte errores HTTP a mensajes legibles

**3. API REST (`app/main.py`)**
- Valida permisos con API Key
- Aplica lógica de negocio
- Registra operaciones en `audit_logs`
- Ejecuta queries SQL vía SQLAlchemy ORM

**4. Base de Datos**
- PostgreSQL
- **No es accedida directamente por el CLI**
- Solo la API tiene credenciales

### Ventajas de esta Arquitectura

1. **Seguridad por capas:**
   - CLI solo conoce la API Key, no credenciales de BBDD
   - API valida cada operación
   - Base de datos está protegida detrás de la API

2. **Auditoría completa:**
   - Cada comando CLI → request HTTP → registro en audit_logs
   - Sabes quién hizo qué y cuándo

3. **Reutilizable:**
   - Los endpoints API pueden usarse desde:
     - CLI (este)
     - Dashboard web
     - Scripts automatizados
     - Otras aplicaciones

4. **Mantenible:**
   - Cambios en BBDD → solo actualizar API
   - CLI sigue funcionando sin cambios

### Archivos del Proyecto

```
scripts/
├── cli.py                      # Punto de entrada del CLI
├── .env                        # Configuración (API_URL, API_KEY)
├── .env.example                # Plantilla de configuración
├── commands/                   # Comandos agrupados por funcionalidad
│   ├── __init__.py
│   ├── users_commands.py       # Gestión de usuarios/profesores
│   └── export_commands.py      # Exportación de datos
└── utils/                      # Utilidades compartidas
    ├── __init__.py
    └── api_client.py           # Cliente HTTP para la API
```

### Extender el CLI

**Para añadir un nuevo comando:**

1. **Crear el endpoint en la API** (si no existe)
2. **Añadir método en `api_client.py`:**
   ```python
   def nueva_operacion(self, data: dict) -> dict:
       response = self.client.post("/api/v1/nueva-operacion", json=data)
       return self._handle_response(response)
   ```

3. **Crear comando en `commands/`:**
   ```python
   @click.command()
   def nuevo_comando():
       with APIClient() as api:
           resultado = api.nueva_operacion({...})
           console.print(f"✅ {resultado}")
   ```

4. **Registrar en `cli.py`:**
   ```python
   cli.add_command(nuevo_comando)
   ```

---

## 🤝 Contribuir

Si encuentras bugs o quieres agregar funcionalidades:

1. Documenta el problema/mejora
2. Crea un issue o PR
3. Asegúrate de pasar los linters:
   ```bash
   black scripts/
   ruff check scripts/
   ```

---

## ❓ FAQ (Preguntas Frecuentes)

### ¿Necesito credenciales de base de datos?

**No.** Este CLI solo requiere:
- URL de la API (`API_URL`)
- API Key (`API_KEY`)

No necesitas usuario, contraseña, host ni puerto de PostgreSQL.

---

### ¿Puedo usar esto en producción?

**Sí**, pero:
1. Habilita `CLI_READ_ONLY=true` en el `.env`
2. Solo desactívalo cuando necesites hacer cambios
3. Usa una API Key diferente a la de desarrollo
4. Exporta datos regularmente como backup

---

### ¿Qué pasa si necesito hacer algo que la API no permite?

1. **Primero:** Verifica si debería existir ese endpoint en la API
2. **Mejor:** Crea el endpoint en la API (mantiene seguridad)
3. **Último recurso:** Usa un script SQL separado con acceso directo a BBDD

**Regla:** Si puedes hacerlo vía API, hazlo vía API.

---

### ¿Puedo ejecutar el CLI desde otra máquina?

**Sí.** El CLI puede ejecutarse desde cualquier máquina que tenga:
- Python 3.10+
- Conexión a internet (si la API es remota)
- La API Key correcta

No necesitas estar en el servidor ni tener VPN.

---

### ¿Se registra lo que hago?

**Sí.** Todas las operaciones se registran en `audit_logs` de la base de datos:
- Qué hiciste
- Cuándo lo hiciste
- Qué API Key usaste

Esto es una **ventaja**, no una desventaja: permite auditoría y debugging.

---

### ¿Puedo automatizar tareas con el CLI?

**Sí.** Ejemplos:

**Backup diario:**
```bash
#!/bin/bash
# backup-diario.sh
cd /path/to/GerniApi
python scripts/cli.py export all --format json --output ./backups/$(date +%Y%m%d)
```

**Cron job para ejecutarlo a las 2 AM:**
```cron
0 2 * * * /path/to/backup-diario.sh
```

**Script de creación masiva:**
```bash
#!/bin/bash
# crear-clases-nuevas.sh
python scripts/cli.py users import-csv clase_1a.csv --clase ABC123
python scripts/cli.py users import-csv clase_1b.csv --clase DEF456
python scripts/cli.py users import-csv clase_2a.csv --clase GHI789
```

---

### ¿Funciona con la API en Railway/Vercel/otro hosting?

**Sí.** Solo configura la URL correcta en `.env`:

```bash
# Railway
API_URL=https://tu-proyecto.up.railway.app

# Render
API_URL=https://tu-proyecto.onrender.com

# Cualquier otro
API_URL=https://tu-dominio.com
```

---

### ¿Qué diferencia hay entre esto y psql/pgAdmin?

| Característica | psql/pgAdmin | Este CLI |
|----------------|--------------|----------|
| Acceso a BBDD | Directo | Vía API |
| Requiere credenciales BBDD | ✅ Sí | ❌ No |
| Auditoría | ❌ No | ✅ Sí |
| Validación de permisos | ❌ Manual | ✅ Automática |
| Riesgo de romper datos | ⚠️ Alto | ✅ Bajo |
| Comandos fáciles | ❌ SQL | ✅ Simples |
| Uso remoto | ❌ Requiere VPN | ✅ Directo |

**Usa psql/pgAdmin solo para:** operaciones de mantenimiento de BBDD, debug de bajo nivel, migraciones complejas.

**Usa este CLI para:** gestión diaria, creación de usuarios, exportación de datos, operaciones seguras.

---

### ¿Puedo compartir el CLI con otros profesores?

**Sí**, pero **nunca compartas el archivo `.env` completo**:

1. Comparte el código del CLI (todo menos `.env`)
2. Cada persona debe:
   - Copiar `.env.example` a `.env`
   - Solicitar su propia API Key al administrador
   - Configurar su `.env` individual

De esta forma:
- Cada persona tiene su propia API Key
- Puedes rastrear quién hizo qué
- Puedes revocar acceso individual sin afectar a otros

---

## 📄 Licencia

MIT License - Ver LICENSE en el repositorio principal.
