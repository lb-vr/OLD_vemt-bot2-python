from typing import List
import enum


class CategoryName(enum.Enum):
    kBot: str = "bot"
    kContact: str = "contact"

    @classmethod
    def getAll(cls) -> List[str]:
        return [item.value for item in cls.__members__.values()]


class ChannelName(enum.Enum):
    kBotControl: str = "bot-control"
    kEntry: str = "entry"
    kStatus: str = "status"
    kQuery: str = "query"

    @classmethod
    def getAll(cls) -> List[str]:
        return [item.value for item in cls.__members__.values()]


class RoleName(enum.Enum):
    kBotAdmin: str = "BOT-Admin"
    kExhibitor: str = "Exhibitor"
    kManager: str = "Manager"

    @classmethod
    def getAll(cls) -> List[str]:
        return [item.value for item in cls.__members__.values()]
