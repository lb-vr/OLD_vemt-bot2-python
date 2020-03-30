from db.registry._registry_base import _RegistryBase
from db.database import Database
from typing import Optional


class RegistryGuild(_RegistryBase):
    def __init__(self, database: Database):
        super().__init__(database, "registry_int")

    def getCategoryBotId(self) -> Optional[int]:
        return self._get("id.category.bot")

    def setCategoryBotId(self, id: int):
        self._set("id.category.bot", id)

    def getCategoryContactId(self) -> Optional[int]:
        return self._get("id.category.contact")

    def setCategoryContactId(self, id: int):
        self._set("id.category.contact", id)

    def getChannelBotControlId(self) -> Optional[int]:
        return self._get("id.channel.bot-control")

    def setChannelBotControlId(self, id: int):
        self._set("id.channel.bot-control", id)

    def getChannelEntryId(self) -> Optional[int]:
        return self._get("id.channel.entry")

    def setChannelEntryId(self, id: int):
        self._set("id.channel.entry", id)

    def getChannelStatusId(self) -> Optional[int]:
        return self._get("id.channel.status")

    def setChannelStatusId(self, id: int):
        self._set("id.channel.status", id)

    def getChannelQueryId(self) -> Optional[int]:
        return self._get("id.channel.query")

    def setChannelQueryId(self, id: int):
        self._set("id.channel.query", id)

    def getRoleBotAdminId(self) -> Optional[int]:
        return self._get("id.role.bot-admin")

    def setRoleBotAdminId(self, id: int):
        self._set("id.role.bot-admin", id)

    def getRoleExhibitorId(self) -> Optional[int]:
        return self._get("id.role.exhibitor")

    def setRoleExhibitorId(self, id: int):
        self._set("id.role.exhibitor", id)

    def getRoleManagerId(self) -> Optional[int]:
        return self._get("id.role.manager")

    def setRoleManagerId(self, id: int):
        self._set("id.role.manager", id)
