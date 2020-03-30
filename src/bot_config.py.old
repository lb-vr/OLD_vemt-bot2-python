import json
import os
from typing import Optional, Any


class Config:

    def __init__(self, cfg_fname: str):
        self.__cfg = {}
        self.__cfg_fname = cfg_fname
        with open(cfg_fname, mode="r", encoding="utf-8") as f:
            self.__cfg = json.load(f)

    def getVal(self, key: str, defval: Optional[Any] = None, type_: Optional[type] = None):
        assert type(key) is str, "key must be string."

        if key in self.__cfg:
            if type_ is None:
                return self.__cfg[key]
            elif type(self.__cfg[key]) is type_:
                return self.__cfg[key]
        return defval

    def setVal(self, key: str, value, save: bool = True):
        assert type(key) is str, "key must be string."

        self.__cfg[key] = value
        if save:
            self.save()

    def save(self):
        with open(self.__cfg_fname, mode="w", encoding="utf-8") as f:
            json.dump(self.__cfg, f)

    @classmethod
    def getConfig(cls, guild_id):
        # ファイル名
        config_fname = "cfg_" + str(guild_id) + ".json"
        if not os.path.exists(config_fname):
            with open(config_fname, mode="w", encoding="utf-8") as f:
                f.write(r"{}")

        return Config(config_fname)

    @classmethod
    def remove(cls, guild_id):
        # ファイル名
        config_fname = "cfg_" + str(guild_id) + ".json"
        if os.path.exists(config_fname):
            os.remove(config_fname)
