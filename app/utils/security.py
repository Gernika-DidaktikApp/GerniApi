"""Security utilities for password hashing and JWT token management.

This module provides cryptographic functions for secure password storage
using bcrypt and JWT token generation/validation for authentication.

Autor: Gernibide
"""

import os
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from app.config import settings
from app.logging import log_debug, log_error, log_warning


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


# ==================== Token Blacklist (Logout) ====================

# Cliente Redis para blacklist de tokens
_redis_client = None
# Fallback en memoria si Redis no está disponible (solo para desarrollo)
_memory_blacklist: dict[str, float] = {}


def _get_redis_client():
    """Obtiene o crea una conexión Redis para la blacklist de tokens.

    Intenta conectar a Redis en este orden:
    1. REDIS_URL de entorno (producción)
    2. Redis local (desarrollo)
    3. Fallback a None (usar memoria)

    Returns:
        Cliente Redis o None si no está disponible.
    """
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    # Intentar REDIS_URL de entorno
    redis_url = settings.REDIS_URL if hasattr(settings, "REDIS_URL") else os.getenv("REDIS_URL")
    if redis_url:
        try:
            import redis

            _redis_client = redis.from_url(redis_url, decode_responses=True)
            _redis_client.ping()
            log_debug("Blacklist de tokens usando Redis", redis_url="***")
            return _redis_client
        except Exception as e:
            log_warning(f"No se pudo conectar a Redis para blacklist: {e}")

    # Intentar Redis local
    try:
        import redis

        _redis_client = redis.Redis(
            host="localhost", port=6379, db=1, decode_responses=True, socket_connect_timeout=1
        )
        _redis_client.ping()
        log_debug("Blacklist de tokens usando Redis local")
        return _redis_client
    except Exception:
        pass

    # Sin Redis disponible
    log_warning("Redis no disponible para blacklist de tokens - usando memoria (no persistente)")
    return None


def add_token_to_blacklist(token: str) -> bool:
    """Añade un token JWT a la blacklist para invalidarlo.

    El token se almacena en Redis con TTL automático igual al tiempo
    restante hasta su expiración. Esto previene que tokens válidos
    se reutilicen después de logout.

    Args:
        token: Token JWT a invalidar.

    Returns:
        True si se añadió correctamente, False si hubo error.
    """
    try:
        # Decodificar token para obtener exp
        payload = decode_access_token(token)
        if not payload or "exp" not in payload:
            log_warning("No se pudo decodificar token para blacklist")
            return False

        # Calcular TTL (tiempo restante hasta expiración)
        exp_timestamp = payload["exp"]
        now_timestamp = datetime.now(UTC).timestamp()
        ttl_seconds = int(exp_timestamp - now_timestamp)

        # Si ya expiró, no hace falta añadirlo a blacklist
        if ttl_seconds <= 0:
            log_debug("Token ya expirado, no se añade a blacklist")
            return True

        # Intentar añadir a Redis
        redis_client = _get_redis_client()
        if redis_client:
            key = f"blacklist:{token}"
            redis_client.setex(key, ttl_seconds, "1")
            log_debug("Token añadido a blacklist en Redis", ttl=ttl_seconds)
            return True

        # Fallback a memoria (no persistente)
        _memory_blacklist[token] = exp_timestamp
        log_debug("Token añadido a blacklist en memoria", ttl=ttl_seconds)
        return True

    except Exception as e:
        log_error(f"Error al añadir token a blacklist: {e}")
        return False


def is_token_blacklisted(token: str) -> bool:
    """Verifica si un token JWT está en la blacklist.

    Args:
        token: Token JWT a verificar.

    Returns:
        True si el token está en blacklist (invalidado), False en caso contrario.
    """
    try:
        # Verificar en Redis
        redis_client = _get_redis_client()
        if redis_client:
            key = f"blacklist:{token}"
            result = redis_client.exists(key)
            return bool(result)

        # Verificar en memoria y limpiar tokens expirados
        now_timestamp = datetime.now(UTC).timestamp()
        # Limpiar tokens expirados de memoria
        expired_tokens = [t for t, exp in _memory_blacklist.items() if exp <= now_timestamp]
        for t in expired_tokens:
            del _memory_blacklist[t]

        return token in _memory_blacklist

    except Exception as e:
        log_error(f"Error al verificar token en blacklist: {e}")
        # En caso de error, permitir el token (fail-open para no bloquear usuarios)
        return False
