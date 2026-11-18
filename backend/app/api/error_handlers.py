from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UsernameAlreadyTakenError,
)


def _error(
    status_code: int, detail: str, headers: dict[str, str] | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content={"detail": detail}, headers=headers
    )


async def email_already_registered_handler(
    request: Request, exc: EmailAlreadyRegisteredError
) -> JSONResponse:
    return _error(status.HTTP_409_CONFLICT, "Email already registered")


async def username_taken_handler(
    request: Request, exc: UsernameAlreadyTakenError
) -> JSONResponse:
    return _error(status.HTTP_409_CONFLICT, "Username already taken")


async def invalid_credentials_handler(
    request: Request, exc: InvalidCredentialsError
) -> JSONResponse:
    return _error(
        status.HTTP_401_UNAUTHORIZED,
        "Invalid email or password",
        {"WWW-Authenticate": "Bearer"},
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        EmailAlreadyRegisteredError, email_already_registered_handler
    )
    app.add_exception_handler(UsernameAlreadyTakenError, username_taken_handler)
    app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)