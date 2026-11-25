from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class AuthUserOut(BaseModel):
    id: int
    email: str
    steam_linked: bool


class SessionOut(BaseModel):
    id: UUID
    created_at: datetime
    last_used_at: datetime
    user_agent: str | None