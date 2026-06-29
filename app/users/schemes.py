from datetime import datetime
import uuid

from pydantic import BaseModel, Field, ConfigDict


class AuthUserModel(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        from_attributes=True
    )
    
    login: str
    password: str


class RegistrationUserModel(AuthUserModel):
    first_name: str = Field(max_length=128)
    last_name: str = Field(max_length=128)


class UserModel(RegistrationUserModel):
    id: uuid.UUID