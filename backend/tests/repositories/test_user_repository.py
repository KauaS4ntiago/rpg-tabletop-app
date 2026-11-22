import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    UsernameAlreadyTakenError,
)
from app.repositories.user_repository import UserRepository
from unittest.mock import AsyncMock


async def test_create_translates_duplicate_email(db_session, registered_user):
    repository = UserRepository(db_session)

    with pytest.raises(EmailAlreadyRegisteredError):
        await repository.create(
            username="another_user",
            email=registered_user["email"],
            password_hash="hashed-password",
        )


async def test_create_translates_duplicate_username(db_session, registered_user):
    repository = UserRepository(db_session)

    with pytest.raises(UsernameAlreadyTakenError):
        await repository.create(
            username=registered_user["username"],
            email="another@example.com",
            password_hash="hashed-password",
        )


async def test_create_reraises_unknown_integrity_error(db_session, monkeypatch):
    repository = UserRepository(db_session)
    original = Exception("unexpected constraint")
    integrity_error = IntegrityError("INSERT", {}, original)

    class FailingNestedTransaction:
        async def __aenter__(self):
            raise integrity_error

        async def __aexit__(self, exc_type, exc, traceback):
            return False

    monkeypatch.setattr(
        db_session,
        "begin_nested",
        lambda: FailingNestedTransaction(),
    )

    with pytest.raises(IntegrityError) as exc_info:
        await repository.create(
            username="new_user",
            email="new@example.com",
            password_hash="hashed-password",
        )

    assert exc_info.value is integrity_error
    assert exc_info.value.orig is original