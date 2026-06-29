import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship

from app.models.enums.role import Role
from app.models.users import User
from app.models.chat import Chat


class ChatMember(SQLModel, table=True):
    __tablename__ = "chat_member"
    
    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    chat_id: uuid.UUID = Field(foreign_key="chat.id", primary_key=True)
    role: Role = Field(nullable=False)
    
    user: User = Relationship()
    chat: Chat = Relationship()
