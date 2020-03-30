import datetime
from db.database import Database
from db.registry._registry_base import _RegistryBase


class RegistryServer(_RegistryBase):
    def __init__(self, database: Database):
        super().__init__(database, "registry_datetime")

    def setServerInitializedDatetime(self):
        """ サーバーが初期化された日時を記録する

        値は現在時刻が使用され、サーバーが初期化された証明にすることができる
        """
        self._set("guild.setup", datetime.datetime.now())

    def isInitializedServer(self) -> bool:
        """ サーバーが初期化されているか """
        return self._get("guild.setup") is not None
