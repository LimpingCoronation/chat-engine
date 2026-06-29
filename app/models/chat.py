import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field

from app.models.enums.chat_types import ChatTypes


class Chat(SQLModel, table=True):
    __tablename__ = "chat"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    common_id: str
    chat_types: ChatTypes
    photo: str | None = Field(default=None)
    title: str = Field(max_length=128, nullable=False)
    desc: str | None = Field(max_length=1024, default=None)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
