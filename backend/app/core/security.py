import asyncio
import uuid
import secrets
import hashlib
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

ALGORITHM = "HS256"
ACCESS_TOKEN_TYPE = "access"

_password_hash = PasswordHash.recommended()

# Used to spend the same time hashing when the user does not exist,
# so response timing does not reveal which emails are registered.
DUMMY_HASH = _password_hash.hash("not-a-real-password")


async def hash_password(password: str) -> str:
    return await asyncio.to_thread(_password_hash.hash, password)


async def verify_password(password: str, hashed: str) -> tuple[bool, str | None]:
    """Return (is_valid, new_hash). new_hash is set when the stored hash
    uses outdated parameters and should be replaced."""
    return await asyncio.to_thread(
        _password_hash.verify_and_update, password, hashed
    )


def create_access_token(user_id: uuid.UUID) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "type": ACCESS_TOKEN_TYPE,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(
        payload, settings.secret_key.get_secret_value(), algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> uuid.UUID | None:
    """Return the user id if the token is valid, otherwise None."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        if payload.get("type") != ACCESS_TOKEN_TYPE:
            return None
        return uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError):
        return None
    
def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)

def hash_refresh_token(token: str) -> str:
    hash_token = hashlib.sha256(token.encode('UTF-8'))
    
    return hash_token.hexdigest()
     