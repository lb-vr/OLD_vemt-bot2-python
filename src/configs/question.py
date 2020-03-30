import dataclasses

from typing import Optional, List
from configs.lang import Lang
from configs.loader import _ConfigBase


@dataclasses.dataclass
class QuestionItem(_ConfigBase):
    header: Lang
    description: Lang
    type: str
    id: Optional[int] = None
    nargs: Optional[List[int]] = None
    length: int = 256
    choice: Optional[List[str]] = None
    regex_rule: str = ".+"
    limit_phase: Optional[str] = None
    allow_multiline: bool = False
    key: Optional[str] = None
    min: Optional[int] = None
    max: Optional[int] = None
    _conditions: dataclasses.Field = dataclasses.field(init=False)

    def __post_init__(self):
        # エラーチェック
        if self.type not in [
            "string", "id-choice", "integer", "switch",
                "userlist", "picture", "regex", "catalog"]:
            raise ValueError("illegal type: {}".format(self.type))

        if self.type == "switch" and self.key is None:
            raise ValueError("key is required when type is switch.")

        if self.type == "id-choice" and not self.choice:
            raise ValueError("choice is required when type is id-choice.")

        # 初期化補助
        if self.type == "integer":
            if self.min is None:
                self.min = -10000000
            if self.max is None:
                self.max = 10000000

        if self.nargs is None:
            self.nargs = [1]

        # 条件
        self._conditions = {}
        for k, v in self._optionals.items():
            if type(v) is bool:
                self._conditions[k] = v


@dataclasses.dataclass
class Question(_ConfigBase):
    prologue: Lang
    require: List[QuestionItem]
    optional: List[QuestionItem]
