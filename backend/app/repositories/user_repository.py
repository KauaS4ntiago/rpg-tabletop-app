import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    UsernameAlreadyTakenError,
)
from app.models import User

EMAIL_UNIQUE_CONSTRAINT = "uq_users_email"
USERNAME_UNIQUE_CONSTRAINT = "uq_users_username"


def _violated_constraint(exc: IntegrityError) -> str | None:
    cause = exc.orig.__cause__ if exc.orig is not None else None
    name = getattr(cause, "constraint_name", None)
    if name:
        return name
    message = str(exc.orig)
    for constraint in (EMAIL_UNIQUE_CONSTRAINT, USERNAME_UNIQUE_CONSTRAINT):
        if constraint in message:
            return constraint
    return None


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self._session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create(
        self, *, username: str, email: str, password_hash: str
    ) -> User:
        user = User(username=username, email=email, password_hash=password_hash)
        try:
            async with self._session.begin_nested():
                self._session.add(user)
        except IntegrityError as exc:
            constraint = _violated_constraint(exc)
            if constraint == EMAIL_UNIQUE_CONSTRAINT:
                raise EmailAlreadyRegisteredError from exc
            if constraint == USERNAME_UNIQUE_CONSTRAINT:
                raise UsernameAlreadyTakenError from exc
            raise
        return user