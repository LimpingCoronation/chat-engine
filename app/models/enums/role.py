from enum import Enum


class Role(str, Enum):
    USER = "user"
    READ_ONLY_USER = "read_only_user"
    ADMIN = "admin"
