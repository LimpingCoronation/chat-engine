import json
from typing import Callable, Any, Awaitable
from functools import wraps

from fastapi import WebSocket
from fastapi.exceptions import WebSocketException

from app.models.users import User
from app.core.config import logger


class WebSocketManager:
    def __init__(self):
        self.connections: dict[WebSocket, User] = {}
        self.user_to_con: dict[str, WebSocket] = {}
        self.handlers: dict[str, Callable[[dict], Any]] = {}

    def add_handler(self,  key: str, func: Callable[[WebSocket, dict[str, Any], dict[WebSocket, User]], Awaitable[Any]]):
        self.handlers[key] = func
    
    def authorize(self, ws: WebSocket, user: User):
        self.connections[ws] = user
        self.user_to_con[str(user.id)] = ws

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            del self.connections[ws]

    async def handle(self, ws: WebSocket, response: str) -> dict:
        logger.info("New message accepted: " + response)

        data = json.loads(response)
        msg_type = data.get("type")

        if msg_type is not None:
            func = self.handlers.get(msg_type)
            if func is not None:
                return await func(ws, data, self.connections)

        raise WebSocketException(1001, "Wrong msg type")  
