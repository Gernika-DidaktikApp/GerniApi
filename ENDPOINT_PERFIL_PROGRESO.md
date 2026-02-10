# Endpoint: Perfil y Progreso del Usuario

## 📋 Resumen de la Implementación

Este documento describe el nuevo endpoint `/usuarios/{usuario_id}/perfil-progreso` que proporciona información detallada del perfil y progreso del usuario para la app móvil.

## 🏗️ Arquitectura

### Archivos Modificados/Creados

1. **`app/schemas/usuario.py`** ✅
   - Añadidos 4 nuevos schemas al final del archivo:
     - `ActividadDetalle` - Detalle de una actividad con su estado
     - `PuntoProgreso` - Progreso de un punto/módulo
     - `EstadisticasGenerales` - Estadísticas generales del usuario
     - `PerfilProgreso` - Schema principal de respuesta

2. **`app/services/usuario_perfil_service.py`** ✅ NUEVO
   - Servicio nuevo coherente con la arquitectura existente
   - `UsuarioPerfilService` - Calcula el progreso completo
   - Métodos privados para cálculos específicos

3. **`app/utils/dependencies.py`** ✅
   - Añadida función `get_usuario_perfil_service()`
   - Inyección de dependencias siguiendo el patrón existente

4. **`app/routers/usuarios.py`** ✅
   - Añadido endpoint `GET /usuarios/{usuario_id}/perfil-progreso`
   - Imports actualizados
   - Documentación completa del endpoint

## 🎯 Endpoint

### URL
```
GET /api/v1/usuarios/{usuario_id}/perfil-progreso
```

### Autenticación
- **API Key**: Puede acceder a cualquier usuario
- **Token JWT**: Solo puede acceder a su propio perfil

### Respuesta

```json
{
  "usuario": {
    "id": "uuid",
    "username": "string",
    "nombre": "string",
    "apellido": "string",
    "id_clase": "uuid | null",
    "creation": "datetime",
    "top_score": "int"
  },
  "estadisticas": {
    "total_actividades_disponibles": "int",
    "actividades_completadas": "int",
    "porcentaje_progreso_global": "float (0-100)",
    "total_puntos_acumulados": "float",
    "racha_dias": "int",
    "ultima_partida": "datetime | null",
    "puntos_completados": "int",
    "total_puntos_disponibles": "int"
  },
  "puntos": [
    {
      "id_punto": "uuid",
      "nombre_punto": "string",
      "total_actividades": "int",
      "actividades_completadas": "int",
      "porcentaje_completado": "float (0-100)",
      "puntos_obtenidos": "float",
      "estado": "no_iniciado | en_progreso | completado",
      "actividades": [
        {
          "id_actividad": "uuid",
          "nombre_actividad": "string",
          "estado": "no_iniciada | en_progreso | completada",
          "puntuacion": "float | null",
          "fecha_completado": "datetime | null",
          "duracion_segundos": "int | null"
        }
      ]
    }
  ]
}
```

## 🔍 Lógica del Servicio

### Flujo Principal (`obtener_perfil_progreso`)

1. **Validar usuario**: Verifica que el usuario existe
2. **Obtener progreso por punto**: Calcula el progreso de cada punto/módulo
3. **Calcular estadísticas generales**: Agrega datos de todos los puntos
4. **Retornar respuesta completa**

### Método `_obtener_progreso_por_punto`

Para cada punto en el sistema:
1. Obtiene todas las actividades del punto
2. Busca las partidas del usuario
3. Para cada actividad, busca si el usuario tiene progreso
4. Si hay progreso:
   - Toma el más reciente si hay múltiples
   - Extrae: estado, puntuación, fecha, duración
5. Si no hay progreso:
   - Marca como "no_iniciada"
6. Calcula:
   - Actividades completadas
   - Puntos obtenidos
   - Porcentaje de completado
   - Estado del punto (no_iniciado/en_progreso/completado)

### Método `_calcular_estadisticas_generales`

Agrega información de todos los puntos:
- Suma total de actividades y completadas
- Calcula porcentaje global
- Suma puntos totales
- Cuenta puntos completados al 100%
- Obtiene última partida (del repositorio)
- Calcula racha de días

### Método `_calcular_racha_dias`

Calcula días consecutivos de juego:
1. Obtiene fechas únicas de partidas del usuario
2. Desde hoy hacia atrás, cuenta días consecutivos
3. Se rompe al encontrar un día sin partidas

## 📊 Diferencias con `/estadisticas` existente

| Característica | `/estadisticas` | `/perfil-progreso` |
|----------------|-----------------|-------------------|
| Información usuario | ❌ | ✅ Completa |
| Actividades completadas | ✅ Total | ✅ Por punto + detalle |
| Actividades NO completadas | ❌ | ✅ Listadas |
| Progreso por punto | ❌ | ✅ Detallado |
| Puntuaciones | ✅ Total | ✅ Por actividad |
| Fechas de completado | ❌ | ✅ Por actividad |
| Duración actividades | ❌ | ✅ Por actividad |
| Estados | ❌ | ✅ Por punto y actividad |

## 🧪 Cómo Probar

### 1. Con Token JWT (Usuario)

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login-app \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario123", "password": "password"}'

# Usar el token en perfil-progreso
curl -X GET http://localhost:8000/api/v1/usuarios/{usuario_id}/perfil-progreso \
  -H "Authorization: Bearer {token}"
```

### 2. Con API Key

```bash
curl -X GET http://localhost:8000/api/v1/usuarios/{usuario_id}/perfil-progreso \
  -H "X-API-Key: {your_api_key}"
```

## ✅ Checklist de Verificación

- [x] Schemas añadidos a `usuario.py`
- [x] Servicio creado con patrón coherente
- [x] Dependency injection configurada
- [x] Endpoint añadido al router
- [x] Imports actualizados correctamente
- [x] Sintaxis verificada (py_compile)
- [x] Autenticación y autorización implementadas
- [x] Documentación del endpoint completa
- [x] Manejo de errores (404 si usuario no existe)
- [x] Respeta ownership (usuario solo ve su perfil con token)

## 🚀 Próximos Pasos

1. **Probar el endpoint** con datos reales
2. **Verificar performance** con muchas actividades
3. **Considerar caché** si es necesario para optimización
4. **Documentar en Swagger/OpenAPI** (ya incluido automáticamente)

## 📝 Notas Técnicas

### Coherencia con Arquitectura Existente

- ✅ Usa repositorios existentes (`UsuarioRepository`, `PartidaRepository`)
- ✅ Sigue patrón de servicios (`UsuarioService`, `UsuarioStatsService`)
- ✅ Dependency injection igual que otros servicios
- ✅ Documentación estilo docstring consistente
- ✅ Manejo de errores con HTTPException
- ✅ Validación de ownership coherente
- ✅ Logging pendiente (opcional, añadir si necesario)

### Modelos Usados

- `Usuario` - Usuario del sistema
- `Partida` (tabla: `juego`) - Sesiones de juego
- `Punto` - Módulos/temas educativos
- `Actividad` - Actividades dentro de puntos
- `ActividadProgreso` - Progreso del usuario en actividades

### Consideraciones de Performance

- El endpoint hace múltiples queries a la BD
- Con pocos puntos/actividades (<100) el performance es bueno
- Para optimizar con muchas actividades:
  - Considerar añadir índices en BD
  - Implementar caché (Redis)
  - Paginar los puntos si es necesario

## 🐛 Troubleshooting

### Error: "Usuario no encontrado"
- Verificar que el `usuario_id` existe en la BD
- Verificar que el UUID tenga el formato correcto

### Error: "No tienes permiso para acceder a este recurso"
- Esto ocurre cuando usas Token JWT e intentas acceder al perfil de otro usuario
- Usar API Key para acceso administrativo

### Error: Imports no funcionan
- Verificar que todas las dependencias estén instaladas
- Verificar que el archivo `.env` esté configurado correctamente

## 📄 Licencia

MIT License - Gernibide Project
