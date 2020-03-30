from db.database import Database
from configs.event import Event, Owner
from configs.lang import Lang
from typing import Optional
import logging


class PrologueDB:
    def __init__(self, database: Database):
        self.__database = database
        self.__logger: logging.Logger = logging.getLogger("PrologueDB")

    def _get(self, key: str) -> Optional[str]:
        ret = self.__database.select("registry_string", ["itemvalue"], {"title": key})
        if len(ret) == 1:
            ret = ret[0]["itemvalue"]
        else:
            ret = None
        return ret

    def getPrologue(self) -> Optional[Lang]:
        ret: Optional[Lang] = None
        try:
            ret = Lang(
                jp=self._get("question.prologue.jp"),
                en=self._get("question.prologue.en"),
                ko=self._get("question.prologue.ko")
            )
        except TypeError as e:
            self.__logger.warning("Failed to get prologue. %s", e)
        return ret

    def setPrologue(self, prologue: Lang):
        self.__database.insertOrReplace("registry_string", {"title": "question.prologue.jp", "itemvalue": prologue.jp})
        self.__database.insertOrReplace("registry_string", {"title": "question.prologue.en", "itemvalue": prologue.en})
        self.__database.insertOrReplace("registry_string", {"title": "question.prologue.ko", "itemvalue": prologue.ko})
