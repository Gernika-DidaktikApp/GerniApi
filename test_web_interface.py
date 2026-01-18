"""
Script de prueba para visualizar la interfaz web sin necesidad de la API completa
Ejecutar con: python test_web_interface.py
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import uvicorn

# Crear aplicación FastAPI simple
app = FastAPI(title="Gernibide Web Interface - Test")

# Configurar directorios
BASE_DIR = Path(__file__).parent / "app" / "web"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Configurar templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Página de inicio pública"""
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Página de dashboard (placeholder)"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


if __name__ == "__main__":
    print("=" * 60)
    print("🌳 Gernibide Web Interface - Servidor de Prueba")
    print("=" * 60)
    print("\n📍 Páginas disponibles:")
    print("   - Inicio: http://localhost:8000/")
    print("   - Login: http://localhost:8000/login")
    print("   - Dashboard Admin: http://localhost:8000/dashboard")
    print("\n✨ Características:")
    print("   - Página de inicio con estadísticas animadas")
    print("   - Puntos de interés destacados")
    print("   - Banner de descarga de app")
    print("   - Página de login completamente funcional")
    print("   - Dashboard de administrador con placeholders para Plotly")
    print("   - Diseño responsive y accesible")
    print("\n⚠️  Nota: Esta es una vista previa. La autenticación real")
    print("   requiere la API completa en ejecución.")
    print("\n🛑 Presiona Ctrl+C para detener el servidor\n")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
