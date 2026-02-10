"""Loader de traducciones con caché en memoria.

Este módulo carga archivos JSON de traducciones y los mantiene
en caché para mejorar el rendimiento.

Autor: Gernibide
"""

import json
from pathlib import Path
from typing import Any

_translations_cache: dict[str, dict[str, Any]] = {}


def load_translations(lang: str) -> dict[str, Any]:
    """Load translations from JSON file with caching.

    Args:
        lang: Language code (e.g., 'es', 'eu').

    Returns:
        Dictionary with all translations for the specified language.
        Falls back to Spanish if language file not found.
    """
    if lang in _translations_cache:
        return _translations_cache[lang]

    file_path = Path(__file__).parent / f"{lang}.json"
    if not file_path.exists():
        # Fallback to Spanish if lang not found
        file_path = Path(__file__).parent / "es.json"

    with open(file_path, encoding="utf-8") as f:
        translations = json.load(f)

    _translations_cache[lang] = translations
    return translations


def get_nested_value(data: dict, key: str, default: str = "") -> str:
    """Get value from nested dict using dot notation.

    Args:
        data: Dictionary to search in.
        key: Dot-separated key path (e.g., 'common.nav.home').
        default: Default value if key not found.

    Returns:
        String value at the specified path, or default if not found.

    Example:
        >>> get_nested_value({'common': {'nav': {'home': 'Inicio'}}}, 'common.nav.home')
        'Inicio'
    """
    keys = key.split(".")
    value = data
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return default
    return value if value is not None else default
