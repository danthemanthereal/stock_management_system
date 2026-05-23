import uuid
import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from fastapi_camelcase import CamelModel

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"

class UserInfoResponse(CamelModel):
    username: str
    reveal_credits: float
    reverse_credits: float
    id: uuid.UUID
    created: datetime.datetime
    status: UserStatus
    api_key: str
    callback_url: Optional[str]
    is_admin: bool

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class LoginRequest(CamelModel):
    username: str
    password: str

class LoginResponseData(CamelModel):
    access_token: Optional[str]
    user: UserInfoResponse

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8)

    @field_validator("username")
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Nur Buchstaben, Zahlen und Unterstrich erlaubt")
        return v

    @field_validator("password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Passwort muss mindestens einen Großbuchstaben enthalten")
        if not re.search(r"[a-z]", v):
            raise ValueError("Passwort muss mindestens einen Kleinbuchstaben enthalten")
        if not re.search(r"\d", v):
            raise ValueError("Passwort muss mindestens eine Zahl enthalten")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Passwort muss mindestens ein Sonderzeichen enthalten")
        return v