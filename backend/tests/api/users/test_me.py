import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from sqlalchemy import text

from app.core.config import get_settings

ME_URL = "/api/v1/users/me"


def _payload(*, token_type="access", expires_in=timedelta(minutes=5)) -> dict:
    return {
        "sub": str(uuid.uuid4()),
        "type": token_type,
        "exp": datetime.now(UTC) + expires_in,
    }


def _signed(payload: dict, key: str | None = None) -> str:
    secret = key or get_settings().secret_key.get_secret_value()
    return jwt.encode(payload, secret, algorithm="HS256")


# Factories, so each token is built inside the test, after the settings exist.
INVALID_TOKENS = {
    "garbage": lambda: "not-a-jwt",
    "expired": lambda: _signed(_payload(expires_in=timedelta(minutes=-1))),
    "wrong_token_type": lambda: _signed(_payload(token_type="refresh")),
    "wrong_signing_key": lambda: _signed(_payload(), key="x" * 40),
    "unsigned": lambda: jwt.encode(_payload(), None, algorithm="none"),
    "unknown_user": lambda: _signed(_payload()),
}


async def test_me_requires_authentication(client):
    response = await client.get(ME_URL)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


async def test_me_rejects_other_auth_schemes(client):
    response = await client.get(ME_URL, headers={"Authorization": "Basic dXNlcjpwYXNz"})

    assert response.status_code == 401


@pytest.mark.parametrize(
    "make_token", list(INVALID_TOKENS.values()), ids=list(INVALID_TOKENS)
)
async def test_me_rejects_invalid_tokens(client, make_token):
    headers = {"Authorization": f"Bearer {make_token()}"}

    response = await client.get(ME_URL, headers=headers)

    assert response.status_code == 401


async def test_me_returns_the_current_user(client, registered_user, auth_headers):
    response = await client.get(ME_URL, headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == registered_user["username"]
    assert body["email"] == registered_user["email"]
    assert "password_hash" not in body


async def test_me_rejects_the_token_of_a_deleted_user(client, auth_headers, db_session):
    await db_session.execute(text("DELETE FROM users"))
    # The test shares one session with the app, so forget the cached user,
    # as a new request in production would.
    db_session.expunge_all()

    response = await client.get(ME_URL, headers=auth_headers)

    assert response.status_code == 401