from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI

from app.core.config import DEV_MODE, logger
from app.users.router import router as user_router
from app.websocket.router import router as ws_router
from app.websocket.redis_manager import RedisManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server started")
    manager = RedisManager.get_instance()
    asyncio.create_task(manager.handle())
    yield
    
    await manager.close()
    

app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(ws_router)

@app.get("/root")
def root():
    return {"message": f"DEV_MODE is {DEV_MODE}"}
