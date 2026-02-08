"""Sistema de internacionalización (i18n) para Gernibide.

Este módulo proporciona funcionalidades de traducción multi-idioma
para la aplicación web, soportando español y euskera.

Autor: Gernibide
"""

from app.i18n.helpers import get_language_from_request, get_translator
from app.i18n.loader import load_translations

__all__ = ["get_translator", "get_language_from_request", "load_translations"]
