import uuid
from datetime import datetime
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
)

Username = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=30,
        pattern=r"^[A-Za-z0-9_]+$",
    ),
]

Email = Annotated[EmailStr, AfterValidator(str.lower)]


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Username
    email: Email
    password: str = Field(min_length=8, max_length=128, repr=False)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    profile_pic_url: str | None = None
    created_at: datetime