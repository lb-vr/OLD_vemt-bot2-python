from db.database import Database
from typing import Optional, Any
import logging


class _RegistryBase:
    def __init__(self, database: Database, table: str):
        assert type(database) is Database
        assert type(table) is str
        self.__database: Database = database
        self.__table: str = table
        self.__logger: logging.Logger = logging.getLogger(self.__class__.__name__)

    @property
    def logger(self) -> logging.Logger:
        return self.__logger

    def _get(self, key: str, table: Optional[str] = None) -> Any:
        assert type(key) is str
        target_table: str = self.__table
        if table is not None and type(table) is str:
            target_table = table

        ret = self.__database.select(target_table, ["itemvalue"], {"title": key})
        if len(ret) == 1:
            ret = ret[0]["itemvalue"]
        else:
            ret = None
        return ret

    def _set(self, key: str, value: Any, table: Optional[str] = None, allow_insert: bool = True):
        assert type(key) is str
        target_table: str = self.__table
        if table is not None and type(table) is str:
            target_table = table

        if allow_insert:
            self.__database.insertOrReplace(target_table, {"itemvalue": value, "title": key})
        else:
            self.__database.update(target_table, {"itemvalue": value}, {"title": key})
