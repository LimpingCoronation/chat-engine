import uuid
from typing import Any

from fastapi import WebSocket
from fastapi.exceptions import WebSocketException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.base_repository import get_repository
from app.core.database.setup_db import get_session
from app.core.safety.jwt import verify_token
from app.models.users import User
from app.models.chat import Chat
from app.models.chat_member import ChatMember
from app.models.message import Message
from app.core.config import logger
from app.websocket.redis_manager import RedisManager
from app.websocket.state import manager
from app.websocket.protocol import Protocol
from app.models.enums.chat_types import ChatTypes
from app.models.enums.role import Role


# WEBSOCKET HANDLERS

async def get_user(
        ws: WebSocket, 
        payload: dict, 
        connections: dict, 
        db_session: AsyncSession,
        use_db: bool = False,
        raise_exceptions: bool = True
) -> User:
    if connections.get(ws) is not None:
        return connections.get(ws)

    token = payload.get('token')
    if token is None:
        raise WebSocketException(code=1002, reason="Token not specified")

    if use_db:
        payload = verify_token(token)
        if payload is not None:
            users_repo = get_repository(db_session, User)
            user = await users_repo.get_first(**{"id": uuid.UUID(payload["id"])}) 
            manager.authorize(ws, user)

            if user is not None:
                return user
    
    if raise_exceptions:
        raise WebSocketException(code=1001, reason="Wrong token")


async def notify(chat: Chat, message: Message, actor: User, db_session: AsyncSession,):
    chat_member_repo = get_repository(db_session, ChatMember)
    memebers = await chat_member_repo.list(chat_id = chat.id)
    manager = RedisManager.get_instance()

    for m in memebers:
        payload = Protocol.get_message_notify(message, actor, m)
        await manager.notify(payload)


async def ping(ws: WebSocket, payload: dict, connections: dict, db_session: AsyncSession):
    return {
        "type": "response",
        "details": "pong"
    }


async def auth(ws: WebSocket, payload: dict, connections: dict, db_session: AsyncSession) -> dict:
    user = await get_user(ws, payload, connections, db_session, use_db=True)
    manager.authorize(ws, user)

    logger.info(f"{user.login} authorized")

    return {
        "type": "auth",
        "details": {
            "id": str(user.id),
            "login": user.login
        }
    }


async def check_auth(ws: WebSocket, payload: dict, connections: dict, db_session: AsyncSession):
    user = await get_user(ws, payload, connections, db_session, False, False)

    if user is None:
        raise WebSocketException(code=1002, reason="Not authorized")

    return {
        "status": "ok",
        "details": {
            "id": str(user.id),
            "login": user.login
        }
    }


async def message(ws: WebSocket, payload: dict, connections: dict, db_session: AsyncSession):
    user = await get_user(ws, payload, connections, db_session)
    chat_id = payload.get("chat_id")
    text = payload.get("text")
    contact_id = payload.get("contact_id")

    if not text:
        raise WebSocketException(code=1007, reason="Wrong data")
    
    chat_repo = get_repository(db_session, Chat)
    chat_member_repo = get_repository(db_session, ChatMember)
    message_repo = get_repository(db_session, Message)
    chat = None
    msg = None
    
    if chat_id is not None:
        chat = await chat_repo.get_first(id = uuid.UUID(chat_id))
        member = await chat_member_repo.get_first(
            user_id = uuid.UUID(user.id),
            chat_id = uuid.UUID(chat.id)
        )

        if member is not None:
            msg = await message_repo.create(
                text = text,
                user_id = uuid.UUID(user.id),
                chat_id = uuid.UUID(chat.id)
            )
        
        return Protocol.get_created_message()
    elif contact_id is not None:
        chat: Chat = await chat_repo.get_first(common_id = str(user.id) + contact_id)
        if chat is None:
            chat = await chat_repo.create(
                common_id = str(user.id) + contact_id,
                title = "Private chat",
                chat_types = ChatTypes.CHAT
            )
            
            for user_id in [user.id, uuid.UUID(contact_id)]:
                await chat_member_repo.create(
                    user_id = user_id,
                    chat_id = chat.id,
                    role=Role.USER
                )
        
        msg = await message_repo.create(
            text = text,
            user_id = user.id,
            chat_id = chat.id
        )
    
    await db_session.commit()

    if chat is None or msg is None:
        raise WebSocketException(code=1007, reason="Chat is not selected")
    else:
        await notify(chat, msg, user, db_session)
        return Protocol.get_success_message("message created")


async def get_history(ws: WebSocket, payload: dict[str, Any], connections: dict[WebSocket, User], db_session: AsyncSession):
    user = await get_user(ws, payload, connections, db_session)
    
    chat_id = payload.get('chat_id')
    limit = payload.get('limit', 100)
    
    if chat_id is None:
        raise WebSocketException(code=1007, reason="Wrong data")
    
    chat_id = uuid.UUID(chat_id)
    chat_member_repo = get_repository(db_session, ChatMember)
    message_repo = get_repository(db_session, Message)
    member = await chat_member_repo.get_first(user_id=user.id, chat_id=chat_id)
    
    if member is None:
        raise WebSocketException(code=1007, reason="No such chat")
    
    messages = await message_repo.list(chat_id=chat_id)[:limit]
    
    return {
        "type": "messages",
        "details": {
            "messages": [Protocol.get_message(m) for m in messages]
        }
    }
    

manager.add_handler("auth", auth)
manager.add_handler("ping", ping)
manager.add_handler("check_auth", check_auth)
manager.add_handler("message", message)
manager.add_handler("get_history", get_history)

# REDIS HANDLERS

async def send_message(payload: dict[str, Any], connections: dict[str, WebSocket]):
    data = payload.get("details")
    acceptor = data.get("acceptor")
    
    if acceptor in connections:
        await connections[acceptor].send_json(payload)


manager.add_redis_handler("new_msg", send_message)
