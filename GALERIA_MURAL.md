# 📸 Galería y Mural de Estudiantes

## 📋 Resumen

Se ha implementado un sistema completo de **Galería de Imágenes** y **Mural de Mensajes** para el dashboard de profesores, permitiendo visualizar las respuestas de los estudiantes organizadas por clase.

## 🎯 Funcionalidades

### Galería de Imágenes
- ✅ Muestra todas las imágenes (URLs de Cloudinary) subidas por estudiantes
- ✅ Grid responsivo con preview de imágenes
- ✅ Modal para ver imágenes en tamaño completo
- ✅ Información de estudiante, clase, actividad y fecha
- ✅ Filtrado por clase

### Mural de Mensajes
- ✅ Muestra todos los mensajes de texto de estudiantes
- ✅ Tarjetas estilizadas con animaciones
- ✅ Información de estudiante, clase, actividad y fecha
- ✅ Filtrado por clase

### Características Comunes
- ✅ Tabs para cambiar entre galería y mural
- ✅ Contador de elementos
- ✅ Estados de carga y vacío
- ✅ Diseño coherente con el resto de la aplicación
- ✅ Totalmente responsivo

## 🏗️ Arquitectura

### Backend (API)

#### Servicio: `teacher_dashboard_service.py`
```python
TeacherDashboardService.get_gallery_images(db, profesor_id, clase_id=None)
# Retorna lista de imágenes con metadata

TeacherDashboardService.get_message_wall(db, profesor_id, clase_id=None)
# Retorna lista de mensajes con metadata
```

#### Endpoints: `teacher_dashboard.py`
```
GET /api/teacher/dashboard/gallery?clase_id={opcional}
GET /api/teacher/dashboard/message-wall?clase_id={opcional}
```

**Autenticación:** JWT Token de profesor (required)

**Respuesta Galería:**
```json
[
  {
    "url": "https://res.cloudinary.com/...",
    "alumno": "Juan Pérez",
    "clase": "5º Primaria A",
    "actividad": "Fotografía del Árbol del Gernika",
    "fecha": "2024-01-20 15:30"
  }
]
```

**Respuesta Mural:**
```json
[
  {
    "mensaje": "Me ha encantado visitar el Árbol...",
    "alumno": "María García",
    "clase": "5º Primaria A",
    "actividad": "Reflexión sobre el Árbol",
    "fecha": "2024-01-20 15:30"
  }
]
```

### Frontend (Web)

#### Archivos Creados:
- `app/web/templates/gallery-wall.html` - Plantilla HTML
- `app/web/static/css/gallery-wall.css` - Estilos
- `app/web/static/js/gallery-wall.js` - JavaScript

#### Ruta Web:
```
GET /gallery
```

## 🎨 Diseño

### Paleta de Colores
Coherente con el diseño "Organic/Natural" del resto de la aplicación:
- Verde oliva: `#6B8E3A`
- Verde oscuro: `#4A5D23`
- Lima: `#A4B84C`
- Beige: `#F5F3E8`

### Componentes UI

#### Galería
- Grid responsivo (3-4 columnas en desktop, 1-2 en móvil)
- Cards con imagen, nombre estudiante y metadata
- Hover effect con elevación
- Click para abrir modal

#### Mural
- Grid de tarjetas (2-3 columnas en desktop, 1 en móvil)
- Borde izquierdo verde oliva
- Animaciones de entrada escalonadas
- Diseño de "nota adhesiva"

#### Modal de Imagen
- Fondo oscuro con blur
- Imagen centrada con tamaño máximo 90vh
- Botón de cierre flotante
- Info debajo de la imagen
- Cierre con Escape o click fuera

## 🔍 Lógica de Filtrado

### Backend
El servicio distingue entre imágenes y mensajes:
- **Imágenes:** `respuesta_contenido` contiene "cloudinary.com" O empieza con "http"
- **Mensajes:** `respuesta_contenido` NO contiene "cloudinary.com" Y NO empieza con "http"

### Filtro por Clase
Ambos endpoints aceptan parámetro opcional `clase_id`:
- Si está presente: filtra por esa clase
- Si está vacío/null: muestra todas las clases del profesor

## 🚀 Cómo Usar

### Para Profesores

1. **Acceder a la página:**
   ```
   http://localhost:8000/gallery
   ```

2. **Iniciar sesión** como profesor (si no está autenticado)

3. **Filtrar por clase** (opcional):
   - Usar el dropdown superior
   - Seleccionar "Todas las clases" para ver todo

4. **Ver galería:**
   - Click en tab "Galería de Imágenes"
   - Click en cualquier imagen para ampliar
   - Ver información del estudiante y contexto

5. **Ver mural:**
   - Click en tab "Mural de Mensajes"
   - Scroll para ver todos los mensajes
   - Cada tarjeta muestra el mensaje completo

### Añadir al Menú de Navegación

Actualizar el navbar en otros templates HTML para incluir:
```html
<li class="navbar-menu-item navbar-admin-only">
    <a href="/gallery" class="navbar-menu-link">Galería y Mural</a>
</li>
```

## 📊 Estructura de Datos

### Tabla Origen: `actividad_progreso`

| Campo | Tipo | Uso |
|-------|------|-----|
| `id_juego` | UUID | Join con `partida` → `id_usuario` |
| `id_actividad` | UUID | Join con `actividad` (nombre) |
| `respuesta_contenido` | TEXT | Contiene URL o mensaje |
| `fecha_fin` | DATETIME | Fecha de completado |
| `estado` | VARCHAR | Filtro: "completado" |

### Joins Necesarios
```
actividad_progreso
  → partida (id_juego)
    → usuario (id_usuario)
      → clase (id_clase)
        → profesor (id_profesor)
  → actividad (id_actividad)
```

## ✅ Testing

### Verificar Backend

1. **Login como profesor:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login-web \
     -H "Content-Type: application/json" \
     -d '{"username": "profesor", "password": "password"}'
   ```

2. **Obtener galería:**
   ```bash
   curl http://localhost:8000/api/teacher/dashboard/gallery \
     -H "Authorization: Bearer {token}"
   ```

3. **Obtener mural:**
   ```bash
   curl http://localhost:8000/api/teacher/dashboard/message-wall \
     -H "Authorization: Bearer {token}"
   ```

### Verificar Frontend

1. Abrir: `http://localhost:8000/gallery`
2. Login como profesor
3. Verificar que carga clases en el filtro
4. Verificar que carga galería
5. Verificar que carga mural
6. Probar filtro por clase
7. Probar modal de imagen
8. Verificar responsive (móvil/tablet)

## 🐛 Troubleshooting

### No aparecen imágenes/mensajes

**Causa:** No hay datos en `actividad_progreso.respuesta_contenido`

**Solución:** Verificar que las actividades estén guardando respuestas:
```sql
SELECT respuesta_contenido, estado
FROM actividad_progreso
WHERE respuesta_contenido IS NOT NULL
  AND respuesta_contenido != '';
```

### Error 403 Forbidden

**Causa:** Token expirado o inválido

**Solución:** Cerrar sesión y volver a iniciar sesión

### Imágenes no cargan en modal

**Causa:** URL de Cloudinary no válida o CORS

**Solución:**
- Verificar URLs en la base de datos
- Configurar CORS en Cloudinary si es necesario

### Filtro de clase no funciona

**Causa:** `id_clase` en usuarios es NULL

**Solución:** Asignar clases a los usuarios en la base de datos

## 🔄 Próximas Mejoras

### Funcionalidades Sugeridas
- [ ] Paginación para muchas imágenes/mensajes
- [ ] Ordenamiento (fecha, estudiante, clase)
- [ ] Búsqueda por texto
- [ ] Descarga de imágenes
- [ ] Exportar mensajes a PDF
- [ ] Comentarios del profesor en cada elemento
- [ ] Sistema de "me gusta" o favoritos
- [ ] Filtro por actividad específica
- [ ] Filtro por rango de fechas
- [ ] Vista de carrusel para galería

### Optimizaciones
- [ ] Lazy loading de imágenes
- [ ] Caché en frontend
- [ ] Thumbnails para preview (Cloudinary transformations)
- [ ] Infinite scroll
- [ ] WebSocket para actualizaciones en tiempo real

## 📝 Notas Técnicas

### Performance
- Las consultas filtran solo actividades completadas
- Se usa JOIN eficiente con índices existentes
- Las imágenes se cargan con `loading="lazy"`

### Seguridad
- Todos los endpoints requieren autenticación JWT
- Se valida que el profesor solo vea sus propias clases
- Se escapa HTML en JavaScript para prevenir XSS
- URLs de Cloudinary son seguras (HTTPS)

### Responsive
- Mobile-first design
- Breakpoint principal: 768px
- Grid adaptativo según tamaño de pantalla
- Touch-friendly (botones grandes, spacing)

## 📄 Licencia

MIT License - Gernibide Project

---

## 📞 Soporte

Para dudas o problemas, revisar:
1. Logs del servidor FastAPI
2. Console del navegador (F12)
3. Network tab para ver requests fallidos
4. Database para verificar datos
