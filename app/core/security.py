"""JWT token issuance/verification and password hashing utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class InvalidTokenError(Exception):
    """Raised when a JWT is missing, expired, malformed, or of the wrong type."""


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token.

    Args:
        data: claims to embed in the token, e.g. {"sub": username, "role": role}.
        expires_delta: optional override for the token lifetime. Defaults to
            `settings.access_token_expire_minutes`.

    Returns:
        str: the encoded JWT.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a signed JWT refresh token.

    Args:
        data: claims to embed in the token, e.g. {"sub": username, "role": role}.

    Returns:
        str: the encoded JWT.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def verify_token(token: str, token_type: str) -> dict[str, Any]:
    """Decode a JWT and verify its signature, expiry, and type.

    Args:
        token: the encoded JWT.
        token_type: the expected value of the token's "type" claim, either
            "access" or "refresh".

    Returns:
        dict[str, Any]: the decoded token claims.

    Raises:
        InvalidTokenError: if the token is malformed, expired, or of the wrong type.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise InvalidTokenError("Could not validate token") from exc

    if payload.get("type") != token_type:
        raise InvalidTokenError(f"Expected a {token_type} token")

    return payload


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a bcrypt hash.

    Args:
        plain_password: the password supplied by the caller.
        hashed_password: the bcrypt hash to compare against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        password: the plaintext password to hash.

    Returns:
        str: the bcrypt hash, safe to store.
    """
    return pwd_context.hash(password)
