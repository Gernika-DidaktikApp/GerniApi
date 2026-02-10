# Interfaz Web de Gernibide

Esta carpeta contiene la interfaz web HTML para la aplicación Gernibide.

## 📁 Estructura

```
web/
├── static/              # Archivos estáticos
│   ├── css/            # Hojas de estilo
│   │   └── login.css   # Estilos de la página de login
│   ├── js/             # Scripts JavaScript
│   │   └── login.js    # Lógica de la página de login
│   └── icons/          # Iconos e imágenes
│       └── tree-logo.svg  # Logo del árbol de Gernibide
├── templates/          # Plantillas HTML
│   ├── login.html      # Página de login
│   ├── dashboard.html  # Dashboard principal (pendiente)
│   └── base.html       # Plantilla base (pendiente)
└── routes.py          # Rutas de FastAPI para servir las páginas
```

## 🎨 Paleta de Colores

La interfaz utiliza la siguiente paleta de colores natural y educativa:

- **Negro**: `#000000` - Texto principal
- **Marrón Oscuro**: `#3D2817` - Acentos oscuros
- **Marrón**: `#8B6F47` - Elementos secundarios
- **Verde Salvia**: `#6B8E6F` - Color primario (botones, enlaces)
- **Verde Lima**: `#B8C74A` - Acentos vibrantes
- **Menta Claro**: `#D9E8D8` - Fondos suaves
- **Blanco**: `#FFFFFF` - Fondos principales
- **Fondo**: `#E8F1F5` - Fondo de página

## 🚀 Características Implementadas

### Página de Login (`login.html`)

- ✅ Diseño limpio y moderno con gradientes suaves
- ✅ Validación de formularios en tiempo real
- ✅ Toggle de visibilidad de contraseña
- ✅ Animaciones y micro-interacciones
- ✅ Responsive design
- ✅ Accesibilidad (ARIA labels, navegación por teclado)
- ✅ Carga asíncrona de recursos
- ✅ Separación completa de HTML, CSS y JS

### Características Técnicas

- **Sin estilos en línea**: Todo el CSS está en archivos externos
- **Sin scripts en línea**: Todo el JavaScript está en archivos externos
- **Carga asíncrona**: Los recursos se cargan de forma optimizada
- **SEO optimizado**: Meta tags y estructura semántica
- **Accesibilidad**: WCAG 2.1 compatible

## 🔧 Configuración

### Requisitos

Asegúrate de tener instalado `jinja2`:

```bash
pip install jinja2>=3.1.0
```

### Rutas Disponibles

- `/` - Página principal (redirige a login)
- `/login` - Página de login
- `/dashboard` - Dashboard (requiere autenticación)

### Archivos Estáticos

Los archivos estáticos se sirven desde `/static/`:

- CSS: `/static/css/login.css`
- JS: `/static/js/login.js`
- Iconos: `/static/icons/tree-logo.svg`

## 📝 Próximos Pasos

### Páginas Pendientes

1. **Dashboard** (`dashboard.html`)
   - Panel principal del profesor
   - Visualización de clases y actividades
   - Estadísticas y gráficos

2. **Gestión de Clases** 
   - Crear/editar clases
   - Asignar estudiantes
   - Ver progreso

3. **Gestión de Actividades**
   - Crear actividades educativas
   - Configurar eventos
   - Seguimiento de progreso

4. **Gestión de Partidas**
   - Iniciar partidas
   - Monitorear progreso en tiempo real
   - Resultados y estadísticas

### Mejoras Técnicas

- [ ] Implementar sistema de autenticación JWT en el frontend
- [ ] Añadir manejo de sesiones
- [ ] Implementar refresh de tokens
- [ ] Añadir notificaciones toast
- [ ] Implementar modo oscuro
- [ ] Añadir internacionalización (i18n)

## 🎯 Integración con la API

El JavaScript está preparado para integrarse con la API REST:

```javascript
// Endpoint de login (configurar en login.js)
POST /api/v1/auth/login

// Headers requeridos
{
  "Content-Type": "application/json"
}

// Body
{
  "email": "usuario@example.com",
  "password": "contraseña"
}

// Respuesta esperada
{
  "token": "jwt_token_aqui",
  "user": { ... }
}
```

## 🎨 Guía de Estilo

### Tipografía

- **Fuente principal**: Inter (Google Fonts)
- **Tamaños**: Sistema de escala modular
- **Pesos**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### Espaciado

Sistema de espaciado consistente basado en múltiplos de 0.5rem:

- `xs`: 0.5rem
- `sm`: 0.75rem
- `md`: 1rem
- `lg`: 1.5rem
- `xl`: 2rem
- `2xl`: 3rem

### Bordes

- `sm`: 0.5rem
- `md`: 0.75rem
- `lg`: 1rem
- `xl`: 1.5rem
- `full`: 9999px (círculos)

## 📱 Responsive Design

La interfaz está optimizada para:

- 📱 Móviles: < 480px
- 📱 Tablets: 481px - 768px
- 💻 Desktop: > 768px

## ♿ Accesibilidad

- Navegación completa por teclado
- ARIA labels en todos los elementos interactivos
- Contraste de colores WCAG AA
- Soporte para `prefers-reduced-motion`
- Focus visible para navegación por teclado

## 🔒 Seguridad

- Validación de formularios en cliente y servidor
- Protección contra XSS
- Headers de seguridad configurados
- Tokens JWT para autenticación
- HTTPS recomendado en producción
