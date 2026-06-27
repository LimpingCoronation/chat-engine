from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

from app.core.config import settings

ph = PasswordHasher()


def hash_password(password: str):
    return ph.hash(password + settings.SALT)


def verify_password(password: str, hash: str):
    try:
        return ph.verify(hash, password + settings.SALT)
    except VerificationError:
        return False
