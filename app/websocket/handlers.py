import uuid

from fastapi import WebSocket
from fastapi.exceptions import WebSocketException

from app.websocket.websocket_manager import WebSocketManager
from app.core.database.base_repository import get_repository
from app.core.database.setup_db import get_session
from app.core.safety.jwt import verify_token
from app.models.users import User
from app.models.chat import Chat
from app.models.chat_member import ChatMember
from app.models.message import Message
from app.core.config import logger

manager = WebSocketManager()


async def get_user(
        ws: WebSocket, 
        payload: dict, 
        connections: dict, 
        use_db: bool = False,
        raise_exceptions: bool = True
) -> User:
    token = payload.get('token')
    if token is None:
        raise WebSocketException(code=1002, reason="Token not specified")
    
    if connections.get(ws) is not None:
        return connections.get(ws)

    if use_db:
        payload = verify_token(token)
        if payload is not None:
            users_repo = get_repository(await get_session(), User)
            users = await users_repo.get_first(**{"id": uuid.UUID(payload["id"])})

            if users is not None:
                return users
    
    if raise_exceptions:
        raise WebSocketException(code=1001, reason="Wrong token")


async def notify(chat: Chat, session):
    chat_member_repo = get_repository(await get_session(), ChatMember)
    memebers = chat_member_repo.list(chat_id = chat.id)

    for m in memebers:
        # TODO: notify member through redis
        pass


async def ping(ws: WebSocket, payload: dict, connections: dict):
    return {
        "details": "pong"
    }


async def auth(ws: WebSocket, payload: dict, connections: dict) -> dict:
    user = await get_user(ws, payload, connections, True)
    manager.authorize(ws, user)

    logger.info(f"{user.login} authorized")

    return {
        "status": "ok",
        "details": {
            "id": str(user.id),
            "login": user.login
        }
    }


async def check_auth(ws: WebSocket, payload: dict, connections: dict):
    user = await get_user(ws, payload, connections, False, False)

    if user is None:
        raise WebSocketException(code=1002, reason="Not authorized")

    return {
        "status": "ok",
        "details": {
            "id": str(user.id),
            "login": user.login
        }
    }


async def message(ws: WebSocket, payload: dict, connections: dict):
    user = await get_user(ws, payload, connections)
    chat_id = payload.get("chat_id")
    text = payload.get("text")
    contact_id = payload.get("contact_id")

    if not text:
        raise WebSocketException(code=1007, reason="Wrong data")
    
    chat_repo = get_repository(await get_session(), Chat)
    chat_member_repo = get_repository(await get_session(), ChatMember)
    message_repo = get_repository(await get_session(), Message)
    chat = None
    
    if chat_id is not None:
        chat = await chat_repo.get_first(id = uuid.UUID(chat_id))
        member = await chat_member_repo.get_first(
            user_id = uuid.UUID(user.id),
            chat_id = uuid.UUID(chat.id)
        )

        if member is not None:
            message_repo.create(
                text = text,
                user_id = uuid.UUID(user.id),
                chat_id = uuid.UUID(chat.id)
            )
        
        return {
            "status": "ok",
        }
    elif contact_id is not None:
        chat: Chat = chat_repo.get_first(common_id = str(user.id) + contact_id)
        if chat is None:
            chat = chat_repo.create(
                common_id = str(user.id) + contact_id,
                title = "Private chat"
            )
        
        message_repo.create(
            text = text,
            user_id = uuid.UUID(user.id),
            chat_id = chat.id
        )

    if chat is None:
        raise WebSocketException(code=1007, reason="Chat is not selected")
    else:
        await notify(chat, await get_session())


manager.add_handler("auth", auth)
manager.add_handler("ping", ping)
manager.add_handler("check_auth", check_auth)
manager.add_handler("message", message)
