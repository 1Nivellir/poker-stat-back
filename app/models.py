import uuid
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime, timezone
from typing import Optional
# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field()
    tournaments: list["Torney"] = Relationship(back_populates="user")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID

class Torney(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    play_date: datetime | None = Field()
    name: str = Field(max_length=255)
    buy_in: int = Field(default=None)
    re_entry: int | None
    bounty: int | None
    prize: int | None

    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates='tournaments')


class TorneyCreate(SQLModel):
    name: str = Field(max_length=255)
    play_date: Optional[datetime] = None
    buy_in: Optional[int] = None
    re_entry: Optional[int] = None
    bounty: Optional[int] = None
    prize: Optional[int] = None

class TorneyUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=255)
    play_date: Optional[datetime] = None
    buy_in: Optional[int] = None
    re_entry: Optional[int] = None
    bounty: Optional[int] = None
    prize: Optional[int] = None

class TorneyRead(SQLModel):
    id: uuid.UUID
    name: str
    play_date: Optional[datetime] = None
    buy_in: Optional[int] = None
    re_entry: Optional[int] = None
    bounty: Optional[int] = None
    prize: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    user_id: uuid.UUID
    user: Optional[UserBase] = None

class Message(SQLModel):
    message: str

# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

# JSON payload with access and refresh tokens
class TokenWithRefresh(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None

# Refresh token request
class RefreshTokenRequest(SQLModel):
    refresh_token: str


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)