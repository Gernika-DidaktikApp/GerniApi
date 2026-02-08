# Code Linting and Formatting

Este proyecto usa tres herramientas para mantener la calidad del código:

## Herramientas

### 1. **Black** - Formateador de código
- Formatea automáticamente el código Python
- Línea máxima: 100 caracteres
- Estilo consistente y sin configuración

### 2. **isort** - Ordenador de imports
- Ordena y organiza los imports automáticamente
- Compatible con Black
- Agrupa imports en secciones estándar

### 3. **Ruff** - Linter ultra-rápido
- Reemplaza a flake8, pylint, y otros
- Detecta errores comunes y malas prácticas
- Verifica estilo PEP 8
- Muy rápido (escrito en Rust)

## Instalación

Instala las herramientas de desarrollo:

```bash
make install-dev
# o manualmente:
pip install -r requirements-dev.txt
```

## Uso Local

### Verificar código (sin modificar)

```bash
make lint
```

Esto ejecuta:
- `black --check` - Verifica formato
- `isort --check` - Verifica imports
- `ruff check` - Verifica errores y estilo

### Formatear código automáticamente

```bash
make format
```

Esto ejecuta:
- `black app tests` - Formatea el código
- `isort app tests` - Ordena los imports

**Recomendación:** Ejecuta `make format` antes de cada commit.

## Integración con CI

Los linters se ejecutan automáticamente en GitHub Actions en cada push o pull request.

El job `lint` verifica:
1. Formato con Black
2. Orden de imports con isort
3. Calidad de código con Ruff

**Si algún linter falla, el CI no pasará.** Asegúrate de ejecutar `make lint` o `make format` localmente antes de hacer push.

## Configuración

La configuración de los linters está en `pyproject.toml`:

- **Black**: Línea de 100 caracteres, Python 3.11+
- **isort**: Perfil "black" para compatibilidad
- **Ruff**: Reglas de pycodestyle, pyflakes, isort, bugbear, y más

## Integración con IDE

### VS Code

Agrega a tu `.vscode/settings.json`:

```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

### PyCharm

1. Settings → Tools → Black
2. Enable "On save"
3. Settings → Tools → External Tools → Add Ruff

## Pre-commit Hook (Opcional)

Para ejecutar los linters automáticamente antes de cada commit:

```bash
pip install pre-commit
pre-commit install
```

Crea `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.0.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
```

## Solución de Problemas

### "Black would reformat file.py"

Ejecuta: `make format` o `black app tests`

### "isort would reformat file.py"

Ejecuta: `make format` o `isort app tests`

### Errores de Ruff

Lee el mensaje de error. Algunas opciones:

1. **Arreglar el código** - La mayoría de errores son válidos
2. **Usar --fix** - `ruff check --fix app` (arregla automáticamente)
3. **Ignorar línea** - Agrega `# noqa: E501` al final de la línea (úsalo con moderación)

#### E402: Module level import not at top of file

**Cuándo es correcto ignorarlo**:

En `tests/conftest.py`, los imports deben venir DESPUÉS de configurar los mocks:

```python
# ruff: noqa: E402
import sys
from unittest.mock import MagicMock

# Mock de fastapi_limiter (debe ser ANTES de importar app)
sys.modules["fastapi_limiter"] = fastapi_limiter_mock

# Imports de la app (deben ser DESPUÉS del mock)
from app.main import app
from app.database import Base, get_db
```

**Por qué**: Los mocks de módulos deben configurarse antes de importar el código que los usa. El comentario `# ruff: noqa: E402` al inicio del archivo desactiva este error para todo el archivo.

#### SIM102: Use a single if statement instead of nested if statements

**Error**:
```python
# ❌ Mal
if usuario_data.id_clase:
    if not self.clase_repo.exists(usuario_data.id_clase):
        raise HTTPException(404, "Clase no encontrada")
```

**Solución**:
```python
# ✅ Bien
if usuario_data.id_clase and not self.clase_repo.exists(usuario_data.id_clase):
    raise HTTPException(404, "Clase no encontrada")
```

**Nota**: Ruff sugiere combinar condiciones anidadas con `and` cuando sea posible para mayor legibilidad.

## Comandos Útiles

```bash
# Ver ayuda del Makefile
make

# Verificar solo un archivo
black --check app/main.py
ruff check app/main.py

# Formatear solo un archivo
black app/main.py
isort app/main.py

# Ver diferencias sin aplicar cambios
black --diff app
isort --diff app

# Arreglar automáticamente errores de Ruff (cuando sea posible)
ruff check --fix app tests
```

## Más Información

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
