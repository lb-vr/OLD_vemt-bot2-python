import dataclasses
import sqlite3
import logging
import datetime

from typing import Optional, Dict, Any, List
from db.database import Database, DatabaseError

from phase import Phase


@dataclasses.dataclass
class EntryInfo:
    id: int
    discord_user_id: int
    contact_channel_id: int
    current_phase_id: dataclasses.InitVar[int]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    current_phase: Phase = dataclasses.field(init=False)

    def __post_init__(self, current_phase_id: int):
        assert type(current_phase_id) is int
        self.current_phase = Phase.getFromInt(current_phase_id)


class Entries:
    def __init__(self, database: Database):
        assert type(database) is Database
        self.__database = database

    def getEntryInfoFromDiscordID(self, id: int) -> Optional[EntryInfo]:
        ret = self.__database.select("entries", condition={"discord_user_id": id})
        assert len(ret) <= 1
        return EntryInfo(**dict(ret[0])) if len(ret) == 1 else None

    def addNewUser(self, discord_user_id: int, channel_id: int) -> Optional[EntryInfo]:
        self.__database.insert("entries", {
            "discord_user_id": discord_user_id,
            "contact_channel_id": channel_id})

        return self.getEntryInfoFromDiscordID(discord_user_id)
