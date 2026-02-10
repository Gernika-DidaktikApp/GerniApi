"""Endpoints para internacionalización (i18n).

Este módulo proporciona endpoints para gestionar la preferencia de idioma del usuario.

Autor: Gernibide
"""

from fastapi import APIRouter, Response
from pydantic import BaseModel

from app.logging.logger import log_info

router = APIRouter(prefix="/api", tags=["🌐 i18n"])


class LanguageRequest(BaseModel):
    """Request model for language change."""

    language: str


@router.post(
    "/set-language",
    summary="Set user language preference",
    description="Sets the user's language preference via cookie",
)
async def set_language(data: LanguageRequest, response: Response):
    """Set user language preference.

    Args:
        data: Language code to set ('es' or 'eu').
        response: FastAPI Response object to set cookie.

    Returns:
        Dictionary with the language code or error message.
    """
    if data.language not in ["es", "eu"]:
        return {"error": "Unsupported language"}

    response.set_cookie(
        key="language",
        value=data.language,
        max_age=31536000,  # 1 year
        httponly=False,  # Accessible from JS
        samesite="lax",
    )

    log_info(
        "Idioma cambiado",
        language=data.language,
    )

    return {"language": data.language}
