import dataclasses

from datetime import datetime
from typing import Optional
from configs.loader import _ConfigBase


@dataclasses.dataclass
class Period(_ConfigBase):
    since: Optional[datetime] = None
    until: Optional[datetime] = None

    def isWithin(self, now: datetime) -> bool:
        since_flag = self.since <= now if self.since is not None else True
        until_flag = now <= self.until if self.until is not None else True
        return since_flag and until_flag


@dataclasses.dataclass
class Limitation(_ConfigBase):
    entry: Optional[Period] = None
    attend: Optional[Period] = None
    submit: Optional[Period] = None
    final_submit: Optional[Period] = None
    catalog: Optional[Period] = None


@dataclasses.dataclass
class Schedule(_ConfigBase):
    date: Period = dataclasses.field(default_factory=Period)
    limitation: Limitation = dataclasses.field(default_factory=Limitation)
