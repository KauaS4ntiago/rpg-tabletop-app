from fastapi import APIRouter, Response, status

from app.api.dependencies import AuthServiceDep
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
async def register(data: UserCreate, service: AuthServiceDep) -> User:
    return await service.register(data)


@router.post(
    "/login", response_model=TokenResponse
)
async def login(
    data: LoginRequest, service: AuthServiceDep, response: Response
) -> TokenResponse:
    token = await service.login(data.email, data.password)
    response.headers["Cache-Control"] = "no-store"
    return TokenResponse(access_token=token)