from typing import Tuple


class Definitions:
    """ 定数を定数っぽく扱うためのクラス """

    __kBotCategoryName: str = "bot"
    __kContactCategoryName: str = "contact"

    __kBotControlChannelName: str = "bot-control"
    __kEntryChannelName: str = "entry"
    __kStatusChannelName: str = "status"
    __kQueryChannelName: str = "query"

    __kBotAdminRoleName: str = "BOT-Admin"
    __kExhibitorRoleName: str = "Exhibitor"
    __kManagerRoleName: str = "Manager"

    @classmethod
    def getGuildIdKey(cls) -> str:
        return "guild.id"

    @classmethod
    def getBotCategoryName(cls) -> str:
        return cls.__kBotCategoryName

    @classmethod
    def getBotCategoryKey(cls) -> str:
        return "category." + cls.getBotCategoryName()

    @classmethod
    def getContactCategoryName(cls) -> str:
        return cls.__kContactCategoryName

    @classmethod
    def getContactCategoryKey(cls) -> str:
        return "category." + cls.getContactCategoryName()

    @classmethod
    def getBotControlChannelName(cls) -> str:
        return cls.__kBotControlChannelName

    @classmethod
    def getBotControlChannelKey(cls) -> str:
        return "channel." + cls.getBotControlChannelName()

    @classmethod
    def getEntryChannelName(cls) -> str:
        return cls.__kEntryChannelName

    @classmethod
    def getEntryChannelKey(cls) -> str:
        return "channel." + cls.getEntryChannelName()

    @classmethod
    def getStatusChannelName(cls) -> str:
        return cls.__kStatusChannelName

    @classmethod
    def getStatusChannelKey(cls) -> str:
        return "channel." + cls.getStatusChannelName()

    @classmethod
    def getQueryChannelName(cls) -> str:
        return cls.__kQueryChannelName

    @classmethod
    def getQueryChannelKey(cls) -> str:
        return "channel." + cls.getQueryChannelName()

    @classmethod
    def getBotAdminRoleName(cls) -> str:
        return cls.__kBotAdminRoleName

    @classmethod
    def getBotAdminRoleKey(cls) -> str:
        return "channel." + cls.getBotAdminRoleName()

    @classmethod
    def getExhibitorRoleName(cls) -> str:
        return cls.__kExhibitorRoleName

    @classmethod
    def getExhibitorRoleKey(cls) -> str:
        return "role." + cls.getExhibitorRoleName()

    @classmethod
    def getManagerRoleName(cls) -> str:
        return cls.__kManagerRoleName

    @classmethod
    def getManagerRoleKey(cls) -> str:
        return "role." + cls.getManagerRoleName()

    @classmethod
    def getAllChannels(cls) -> Tuple[str]:
        return (
            cls.getBotCategoryName(),
            cls.getContactCategoryName(),
            cls.getBotControlChannelName(),
            cls.getEntryChannelName(),
            cls.getStatusChannelName(),
            cls.getQueryChannelName()
        )

    @classmethod
    def getAllRoles(cls) -> Tuple[str]:
        return (
            cls.getBotAdminRoleName(),
            cls.getExhibitorRoleName(),
            cls.getManagerRoleName()
        )
