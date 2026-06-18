"""Password hashing, JWT encode/decode, and httpOnly cookie helpers."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from fastapi import Response
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, token_version: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    payload = {
        "sub": str(user_id),
        "ver": token_version,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decode and verify the access JWT. Raises jose.JWTError on failure."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def generate_refresh_token() -> str:
    """Return a raw URL-safe random token (86 chars). Store only the hash."""
    return secrets.token_urlsafe(64)


def hash_refresh_token(raw: str) -> str:
    return sha256(raw.encode()).hexdigest()


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Write httpOnly cookies for access + refresh tokens."""
    common: dict = dict(
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain or None,
        path="/",
    )
    response.set_cookie(
        key=settings.access_cookie_name,
        value=access_token,
        max_age=settings.access_token_minutes * 60,
        **common,
    )
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        max_age=settings.refresh_token_days * 86400,
        **common,
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key=settings.access_cookie_name, path="/")
    response.delete_cookie(key=settings.refresh_cookie_name, path="/")
