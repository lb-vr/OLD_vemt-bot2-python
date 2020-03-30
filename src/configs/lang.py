from typing import Optional, Union, List
import dataclasses
from configs.loader import _ConfigBase


@dataclasses.dataclass
class Lang(_ConfigBase):
    jp: Union[str, List[str]]
    en: Optional[Union[str, List[str]]] = None
    ko: Optional[Union[str, List[str]]] = None

    def __post_init__(self):
        if type(self.jp) is list:
            self.jp = "\n".join(self.jp)
        if type(self.en) is list:
            self.en = "\n".join(self.en)
        if type(self.ko) is list:
            self.ko = "\n".join(self.ko)
