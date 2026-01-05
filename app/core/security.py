import secrets
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Any, Optional, Union

from jose import jwt

from app.core.config import settings


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    # Split hash and salt
    try:
        stored_hash, salt = hashed_password.split("$")
    except ValueError:
        return False

    computed_hash = sha256(f"{plain_password}{salt}".encode()).hexdigest()
    return stored_hash == computed_hash


def get_password_hash(password: str) -> str:
    """Generate password hash with salt"""
    salt = secrets.token_hex(16)
    password_hash = sha256(f"{password}{salt}".encode()).hexdigest()
    return f"{password_hash}${salt}"


def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return email if valid"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except jwt.JWTError:
        return None
