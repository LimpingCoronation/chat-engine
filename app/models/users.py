import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    login: str = Field(max_length=128, unique=True)
    first_name: str = Field(max_length=128)
    last_name: str = Field(max_length=128)
    password: str
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
