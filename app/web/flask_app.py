"""Flask application para la interfaz web.

Esta aplicación Flask se integra con FastAPI para servir la interfaz web
de Gernibide. Usa los mismos templates Jinja2 y proporciona las mismas
rutas que la versión FastAPI.

Integración académica: Este módulo demuestra el uso de Flask junto con FastAPI
en el mismo proyecto, permitiendo aprovechar las fortalezas de ambos frameworks.

Autor: Gernibide
"""

from pathlib import Path

from flask import Flask, render_template, request

# Crear app Flask
flask_app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)


def get_translator_flask():
    """Obtener traductor para Flask basado en cookies/headers.

    Returns:
        tuple: (función de traducción, código de idioma)
    """
    # Obtener idioma de cookies (con try/except por si no hay contexto de request)
    try:
        lang = request.cookies.get("language", "es")
    except RuntimeError:
        # No hay contexto de request, usar español por defecto
        lang = "es"

    if lang not in ["es", "eu"]:
        lang = "es"

    # Cargar traducciones
    import json

    i18n_path = Path(__file__).parent.parent / "i18n" / f"{lang}.json"
    with open(i18n_path, encoding="utf-8") as f:
        translations = json.load(f)

    def translate(key: str, **kwargs) -> str:
        """Traducir una clave usando dot notation."""
        keys = key.split(".")
        value = translations
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, key)
            else:
                return key
        return str(value).format(**kwargs) if kwargs else str(value)

    return translate, lang


@flask_app.route("/")
def home_page():
    """Página de inicio."""
    translate, lang = get_translator_flask()
    return render_template("home.html", _=translate, current_lang=lang)


@flask_app.route("/login")
def login_page():
    """Página de login."""
    translate, lang = get_translator_flask()
    return render_template("login.html", _=translate, current_lang=lang)


@flask_app.route("/dashboard")
def dashboard_page():
    """Página del dashboard."""
    translate, lang = get_translator_flask()
    return render_template("dashboard.html", _=translate, current_lang=lang)


@flask_app.route("/dashboard/teacher")
def dashboard_teacher_page():
    """Página del dashboard de profesor."""
    translate, lang = get_translator_flask()
    return render_template("dashboard-teacher.html", _=translate, current_lang=lang)


@flask_app.route("/statistics")
def statistics_page():
    """Página de estadísticas."""
    translate, lang = get_translator_flask()
    return render_template("statistics.html", _=translate, current_lang=lang)


@flask_app.route("/statistics/gameplay")
def statistics_gameplay_page():
    """Página de estadísticas de gameplay."""
    translate, lang = get_translator_flask()
    return render_template("statistics-gameplay.html", _=translate, current_lang=lang)


@flask_app.route("/statistics/learning")
def statistics_learning_page():
    """Página de estadísticas de aprendizaje."""
    translate, lang = get_translator_flask()
    return render_template("statistics-learning.html", _=translate, current_lang=lang)


@flask_app.route("/gallery")
def gallery_wall_page():
    """Página de galería y muro de mensajes."""
    translate, lang = get_translator_flask()
    return render_template("gallery-wall.html", _=translate, current_lang=lang)


# Health check para Flask
@flask_app.route("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "framework": "Flask"}
