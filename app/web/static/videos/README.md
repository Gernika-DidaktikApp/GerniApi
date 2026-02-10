# 🎥 Videos Tutoriales

Esta carpeta contiene los videos tutoriales en formato MP4.

## Archivos necesarios:

### Videos principales:
- `tutorial-web.mp4` - Tutorial del panel web (formato horizontal 16:9)
- `tutorial-app.mp4` - Tutorial de la aplicación móvil (formato vertical 9:16)

### Miniaturas (thumbnails) opcionales:
- `thumbnail-web.jpg` - Miniatura para el tutorial web (1280x720px recomendado)
- `thumbnail-app.jpg` - Miniatura para el tutorial de la app (720x1280px recomendado)

## Instrucciones:

1. **Coloca tus archivos de video aquí** con los nombres exactos indicados arriba
2. Los videos se reproducirán directamente en la página `/manuals`
3. Si los videos son muy pesados (>50MB), considera estas alternativas:
   - Comprimir los videos usando herramientas como HandBrake
   - Subirlos a YouTube/Vimeo y cambiar los enlaces en el HTML
   - Usar un servicio de CDN para videos

## Recomendaciones de formato:

### Video Vertical:
- **Resolución**: 720x1280px o 1080x1920px
- **Aspecto**: 9:16
- **Formato**: MP4 (H.264)
- **Duración**: 2-5 minutos recomendado
- **Tamaño**: <30MB

### Video Horizontal:
- **Resolución**: 1280x720px (HD) o 1920x1080px (Full HD)
- **Aspecto**: 16:9
- **Formato**: MP4 (H.264)
- **Duración**: 5-10 minutos recomendado
- **Tamaño**: <50MB

## Estructura de carpeta:
```
videos/
├── README.md (este archivo)
├── tutorial-web.mp4
├── tutorial-app.mp4
├── thumbnail-web.jpg (opcional)
└── thumbnail-app.jpg (opcional)
```

## Alternativa: Usar YouTube

Si prefieres usar YouTube, edita el archivo `manuals.html` y reemplaza las etiquetas `<video>` por iframes de YouTube:

```html
<iframe
    width="100%"
    height="100%"
    src="https://www.youtube.com/embed/TU_ID_VIDEO"
    frameborder="0"
    allowfullscreen>
</iframe>
```
