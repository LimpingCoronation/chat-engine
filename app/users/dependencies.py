from typing import Annotated
import uuid

from fastapi import Header, Depends
from fastapi.exceptions import HTTPException

from app.core.safety.jwt import verify_token
from app.core.database.setup_db import session_getter
from app.core.database.base_repository import get_repository
from app.models.users import User


async def get_user(token: Annotated[str, Header()], session = Depends(session_getter)):
    payload = verify_token(token)
    if payload is not None:
        users_repo = get_repository(session, User)
        users = await users_repo.list(**{"id": uuid.UUID(payload["id"])})

        if len(users) > 0:
            return users[0]
    
    raise HTTPException(status_code=403, detail="Not authorized")
