# APK Downloads Directory

Este directorio contiene los archivos APK de la aplicación Gernibide para descarga directa.

## Cómo habilitar la descarga del APK

1. **Coloca el APK aquí**: 
   - Añade el archivo `gernibide.apk` en este directorio

2. **Habilita el link en home.html**:
   - Abre `app/web/templates/home.html`
   - Busca el comentario `<!-- Android APK Badge -->`
   - Cambia:
     ```html
     <a href="#" class="badge-item badge-disabled" ...>
     ```
   - Por:
     ```html
     <a href="/static/downloads/gernibide.apk" class="badge-item" ...>
     ```

3. **Listo**: Los usuarios podrán descargar el APK directamente

## Nota

- El badge de iOS (App Store) permanecerá deshabilitado hasta que la app esté en la tienda
- Puedes añadir múltiples versiones del APK con nombres diferentes (ej: `gernibide-v1.0.0.apk`)
