import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field, Column, JSON


class Message(SQLModel, table=True):
    __tablename__ = "message"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    text: str | None
    photo: list[str] = Field(default=[], sa_column=Column(JSON))
    is_read: bool = Field(default=False)
    is_delivered: bool = Field(default=False)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    chat_id: uuid.UUID = Field(foreign_key="chat.id")
    created_at: datetime = Field(default_factory=datetime.now)
