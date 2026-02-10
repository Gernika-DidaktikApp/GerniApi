"""Security utilities for password hashing and JWT token management.

This module provides cryptographic functions for secure password storage
using bcrypt and JWT token generation/validation for authentication.

Autor: Gernibide
"""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from app.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Bcrypt automatically truncates to 72 bytes and includes salt generation.

    Args:
        password: Plain text password to hash.

    Returns:
        Hashed password as a UTF-8 encoded string.
    """
    # Convertir a bytes
    password_bytes = password.encode("utf-8")
    # Generar salt y hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Retornar como string
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if a password matches its hash.

    Bcrypt automatically truncates to 72 bytes during verification.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Hashed password to compare against.

    Returns:
        True if password matches hash, False otherwise or on error.
    """
    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token.

    Generates a signed JWT token with an expiration time. If no expiration
    delta is provided, defaults to 15 minutes.

    Args:
        data: Dictionary of claims to encode in the token (e.g., {"sub": "username"}).
        expires_delta: Optional custom expiration duration. Defaults to 15 minutes.

    Returns:
        Encoded JWT token as a string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT access token.

    Args:
        token: JWT token string to decode.

    Returns:
        Dictionary containing the token payload if valid, None if invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except InvalidTokenError:
        return None


def generar_codigo_clase() -> str:
    """Genera un código alfanumérico único de 6 caracteres para una clase.

    El código es fácil de compartir y recordar (ej: "A3X9K2").
    Usa caracteres alfanuméricos mayúsculas y dígitos para evitar ambigüedad.

    Returns:
        Código de 6 caracteres (A-Z, 0-9).

    Examples:
        >>> codigo = generar_codigo_clase()
        >>> len(codigo)
        6
        >>> codigo.isupper()
        True
    """
    import random
    import string

    # Solo mayúsculas y dígitos para evitar confusión (sin 0/O, 1/I/l)
    caracteres = string.ascii_uppercase.replace("O", "").replace("I", "") + string.digits.replace(
        "0", ""
    ).replace("1", "")
    return "".join(random.choices(caracteres, k=6))
