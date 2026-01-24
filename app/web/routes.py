"""
Flask-style web routes for serving HTML templates
Integrates with FastAPI to provide web interface
"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Get the templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Create router for web pages
router = APIRouter(tags=["🌐 Web Interface"], include_in_schema=True)


@router.get("/login", response_class=HTMLResponse, name="login_page")
async def login_page(request: Request):
    """
    Render the login page

    Returns the HTML login interface for Gernibide
    """
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse, name="dashboard_page")
async def dashboard_page(request: Request):
    """
    Render the dashboard page

    Returns the main dashboard interface (requires authentication)
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/", response_class=HTMLResponse, name="home_page")
async def home_page(request: Request):
    """
    Render the home page

    Public landing page with app description, stats, and download section
    """
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/statistics", response_class=HTMLResponse, name="statistics_page")
async def statistics_page(request: Request):
    """
    Render the statistics page

    Public page with user activity metrics and charts
    """
    return templates.TemplateResponse("statistics.html", {"request": request})


@router.get("/statistics/gameplay", response_class=HTMLResponse, name="statistics_gameplay_page")
async def statistics_gameplay_page(request: Request):
    """
    Render the gameplay statistics page

    Public page with game usage metrics and charts (partidas, eventos, completion rates)
    """
    return templates.TemplateResponse("statistics-gameplay.html", {"request": request})


@router.get("/statistics/learning", response_class=HTMLResponse, name="statistics_learning_page")
async def statistics_learning_page(request: Request):
    """
    Render the learning statistics page

    Public page with learning and performance metrics (puntuaciones, distribución, tiempos)
    """
    return templates.TemplateResponse("statistics-learning.html", {"request": request})


@router.get("/dashboard/teacher", response_class=HTMLResponse, name="dashboard_teacher_page")
async def dashboard_teacher_page(request: Request):
    """
    Render the teacher dashboard page

    Private page for teachers with class-level statistics (requires authentication)
    Shows progress by student, time spent, activities completed, and class evolution
    """
    return templates.TemplateResponse("dashboard-teacher.html", {"request": request})
