# Mejoras de Arquitectura y Desacople

## 🎯 Estado Actual vs Propuesto

### Arquitectura Actual

```
┌─────────────┐
│   Router    │ ← Endpoints FastAPI
├─────────────┤
│   Schema    │ ← Validación Pydantic
├─────────────┤
│ SQLAlchemy  │ ← Acceso directo a BD ❌
└─────────────┘
```

**Problemas**:
- Routers hacen queries SQL directamente
- Lógica de negocio mezclada con presentación
- Difícil de testear (dependencia fuerte de BD)
- Difícil de cambiar ORM o BD

### Arquitectura Propuesta (Clean Architecture)

```
┌──────────────────┐
│     Router       │ ← Endpoints FastAPI
│  (Presentation)  │
├──────────────────┤
│     Service      │ ← Lógica de negocio
│   (Business)     │
├──────────────────┤
│   Repository     │ ← Abstracción de datos
│  (Data Access)   │
├──────────────────┤
│   SQLAlchemy     │ ← ORM (intercambiable)
│     (ORM)        │
└──────────────────┘
```

**Ventajas**:
- ✅ Separación clara de responsabilidades
- ✅ Fácil de testear (mocks de repositorios)
- ✅ Fácil de cambiar BD/ORM
- ✅ Reutilización de lógica de negocio

## 🔧 Cambios Recomendados

### 1. Capa de Repositorios

**Crear para cada entidad**: `app/repositories/`

```python
# usuario_repository.py
class UsuarioRepository:
    def get_by_id(self, id: str) -> Optional[Usuario]:
        return self.db.query(Usuario).filter(Usuario.id == id).first()

    def exists_by_username(self, username: str) -> bool:
        return self.db.query(Usuario).filter(...).first() is not None
```

**Beneficios**:
- Abstrae SQLAlchemy
- Fácil de mockear en tests
- Cambiar ORM solo afecta repositorios

### 2. Capa de Servicios (Business Logic)

**Crear para cada dominio**: `app/services/`

```python
# usuario_service.py
class UsuarioService:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    def crear_usuario(self, data: UsuarioCreate) -> Usuario:
        # Validaciones de negocio
        if self.usuario_repo.exists_by_username(data.username):
            raise HTTPException(...)

        # Lógica de negocio
        usuario = Usuario(...)
        return self.usuario_repo.create(usuario)
```

**Beneficios**:
- Lógica de negocio centralizada
- Reutilizable (CLI, tests, otros endpoints)
- Independiente de FastAPI

### 3. Routers Delgados (Thin Controllers)

**Routers solo coordinan**:

```python
# ❌ ANTES (Router gordo - tiene lógica)
@router.post("/usuarios")
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    # ❌ Query directo
    existe = db.query(Usuario).filter(Usuario.username == data.username).first()
    if existe:
        raise HTTPException(...)

    # ❌ Lógica de negocio en router
    nuevo = Usuario(id=str(uuid.uuid4()), ...)
    db.add(nuevo)
    db.commit()
    return nuevo

# ✅ DESPUÉS (Router delgado - solo coordina)
@router.post("/usuarios")
def crear_usuario(
    data: UsuarioCreate,
    usuario_service: UsuarioService = Depends(get_usuario_service)
):
    return usuario_service.crear_usuario(data)
```

### 4. Dependency Injection Mejorado

**Crear factory functions**:

```python
# app/dependencies.py
def get_usuario_repository(db: Session = Depends(get_db)) -> UsuarioRepository:
    return UsuarioRepository(db)

def get_usuario_service(
    repo: UsuarioRepository = Depends(get_usuario_repository)
) -> UsuarioService:
    return UsuarioService(repo)
```

### 5. DTOs Intermedios (opcional pero recomendado)

**Para casos complejos**:

```python
# app/dtos/usuario_dto.py
from dataclasses import dataclass

@dataclass
class CrearUsuarioDTO:
    """DTO interno para creación de usuario.

    Desacopla schemas de Pydantic de lógica de negocio.
    """
    username: str
    nombre: str
    apellido: str
    password_hash: str
    id_clase: Optional[str] = None
```

## 📊 Comparativa de Impacto

### Testabilidad

**Antes**:
```python
# ❌ Test requiere BD real
def test_crear_usuario():
    db = TestingSessionLocal()  # BD completa
    response = client.post("/usuarios", json={...})
```

**Después**:
```python
# ✅ Test con mock
def test_crear_usuario():
    mock_repo = MagicMock(spec=UsuarioRepository)
    service = UsuarioService(mock_repo)

    usuario = service.crear_usuario(data)
    mock_repo.create.assert_called_once()
```

### Cambiar de PostgreSQL a MongoDB

**Antes**:
- ❌ Cambiar 20+ archivos de routers
- ❌ Reescribir todas las queries

**Después**:
- ✅ Solo cambiar repositorios (5-10 archivos)
- ✅ Servicios y routers sin cambios

## 🚀 Plan de Migración Incremental

### Fase 1: Usuario (Prioridad Alta)
1. ✅ Crear `UsuarioRepository`
2. ✅ Crear `UsuarioService`
3. Refactorizar `usuarios.py` router
4. Tests unitarios de servicio

### Fase 2: Auth (Prioridad Alta)
1. Crear `AuthService`
2. Refactorizar `auth.py`
3. Compartir lógica con usuarios

### Fase 3: Resto de Entidades
1. Profesor, Clase, Partida
2. Actividades, Puntos
3. Estadísticas (ya están bien con servicios)

## 🎓 Patrones Adicionales Recomendados

### 1. Unit of Work (Transacciones)

```python
class UnitOfWork:
    def __init__(self, db: Session):
        self.db = db
        self.usuarios = UsuarioRepository(db)
        self.clases = ClaseRepository(db)

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()
```

### 2. Specification Pattern (Queries Complejas)

```python
class ActiveUsersSpecification:
    def to_sqlalchemy(self):
        return Usuario.activo == True
```

### 3. Domain Events (Desacople entre módulos)

```python
# Cuando se crea un usuario, enviar email sin acoplar
usuario_creado_event = UsuarioCreadoEvent(usuario)
event_bus.publish(usuario_creado_event)
```

## 📈 Métricas de Desacople

### Actual
- **Acoplamiento Router-DB**: ⚠️ Alto (queries directos)
- **Testabilidad**: ⚠️ Media (requiere BD)
- **Reutilización**: ⚠️ Baja (lógica en endpoints)
- **Mantenibilidad**: ✅ Media-Alta (schemas separados)

### Después de Mejoras
- **Acoplamiento Router-DB**: ✅ Bajo (a través de servicios)
- **Testabilidad**: ✅ Alta (mocks fáciles)
- **Reutilización**: ✅ Alta (servicios reutilizables)
- **Mantenibilidad**: ✅ Alta (responsabilidades claras)

## 🔍 Ejemplo Completo: Crear Usuario

### Antes
```python
# router/usuarios.py (50 líneas con lógica)
@router.post("")
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    # Validación
    existe = db.query(Usuario).filter(...).first()
    if existe:
        raise HTTPException(...)

    # Validar clase
    if data.id_clase:
        clase = db.query(Clase).filter(...).first()
        if not clase:
            raise HTTPException(...)

    # Crear
    nuevo = Usuario(
        id=str(uuid.uuid4()),
        password=hash_password(data.password),
        ...
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    # Log
    log_db_operation(...)

    return nuevo
```

### Después
```python
# router/usuarios.py (5 líneas - solo coordina)
@router.post("")
def crear_usuario(
    data: UsuarioCreate,
    service: UsuarioService = Depends(get_usuario_service)
):
    return service.crear_usuario(data)

# service/usuario_service.py (lógica de negocio)
def crear_usuario(self, data: UsuarioCreate) -> Usuario:
    if self.usuario_repo.exists_by_username(data.username):
        raise HTTPException(...)

    if data.id_clase and not self.clase_repo.exists(data.id_clase):
        raise HTTPException(...)

    usuario = Usuario(
        id=str(uuid.uuid4()),
        password=hash_password(data.password),
        **data.dict()
    )

    created = self.usuario_repo.create(usuario)
    log_db_operation(...)
    return created

# repository/usuario_repository.py (acceso a datos)
def exists_by_username(self, username: str) -> bool:
    return self.db.query(Usuario).filter(...).first() is not None

def create(self, usuario: Usuario) -> Usuario:
    self.db.add(usuario)
    self.db.commit()
    self.db.refresh(usuario)
    return usuario
```

## ✅ Resumen de Beneficios

| Aspecto | Antes | Después |
|---------|-------|---------|
| Líneas en router | 50+ | 5 |
| Dependencia de BD | Directa | Indirecta |
| Tests unitarios | Difícil | Fácil |
| Cambiar ORM | Muy difícil | Fácil |
| Reutilizar lógica | No | Sí |
| Complejidad | Media | Baja (por archivo) |

---

**Autor: Gernibide**

**Nota**: Esta es una guía de mejoras progresivas. No es necesario implementar todo de una vez.
Empieza por módulos críticos (Usuario, Auth) y migra gradualmente.
