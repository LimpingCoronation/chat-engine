import json
from typing import Callable, Any, Awaitable

from fastapi import WebSocket
from fastapi.exceptions import WebSocketException

from app.models.users import User
from app.core.config import logger
from app.core.database.setup_db import get_session


class WebSocketManager:
    def __init__(self):
        self.connections: dict[WebSocket, User] = {}
        self.user_to_con: dict[str, WebSocket] = {}
        self.handlers: dict[str, Callable[[dict], Any]] = {}
        self.redis_handlers: dict[str, Callable[[dict], Any]] = {}

    def add_handler(self,  key: str, func: Callable[[WebSocket, dict[str, Any], dict[WebSocket, User]], Awaitable[Any]]):
        self.handlers[key] = func
    
    def add_redis_handler(self, key: str, func: Callable[[dict[str, Any], dict[str, WebSocket]], Awaitable[Any]]):
        self.redis_handlers[key] = func
    
    def authorize(self, ws: WebSocket, user: User):
        self.connections[ws] = user
        self.user_to_con[str(user.id)] = ws

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.user_to_con.pop(str(self.connections[ws].id))
            del self.connections[ws]

    async def handle(self, ws: WebSocket, response: dict[str, Any]) -> dict[str, Any]:
        logger.info("New message accepted: " + json.dumps(response))

        msg_type = response.get("type")

        try:
            session = await get_session()
            if msg_type is not None:
                func = self.handlers.get(msg_type)
                if func is not None:
                    return await func(ws, response, self.connections, session)
        finally:
            await session.close()

        raise WebSocketException(1001, "Wrong msg type")
    
    async def notify(self, payload: dict[str, Any]):
        msg_type = payload.get("type")

        if msg_type is not None:
            func = self.redis_handlers.get(msg_type)
            if func is not None:
                return await func(payload, self.user_to_con)
