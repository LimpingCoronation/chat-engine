import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field

from models.enums.role import Role


class ChatMember(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    chat_id: uuid.UUID = Field(foreign_key="chat.id", primary_key=True)
    role: Role = Field(nullable=False)
