from typing import Any

from app.models.message import Message
from app.models.users import User
from app.models.chat_member import ChatMember
from app.models.chat import Chat


class Protocol:
    @staticmethod
    def get_success_message(message: str):
        return {
            "type": "success",
            "details": message
        }
    
    @staticmethod
    def get_json_error():
        return {
            "type": "json_decode_error",
            "details": "wrong json payload"
        }
    
    @staticmethod
    def get_message_notify(message: Message, actor: User, acceptor: ChatMember) -> dict[str, Any]:
        return {
            "type": "new_msg",
            "details": {
                "chat_id": str(message.chat_id),
                "message": message.text,
                "actor": Protocol.get_user(actor),
                "acceptor": str(acceptor.user_id)
            }
        }
    
    @staticmethod
    def get_user(user: User) -> dict[str, Any]:
        return {
            "id": str(user.id),
            "username": user.login,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    
    @staticmethod
    def get_chat(chat: Chat):
        return {
            "id": chat.id,
            "title": chat.title,
            "photo": chat.photo,
            "desc": chat.desc
        }
    
    @staticmethod
    def get_data_error(reason: str):
        return {
            "type": "error",
            "reason": reason
        }
    
    @staticmethod
    def get_created_message():
        return {
            "status": "created"
        }
    
    @staticmethod
    def get_message(message: Message):
        return {
            "id": message.id,
            "message": message.text,
            "actor": Protocol.get_user(message.user),
            "chat": Protocol.get_chat(message.chat)
        }
