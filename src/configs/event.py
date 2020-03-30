from configs.lang import Lang
import dataclasses
from typing import Optional
from configs.loader import _ConfigBase


@dataclasses.dataclass
class Owner(_ConfigBase):
    name: str
    discord: Optional[str] = None


@dataclasses.dataclass
class Event(_ConfigBase):
    owner: Owner
    website: str
    title: Lang
    description: Lang
