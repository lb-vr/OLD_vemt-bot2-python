import dataclasses
from typing import List
from configs.loader import _ConfigBase


@dataclasses.dataclass
class Submit(_ConfigBase):
    upload_url: str
    download_url: str
    unitypackage_rule: str
