from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import Email


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: Email
    password: str = Field(min_length=1, max_length=128, repr=False)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"