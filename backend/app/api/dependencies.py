from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_auth_service(
    session: SessionDep, users: UserRepositoryDep
) -> AuthService:
    return AuthService(session, users)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]