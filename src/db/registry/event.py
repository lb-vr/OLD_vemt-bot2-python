from db.database import Database
from db.registry._registry_base import _RegistryBase
from configs.event import Event, Owner
from configs.lang import Lang
from typing import Optional


class RegistryEvent(_RegistryBase):
    def __init__(self, database: Database):
        super().__init__(database, "registry_string")

    def getEvent(self) -> Optional[Event]:
        ret: Optional[Event] = None
        try:
            ret = Event(
                owner=Owner(
                    name=self._get("event.owner.name"),
                    discord=self._get("event.owner.discord")
                ),
                website=self._get("event.website"),
                title=Lang(
                    jp=self._get("event.title.jp"),
                    en=self._get("event.title.en"),
                    ko=self._get("event.title.ko")
                ),
                description=Lang(
                    jp=self._get("event.description.jp"),
                    en=self._get("event.description.en"),
                    ko=self._get("event.description.ko")
                )
            )
            self.logger.debug("Fetch Event from database. %s", ret)

        except TypeError as e:
            self.logger.warning("Failed to create Event instance. %s", e)

        return ret

    def setEvent(self, event: Event):
        self._set("event.owner.name", event.owner.name)
        self._set("event.owner.discord", event.owner.discord)
        self._set("event.website", event.website)
        self._set("event.title.jp", event.title.jp)
        self._set("event.title.en", event.title.en)
        self._set("event.title.ko", event.title.ko)
        self._set("event.description.jp", event.description.jp)
        self._set("event.description.en", event.description.en)
        self._set("event.description.ko", event.description.ko)
        self.logger.debug("Update Event data.")
