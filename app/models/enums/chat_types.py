from enum import Enum


class ChatTypes(str, Enum):
    CHAT = "chat"
    GROUP = "group"
    CHANNEL = "channel"
