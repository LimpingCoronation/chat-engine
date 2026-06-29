import json
from typing import Any

import redis.asyncio as redis

from app.core.config import logger, settings
from app.websocket.websocket_manager import WebSocketManager
from app.websocket.state import manager


class RedisManager:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = RedisManager(settings.REDIS_HOST, settings.REDIS_PORT, settings.CHANNEL_NAME, manager)
        return cls._instance
    
    def __init__(self, host, port, channel_name, websocket_manager: WebSocketManager):
        self.host = host
        self.port = port
        self.channel_name = channel_name
        self.websocket_manager = websocket_manager
        
        self.client = redis.Redis(host=self.host, port=self.port, decode_responses=True)

    async def notify(self, payload: dict[str, Any]):
        await self.client.publish(
            self.channel_name, json.dumps(payload)
        )
    
    async def close(self):
        await self.client.close()
    
    async def handle(self):
        pubsub = self.client.pubsub()
        await pubsub.subscribe(self.channel_name)
        
        logger.info("Created redis subscriber")
        
        try:
            async for message in pubsub.listen():
                try:
                    data = json.loads(message['data'])
                    logger.info(f"Redis subscriber has accepted message: {data}")
                    await self.websocket_manager.notify(data)
                except TypeError as e:
                    logger.warning(e)
        finally:
            await pubsub.unsubscribe(self.channel_name)
            await self.client.close()
