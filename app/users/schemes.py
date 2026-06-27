from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class RegistrationUserModel(BaseModel):
    login: str
    password: str
    first_name: str = Field(max_length=128)
    last_name: str = Field(max_length=128)


class AuthUserModel(BaseModel):
    login: str
    password: str


class UserModel(BaseModel):
    id: uuid.UUID
    login: str
    first_name: str
    last_name: str
    created_at: datetime
