import uuid

import pytest

from app.core import security

pytestmark = pytest.mark.usefixtures("test_environment")


async def test_hash_uses_argon2id_with_a_unique_salt():
    first = await security.hash_password("correct-horse-1")
    second = await security.hash_password("correct-horse-1")

    assert first.startswith("$argon2id$")
    assert first != second


async def test_verify_password_accepts_the_right_password_only():
    hashed = await security.hash_password("correct-horse-1")

    assert (await security.verify_password("correct-horse-1", hashed))[0] is True
    assert (await security.verify_password("wrong-password", hashed))[0] is False


def test_access_token_round_trip():
    user_id = uuid.uuid4()

    token = security.create_access_token(user_id)

    assert security.decode_access_token(token) == user_id


def test_tampered_token_is_rejected():
    token = security.create_access_token(uuid.uuid4())

    assert security.decode_access_token(token + "x") is None