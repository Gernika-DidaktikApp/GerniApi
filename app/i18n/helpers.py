"""Helpers para traducción en templates y rutas.

Este módulo proporciona funciones de ayuda para detectar el idioma
preferido del usuario y generar funciones de traducción.

Autor: Gernibide
"""

import contextlib
from collections.abc import Callable

from fastapi import Request

from app.i18n.loader import get_nested_value, load_translations

SUPPORTED_LANGUAGES = ["es", "eu"]
DEFAULT_LANGUAGE = "es"


def get_language_from_request(request: Request) -> str:
    """Detect language from cookie, query param, or header.

    Priority order:
    1. Cookie 'language'
    2. Query parameter 'lang'
    3. Accept-Language header
    4. Default (Spanish)

    Args:
        request: FastAPI Request object.

    Returns:
        Language code ('es' or 'eu').
    """
    # Priority 1: Cookie
    lang = request.cookies.get("language")
    if lang and lang in SUPPORTED_LANGUAGES:
        return lang

    # Priority 2: Query param
    lang = request.query_params.get("lang")
    if lang and lang in SUPPORTED_LANGUAGES:
        return lang

    # Priority 3: Accept-Language header
    accept_lang = request.headers.get("Accept-Language", "")
    for supported in SUPPORTED_LANGUAGES:
        if supported in accept_lang:
            return supported

    # Priority 4: Default
    return DEFAULT_LANGUAGE


def get_translator(request: Request) -> tuple[Callable[[str], str], str]:
    """Return translator function for templates.

    Args:
        request: FastAPI Request object.

    Returns:
        Tuple of (translator function, current language code).
        The translator function takes a key and returns the translated string.

    Example:
        >>> _, lang = get_translator(request)
        >>> translate, lang = get_translator(request)
        >>> translate('common.nav.home')
        'Inicio'  # or 'Hasiera' if language is 'eu'
    """
    lang = get_language_from_request(request)
    translations = load_translations(lang)

    def translate(key: str, **kwargs) -> str:
        """Translate key with optional format arguments.

        Args:
            key: Dot-separated translation key.
            **kwargs: Optional format arguments for string interpolation.

        Returns:
            Translated string with format args applied.
        """
        value = get_nested_value(translations, key, default=key)
        if kwargs:
            # If formatting fails, return unformatted value
            with contextlib.suppress(KeyError, ValueError):
                value = value.format(**kwargs)
        return value

    return translate, lang
