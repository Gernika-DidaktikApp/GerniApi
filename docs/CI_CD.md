# CI/CD - Integración Continua

Este proyecto utiliza **GitHub Actions** para ejecutar tests automáticamente en cada push y pull request.

## 🚀 Cómo Funciona

El workflow de CI se ejecuta automáticamente cuando:
- Haces `push` a las ramas `main` o `develop`
- Creas o actualizas un Pull Request hacia `main` o `develop`

## 📋 Qué Hace el CI

1. **Checkout del código**: Descarga el código del repositorio
2. **Configura Python**: Instala Python 3.11 y 3.12 (matrix de versiones)
3. **Cache de dependencias**: Guarda las dependencias en caché para builds más rápidos
4. **Instala dependencias**: Ejecuta `pip install -r requirements.txt`
5. **Ejecuta tests**: Corre `pytest -v --tb=short`
6. **Genera reporte de cobertura**: Solo en Python 3.12
7. **Sube reporte a artifacts**: Disponible para descarga en GitHub

## 📊 Ver Resultados

### En GitHub

1. Ve a tu repositorio en GitHub
2. Click en la pestaña **Actions**
3. Verás todos los workflows ejecutados
4. Click en cualquier run para ver detalles

### Badge de Estado (Opcional)

Puedes añadir un badge al README para mostrar el estado del CI:

```markdown
![Tests](https://github.com/TU_USUARIO/TU_REPO/workflows/Tests/badge.svg)
```

## 🔍 Revisar Cobertura de Tests

El reporte de cobertura se genera automáticamente y se puede descargar:

1. Ve al workflow run en GitHub Actions
2. Scroll hasta la sección "Artifacts"
3. Descarga `coverage-report`
4. Abre `index.html` en tu navegador

## 🛠️ Configuración del Workflow

El archivo de configuración está en:
```
.github/workflows/tests.yml
```

### Características

- **Matrix de Python**: Tests en Python 3.11 y 3.12
- **Cache inteligente**: Las dependencias se cachean para builds más rápidos
- **Base de datos de test**: Usa SQLite en memoria (no requiere PostgreSQL)
- **Reportes de cobertura**: Generados solo en Python 3.12
- **Artifacts**: Reportes guardados por 30 días

### Personalizar el Workflow

#### Cambiar versiones de Python

```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12', '3.13']  # Añadir más versiones
```

#### Cambiar ramas vigiladas

```yaml
on:
  push:
    branches: [ main, develop, staging ]  # Añadir más ramas
```

#### Añadir más pasos

```yaml
- name: Lint con flake8
  run: |
    pip install flake8
    flake8 app/ --max-line-length=120
```

## 🧪 Testing Local antes de Push

Para asegurar que tus tests pasarán en CI:

```bash
# Ejecutar los mismos tests que CI
pytest -v --tb=short

# Con reporte de cobertura
pytest --cov=app --cov-report=html
```

## ⚠️ Manejo de Fallos

### Si los tests fallan en CI

1. **Ver logs**: Click en el workflow fallido → Click en el job "test"
2. **Identificar el error**: Los logs mostrarán qué test falló y por qué
3. **Reproducir localmente**:
   ```bash
   pytest tests/test_archivo.py::TestClass::test_fallido -v
   ```
4. **Corregir y push**: Una vez corregido, push automáticamente ejecutará CI otra vez

### Errores Comunes

#### Error: "No module named 'app'"
**Causa**: PYTHONPATH no configurado
**Solución**: Ya está configurado en el workflow con `PYTHONPATH: ${{ github.workspace }}`

#### Error: "Database connection failed"
**Causa**: Intentando conectar a PostgreSQL
**Solución**: Los tests deben usar SQLite en memoria (configurado en `tests/conftest.py`)

#### Error: "ImportError"
**Causa**: Dependencia faltante en requirements.txt
**Solución**: Añadir la dependencia a requirements.txt

## 🔒 Variables de Entorno en CI

El workflow configura automáticamente las variables de entorno necesarias:

```yaml
env:
  DATABASE_URL: "sqlite:///:memory:"
  SECRET_KEY: "test-secret-key-for-ci-only-not-for-production"
  PYTHONPATH: ${{ github.workspace }}
```

**Notas importantes:**
- `DATABASE_URL`: Apunta a SQLite en memoria (los tests no usan PostgreSQL)
- `SECRET_KEY`: Clave de prueba solo para CI (no es la de producción)
- `PYTHONPATH`: Permite importar el módulo `app` correctamente

### Añadir más variables de entorno

Si necesitas añadir variables de entorno adicionales:

```yaml
- name: Run tests with pytest
  run: |
    pytest -v --tb=short
  env:
    DATABASE_URL: "sqlite:///:memory:"
    SECRET_KEY: "test-secret-key-for-ci-only-not-for-production"
    MI_VARIABLE: valor
    MI_SECRET: ${{ secrets.MI_SECRET }}  # Usar GitHub Secrets
```

### Configurar Secrets en GitHub

1. Ve a tu repositorio → Settings
2. Click en "Secrets and variables" → "Actions"
3. Click en "New repository secret"
4. Añade el nombre y valor del secret

## 📈 Mejoras Futuras

Puedes extender el CI con:

- **Linting**: flake8, black, mypy
- **Security scanning**: bandit, safety
- **Deployment automático**: Deploy a Railway/Heroku después de tests exitosos
- **Notificaciones**: Slack, Discord, email
- **Performance tests**: Benchmarks de velocidad

### Ejemplo: Añadir Linting

```yaml
- name: Lint with flake8
  run: |
    pip install flake8
    flake8 app/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Ejemplo: Deploy Automático

```yaml
- name: Deploy to Railway
  if: github.ref == 'refs/heads/main' && matrix.python-version == '3.12'
  run: |
    # Comandos de deploy aquí
  env:
    RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## 📚 Recursos

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)

## ✅ Checklist de CI

Antes de mergear tu PR, asegúrate de que:

- [ ] Todos los tests pasan en CI
- [ ] Cobertura de tests es adecuada
- [ ] No hay errores de linting (si está configurado)
- [ ] El código sigue las convenciones del proyecto
- [ ] Has añadido tests para nuevas funcionalidades

---

**Nota**: El CI está configurado para no bloquear merges, pero es altamente recomendable que todos los tests pasen antes de mergear a `main`.
