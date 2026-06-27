import json

from fastapi import WebSocketDisconnect
from fastapi.routing import APIRouter
from fastapi.websockets import WebSocket
from fastapi.exceptions import WebSocketException

from app.websocket.handlers import manager

router = APIRouter(prefix="/chat")


@router.websocket("/ws/")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            try:
                data = await ws.receive_text()
                data = json.dumps(await manager.handle(ws, data))
                await ws.send_text(data)
            except WebSocketException as e:
                await ws.send_text(e.reason)
    except WebSocketDisconnect:
        manager.disconnect(ws)
