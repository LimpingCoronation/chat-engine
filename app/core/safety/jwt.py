import datetime
import jwt

from app.core.config import settings


def get_token(user_id: str, login: str) -> str:
    payload = {
        "id": user_id,
        "login": login,
        "exp": (datetime.datetime.now() + datetime.timedelta(7)).timestamp(),
        "ca": datetime.datetime.now().timestamp()
    }
    encoded = jwt.encode(payload, settings.SALT, "HS256")
    return encoded


def verify_token(token: str):
    try:
        return jwt.decode(token, settings.SALT, algorithms=["HS256"])
    except:
        return None
