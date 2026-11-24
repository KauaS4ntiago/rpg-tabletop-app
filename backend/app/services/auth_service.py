from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError
from app.core.security import (
    DUMMY_HASH,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, session: AsyncSession, users: UserRepository) -> None:
        self._session = session
        self._users = users

    async def register(self, data: UserCreate) -> User:
        password_hash = await hash_password(data.password)
        user = await self._users.create(
            username=data.username,
            email=data.email,
            password_hash=password_hash,
        )
        await self._session.commit()
        return user

    async def login(self, email: str, password: str) -> str:
        user = await self._users.get_by_email(email)

        # Always verify against some hash, so an unknown email costs the
        # same time as a wrong password.
        stored_hash = user.password_hash if user else DUMMY_HASH
        is_valid, new_hash = await verify_password(password, stored_hash)

        if user is None or not is_valid:
            raise InvalidCredentialsError

        if new_hash is not None:
            user.password_hash = new_hash
            await self._session.commit()

        return create_access_token(user.id)