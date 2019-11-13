

class Definitions:
    """ 定数を定数っぽく扱うためのクラス """

    __kBotCategoryName = "bot"
    __kContactCategoryName = "contact"

    __kBotControlChannelName = "bot-control"
    __kEntryChannelName = "entry"
    __kStatusChannelName = "status"
    __kQueryChannelName = "query"

    __kBotAdminRoleName = "BOT-Admin"
    __kExhibitorRoleName = "Exhibitor"
    __kManagerRoleName = "Manager"

    @classmethod
    @property
    def BOT_CATEGORY_NAME(cls):
        return cls.__kBotCategoryName

    @classmethod
    @property
    def CONTACT_CATEGORY_NAME(cls):
        return cls.__kContactCategoryName

    @classmethod
    @property
    def BOT_CONTROL_CHANNEL_NAME(cls):
        return cls.__kBotControlChannelName

    @classmethod
    @property
    def STATUS_CHANNEL_NAME(cls):
        return cls.__kStatusChannelName

    @classmethod
    @property
    def QUERY_CHANNEL_NAME(cls):
        return cls.__kQueryChannelName

    @classmethod
    @property
    def BOT_ADMIN_ROLE_NAME(cls):
        return cls.__kBotAdminRoleName

    @classmethod
    @property
    def EXHIBITOR_ROLE_NAME(cls):
        return cls.__kExhibitorRoleName

    @classmethod
    @property
    def MANAGER_ROLE_NAME(cls):
        return cls.__kManagerRoleName
