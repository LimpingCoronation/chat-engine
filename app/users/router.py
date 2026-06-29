from fastapi.routing import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from app.models.users import User
from app.users.schemes import UserModel
from app.users.dependencies import get_user
from app.core.database.base_repository import get_repository
from app.core.database.setup_db import session_getter
from app.core.safety.hashing import hash_password, verify_password
from app.core.safety.jwt import get_token
from sqlalchemy.exc import IntegrityError

from .schemes import RegistrationUserModel, AuthUserModel

router = APIRouter(prefix="/users")


@router.post("/sign-up/")
async def sign_up(body: RegistrationUserModel, session = Depends(session_getter)):
    users_repo = get_repository(session, User)
    user_data = body.model_dump()
    user_data['password'] = hash_password(body.password)
    try:
        user = await users_repo.create(**user_data)
        await session.commit()
        
        user_pydantic = RegistrationUserModel.model_validate(user)
        return JSONResponse(user_pydantic.model_dump(), status_code=201)
    except IntegrityError as e:
        raise HTTPException(status_code = 400, detail="User with such login already exists")


@router.post('/sign-in/')
async def sign_in(body: AuthUserModel, session = Depends(session_getter)):
    users_repo = get_repository(session, User)
    user = await users_repo.list(login = body.login)
    if len(user) > 0:
        user = user[0]
        if verify_password(body.password, user.password):
            return {
                "token": get_token(str(user.id), user.login)
            }
    
    raise HTTPException(status_code = 400, detail="Wrong login or password")


@router.get('/profile/')
async def get_profile(user = Depends(get_user)) -> UserModel:
    return user


@router.get('/get/{login}')
async def get_user_by_login(login: str, user = Depends(get_user), session = Depends(session_getter)) -> UserModel:
    users_repo = get_repository(session, User)
    user_from_db = await users_repo.get_first(login=login)
    
    if user_from_db:
        return user_from_db
    else:
        raise HTTPException(status_code=404, detail="No such user")
