# Sistema de Audit Logs - Demostración de Herencia y Polimorfismo

## 📚 Conceptos Implementados

Este módulo demuestra los conceptos de **Herencia** y **Polimorfismo** en programación orientada a objetos usando SQLAlchemy y FastAPI.

## 🏗️ Arquitectura de Herencia

### Diagrama de Clases

```
                    ┌─────────────┐
                    │  AuditLog   │ (Clase Base)
                    │  (Base)     │
                    ├─────────────┤
                    │ + id        │
                    │ + timestamp │
                    │ + accion    │
                    │ + tipo      │ ← Discriminador
                    │ + detalles  │
                    ├─────────────┤
                    │ get_description() │ ← Método polimórfico
                    └──────┬──────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
    ┌──────▼──────┐               ┌───────▼──────┐
    │ AuditLogWeb │               │ AuditLogApp  │
    │  (Hereda)   │               │  (Hereda)    │
    ├─────────────┤               ├──────────────┤
    │ + ip_address│               │ + device_type│
    │ + user_agent│               │ + app_version│
    │ + browser   │               │ + device_id  │
    ├─────────────┤               ├──────────────┤
    │ get_description() │         │ get_description() │
    │ (Override)  │               │ (Override)   │
    └─────────────┘               └──────────────┘
```

## 1️⃣ Herencia (Inheritance)

### Definición
La **herencia** permite que una clase (hija) derive de otra clase (padre), heredando sus atributos y métodos.

### Implementación

```python
# Clase BASE - Padre
class AuditLog(Base):
    """Clase padre que define la estructura común"""
    __tablename__ = "audit_log"

    # Atributos comunes a todos los logs
    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    accion = Column(String(100), nullable=False)
    tipo = Column(String(20))  # Discriminador polimórfico

    def get_description(self):
        """Método base que puede ser sobrescrito"""
        return f"{self.accion} - {self.timestamp}"

# Clase HIJA 1 - Hereda de AuditLog
class AuditLogWeb(AuditLog):
    """Especialización para logs de la aplicación web"""

    # Atributos específicos de logs web
    ip_address = Column(String(45))
    browser = Column(String(100))

    # Sobrescribe el método del padre (Override)
    def get_description(self):
        return f"🌐 {self.accion} desde {self.browser}"

# Clase HIJA 2 - Hereda de AuditLog
class AuditLogApp(AuditLog):
    """Especialización para logs de la app móvil"""

    # Atributos específicos de logs app
    device_type = Column(String(50))
    app_version = Column(String(20))

    # Sobrescribe el método del padre (Override)
    def get_description(self):
        return f"📱 {self.accion} desde {self.device_type}"
```

### Ventajas de la Herencia

✅ **Reutilización de código**: Los campos comunes (id, timestamp, accion) se definen una sola vez
✅ **Mantenibilidad**: Cambios en la clase base afectan a todas las hijas
✅ **Organización**: Jerarquía clara de tipos relacionados
✅ **DRY Principle**: No repetimos código común

## 2️⃣ Polimorfismo (Polymorphism)

### Definición
El **polimorfismo** permite que un método se comporte de manera diferente según el tipo del objeto que lo invoca.

### Implementación

```python
# POLIMORFISMO EN ACCIÓN

# Crear un log web
log_web = AuditLogWeb(
    accion="login",
    browser="Chrome"
)

# Crear un log app
log_app = AuditLogApp(
    accion="login",
    device_type="iOS"
)

# EL MISMO MÉTODO, DIFERENTES RESULTADOS ← Esto es polimorfismo
print(log_web.get_description())  # 🌐 login desde Chrome
print(log_app.get_description())  # 📱 login desde iOS
```

### Polimorfismo en Consultas

```python
# Query polimórfica - SQLAlchemy automáticamente retorna el tipo correcto
logs = db.query(AuditLog).all()

for log in logs:
    # SQLAlchemy retorna AuditLogWeb o AuditLogApp según el discriminador
    # get_description() se comporta diferente para cada tipo
    print(log.get_description())

# Output:
# 🌐 login desde Chrome      ← AuditLogWeb
# 📱 login desde iOS          ← AuditLogApp
# 🌐 crear_clase desde Firefox ← AuditLogWeb
# 📱 completar_evento desde Android ← AuditLogApp
```

## 🎯 Uso Práctico - Endpoints

### Crear Log desde Web

```bash
POST /api/v1/audit-logs/web
Content-Type: application/json
X-API-Key: tu-api-key

{
  "usuario_id": "uuid-del-usuario",
  "accion": "login",
  "detalles": "Inicio de sesión exitoso",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "browser": "Chrome"
}
```

**Internamente**: Se crea una instancia de `AuditLogWeb` (clase hija)

### Crear Log desde App

```bash
POST /api/v1/audit-logs/app
Content-Type: application/json
X-API-Key: tu-api-key

{
  "usuario_id": "uuid-del-usuario",
  "accion": "login",
  "detalles": "Inicio de sesión exitoso",
  "device_type": "iOS",
  "app_version": "1.2.0",
  "device_id": "ABC123"
}
```

**Internamente**: Se crea una instancia de `AuditLogApp` (clase hija)

### Listar Todos los Logs (Polimorfismo)

```bash
GET /api/v1/audit-logs
Authorization: Bearer token-jwt
```

**Respuesta**:
```json
[
  {
    "id": "uuid-1",
    "tipo": "web",
    "accion": "login",
    "browser": "Chrome",
    "ip_address": "192.168.1.100",
    "device_type": null,
    "app_version": null
  },
  {
    "id": "uuid-2",
    "tipo": "app",
    "accion": "completar_evento",
    "device_type": "Android",
    "app_version": "1.2.0",
    "browser": null,
    "ip_address": null
  }
]
```

## 🔍 Single Table Inheritance

Este proyecto usa **Single Table Inheritance** de SQLAlchemy:

- ✅ Todas las clases se almacenan en UNA tabla (`audit_log`)
- ✅ El campo `tipo` actúa como **discriminador** ('web' o 'app')
- ✅ Los campos específicos de cada tipo son `nullable`
- ✅ SQLAlchemy automáticamente retorna la clase correcta en queries

### Estructura de la Tabla

```sql
CREATE TABLE audit_log (
    id VARCHAR(36) PRIMARY KEY,
    timestamp DATETIME,
    accion VARCHAR(100),
    tipo VARCHAR(20),          -- Discriminador: 'web' o 'app'

    -- Campos Web (null si tipo='app')
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    browser VARCHAR(100),

    -- Campos App (null si tipo='web')
    device_type VARCHAR(50),
    app_version VARCHAR(20),
    device_id VARCHAR(100)
);
```

## 📊 Ventajas del Sistema

| Característica | Beneficio |
|---------------|-----------|
| **Herencia** | Código reutilizable y organizado |
| **Polimorfismo** | Mismo método, diferentes comportamientos |
| **Single Table** | Queries simples, una sola tabla |
| **Discriminador** | SQLAlchemy maneja automáticamente los tipos |
| **Trazabilidad** | Registro completo de acciones por plataforma |
| **Escalable** | Fácil añadir nuevos tipos (AuditLogAPI, etc.) |

## 🚀 Casos de Uso

1. **Debugging**: Identificar problemas específicos de plataforma
2. **Analytics**: Ver qué plataforma usan más los usuarios
3. **Seguridad**: Detectar actividad sospechosa por IP o dispositivo
4. **Compliance**: Registro de auditoría para regulaciones
5. **UX Research**: Entender comportamiento por plataforma

## 💡 Extensibilidad

Para añadir un nuevo tipo (ej: logs de API interna):

```python
class AuditLogAPI(AuditLog):
    """Logs de llamadas internas entre servicios"""

    service_name = Column(String(100))
    endpoint = Column(String(500))

    __mapper_args__ = {
        'polymorphic_identity': 'api'
    }

    def get_description(self):
        return f"🔧 {self.accion} - {self.service_name} → {self.endpoint}"
```

## 📝 Conclusión

Este sistema demuestra los principios fundamentales de POO:

- ✅ **Encapsulación**: Cada clase encapsula su lógica específica
- ✅ **Herencia**: Reutilización de código mediante jerarquía de clases
- ✅ **Polimorfismo**: Comportamiento dinámico según el tipo
- ✅ **Abstracción**: Interfaz común (`get_description()`) con implementaciones específicas

Es un ejemplo práctico y funcional de cómo aplicar estos conceptos en un sistema real de producción.
