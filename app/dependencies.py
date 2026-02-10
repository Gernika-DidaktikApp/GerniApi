"""Funciones de dependencias para endpoints de FastAPI.

Este módulo maneja la autenticación y autorización de usuarios,
validando tokens JWT y extrayendo información del usuario actual.

Autor: Gernibide
"""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.profesor import Profesor

security = HTTPBearer()


def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> dict:
    """
    Validates JWT token and returns current user data.

    Extracts the token from Authorization header, validates it,
    and returns user information including profesor_id if applicable.

    Args:
        credentials: HTTP Bearer credentials from header
        db: Database session

    Returns:
        Dictionary with user data (username, profesor_id if profesor, etc.)

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        # Decode JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        username: str = payload.get("sub")
        user_type: str = payload.get("type")  # "profesor" or None for usuario

        if username is None:
            raise credentials_exception

        # If it's a profesor, get profesor data
        if user_type == "profesor":
            profesor = db.query(Profesor).filter(Profesor.username == username).first()
            if not profesor:
                raise credentials_exception

            return {
                "username": username,
                "type": "profesor",
                "profesor_id": profesor.id,
                "nombre": profesor.nombre,
                "apellido": profesor.apellido,
            }

        # For regular usuarios (not yet implemented, but structure ready)
        return {"username": username, "type": "usuario"}

    except InvalidTokenError:
        raise credentials_exception
