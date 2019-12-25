import dataclasses
import re
from datetime import datetime
from typing import List, Optional


@dataclasses.dataclass(frozen=True)
class QuestionItem:
    text: str
    description: str = ""
    answer_type: str = "string"
    length: int = 1024
    is_required: bool = False
    choice: Optional[list] = None
    limit_phase: Optional[str] = None
    limit_datetime: Optional[datetime] = None

    def getAnswerTypeDisp(self) -> str:
        if self.answer_type == "string":
            return "文字列"

        if self.answer_type == "number":
            return "数字"

        if self.answer_type == "picture":
            return "画像データ"

        if self.answer_type == "regex":
            return "形式文字列"

        if self.answer_type == "json":
            return "JSON文字列"
        return "エラー"

    def getText(self, index: int) -> str:
        ret: str = "**Q{index}. ".format(index=index)
        if self.is_required:
            ret += "【必須】 "
        ret += "{text}**\n".format(text=self.text)
        if self.description:
            ret += self.description + "\n"
        if self.choice:
            ret += "選択肢：["
            first: bool = True
            for c in self.choice:
                if not first:
                    ret += " | "
                first = False
                ret += c
            ret += "]\n"

        ret += "< {0} | 回答・編集期限：".format(self.getAnswerTypeDisp())
        if self.limit_datetime is not None:
            ret += "{0:%Y/%m/%d %H:%M:%S}".format(self.limit_datetime)
            if self.limit_phase is not None:
                ret += " もしくは "
        if self.limit_phase is not None:
            # TODO 表示用のphaseに変換
            ret += "{0}まで".format(self.limit_phase)
        if self.limit_datetime is None and self.limit_phase is None:
            ret += "なし"
        ret += " >\n"

        ret += ">> （未回答）"
        return ret


@dataclasses.dataclass(frozen=True)
class Question:
    author: str
    title: str
    description: str = ""
    items: List[QuestionItem] = []

    def getHeaderText(self) -> str:
        return "**{0.title}**\n{0.description}"

    def getQuestionText(self) -> List[str]:
        ret: List[str] = []
        for index in range(len(self.items)):
            ret.append(self.items[index].getText(index))
        return ret

    @classmethod
    def __check_str(cls, value, allow_blank: bool = False):
        if type(value) is str:
            raise ValueError("{} is not str.".format(value))
        if not allow_blank and value == "":
            raise ValueError("{} is invalid.".format(value))
        return value

    @classmethod
    def loadFromJson(cls, jdict: dict):
        """
        発生しうる例外をキャッチしない
        """
        author: str = cls.__check_str(jdict["author"])
        title: str = cls.__check_str(jdict["title"])
        description: str = ""
        if "descriptions" in jdict:
            description = "\\n".join(jdict["descriptions"])

        question_items: List[QuestionItem] = []
        if "items" in jdict:
            for itm in jdict["items"]:
                text = itm["text"]

                answer_type: str = "string"
                if "type" in itm:
                    if itm["type"] in ["string", "number", "picture", "regex", "json"]:
                        answer_type = itm["type"]
                    else:
                        raise ValueError("invalid answer_type")

                length: int = 200
                if "length" in itm:
                    length = int(itm(length))
                    if not (0 < length and length <= 200):
                        raise ValueError("length value is out of bounds")

                choice: Optional[list] = None
                if "choice" in itm:
                    if type(itm["choice"]) is list:
                        if len(itm["choice"]) > 1:
                            choice = []
                            for c in itm["choice"]:
                                if type(c) is str:
                                    choice.append(c)

                is_required: bool = False
                if "is_required" in itm:
                    is_required = bool(itm["is_required"])

                regex_rule: str = ".+"
                if "regex_rule" in itm:
                    regex_rule = itm["regex_rule"]
                    re.compile(regex_rule)

                limit_phase: Optional[str] = None
                if "limit_phase" in itm:
                    if itm["limit_phase"] in ["entry", "submit", "publish"]:
                        limit_phase = cls.__check_str(itm["limit_phase"])
                    else:
                        raise ValueError("Invalid phase")

                limit_datetime: Optional[datetime] = None
                if "limit_datetime" in itm:
                    limit_datetime = datetime.strptime(itm["limit_datetime"], "%Y/%m/%d %H:%M:%S")

                question_items.append(QuestionItem(
                    text=text,
                    answer_type=answer_type,
                    length=length,
                    is_required=is_required,
                    choice=choice,
                    limit_phase=limit_phase,
                    limit_datetime=limit_datetime,
                ))

        return Question(
            author=author,
            title=title,
            description=description,
            items=question_items
        )
