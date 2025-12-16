"""JWT token creation and validation utilities.

This module provides JWT authentication functionality including token generation
and verification.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException, status
from jose import JWTError, jwt

from ingenious.core.structured_logging import get_logger

logger = get_logger(__name__)

# Default JWT configuration values
_DEFAULT_ALGORITHM = "HS256"
_DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 1440
_DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = 7


class JWTConfigurationError(Exception):
    """Raised when JWT is not properly configured."""

    pass


def _get_env_str(*keys: str, default: Optional[str] = None) -> Optional[str]:
    """Get the first non-empty value from environment variables."""
    for key in keys:
        value = os.getenv(key, "")
        if value:
            return value
    return default


def _get_env_int(*keys: str, default: int = 0) -> int:
    """Get the first non-zero int value from environment variables."""
    for key in keys:
        value = os.getenv(key, "0")
        try:
            parsed = int(value)
            if parsed:
                return parsed
        except ValueError:
            continue
    return default


def _get_jwt_secret_key() -> str:
    """Get JWT secret key from environment, failing if not configured.

    Returns:
        The JWT secret key

    Raises:
        JWTConfigurationError: If no secret key is configured
    """
    secret_key = _get_env_str("INGENIOUS_JWT_SECRET_KEY", "JWT_SECRET_KEY")
    if not secret_key:
        raise JWTConfigurationError(
            "JWT secret key is not configured. "
            "Set INGENIOUS_JWT_SECRET_KEY environment variable with a strong, "
            "random secret key (at least 32 characters recommended). "
            'You can generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
        )
    return secret_key


def _get_jwt_config_from_env() -> Tuple[str, str, int, int]:
    """Get JWT configuration purely from environment variables."""
    return (
        _get_jwt_secret_key(),
        _get_env_str("INGENIOUS_JWT_ALGORITHM") or _DEFAULT_ALGORITHM,
        _get_env_int(
            "INGENIOUS_JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            default=_DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
        ),
        _get_env_int(
            "INGENIOUS_JWT_REFRESH_TOKEN_EXPIRE_DAYS", default=_DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS
        ),
    )


def _get_jwt_config() -> Tuple[str, str, int, int]:
    """Get JWT configuration from settings or environment variables."""
    try:
        from ingenious.config.config import get_config

        config = get_config()
        auth_config = config.web_configuration.authentication

        # Secret key is required - no fallback to insecure default
        secret_key = auth_config.jwt_secret_key or _get_env_str(
            "INGENIOUS_JWT_SECRET_KEY", "JWT_SECRET_KEY"
        )
        if not secret_key:
            raise JWTConfigurationError(
                "JWT secret key is not configured. "
                "Set INGENIOUS_JWT_SECRET_KEY environment variable or "
                "INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__JWT_SECRET_KEY "
                "with a strong, random secret key (at least 32 characters recommended). "
                'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
            )

        algorithm = (
            auth_config.jwt_algorithm
            or _get_env_str("INGENIOUS_JWT_ALGORITHM")
            or _DEFAULT_ALGORITHM
        )

        access_token_expire = auth_config.jwt_access_token_expire_minutes or _get_env_int(
            "INGENIOUS_JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            default=_DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        refresh_token_expire = auth_config.jwt_refresh_token_expire_days or _get_env_int(
            "INGENIOUS_JWT_REFRESH_TOKEN_EXPIRE_DAYS",
            "JWT_REFRESH_TOKEN_EXPIRE_DAYS",
            default=_DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
        )

        return secret_key, algorithm, access_token_expire, refresh_token_expire
    except JWTConfigurationError:
        raise
    except Exception:
        return _get_jwt_config_from_env()


# Lazy-initialized JWT configuration (only loaded when JWT functions are called)
_jwt_config: Optional[Tuple[str, str, int, int]] = None


def _ensure_jwt_config() -> Tuple[str, str, int, int]:
    """Ensure JWT config is loaded, initializing lazily on first use.

    This allows the module to be imported without failing if JWT is not configured,
    but will fail with a clear error when JWT functions are actually called.
    """
    global _jwt_config
    if _jwt_config is None:
        _jwt_config = _get_jwt_config()
    return _jwt_config


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with expiration."""
    secret_key, algorithm, access_expire, _ = _ensure_jwt_config()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=access_expire)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return str(encoded_jwt)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token with extended expiration."""
    secret_key, algorithm, _, refresh_expire = _ensure_jwt_config()
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=refresh_expire)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return str(encoded_jwt)


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:  # nosec B107
    """Verify and decode a JWT token, checking type and expiration."""
    secret_key, algorithm, _, _ = _ensure_jwt_config()
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])

        # Check if token type matches expected type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if token has expired
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing expiration",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return dict(payload)

    except JWTError as e:
        logger.debug("JWT verification failed", error=str(e), token_type=token_type)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_username_from_token(token: str) -> str:
    """Extract username from a valid JWT token after verification."""
    payload = verify_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return str(username)
