from contextlib import contextmanager

from fastapi import FastAPI

from app.core.config import DEV_MODE, logger
from app.users.router import router as user_router
from app.websocket.router import router as ws_router


@contextmanager
async def lifespan(app: FastAPI):
    # startup'
    logger.info("Server started")
    yield
    # shutdown

app = FastAPI()
app.include_router(user_router)
app.include_router(ws_router)

@app.get("/root")
def root():
    return {"message": f"DEV_MODE is {DEV_MODE}"}
