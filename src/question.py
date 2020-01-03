import dataclasses
import re
from datetime import datetime
from typing import List, Optional
import logging


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
            return "正規表現で制限された文字列"

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

        ret += "[ {0} | 回答・編集期限：".format(self.getAnswerTypeDisp())
        if self.limit_datetime is not None:
            ret += "{0:%Y/%m/%d %H:%M:%S}".format(self.limit_datetime)
            if self.limit_phase is not None:
                ret += " もしくは "
        if self.limit_phase is not None:
            # TODO 表示用のphaseに変換
            ret += "{0}まで".format(self.limit_phase)
        if self.limit_datetime is None and self.limit_phase is None:
            ret += "なし"
        ret += " ]\n"

        ret += ">>\n>> （未回答）\n>>"
        return ret


@dataclasses.dataclass(frozen=True)
class Question:
    author: str
    title: str
    description: str
    items: List[QuestionItem]

    def getHeaderText(self) -> str:
        return "**{0.title}**\n{0.description}".format(self)

    def getQuestionText(self) -> List[str]:
        ret: List[str] = []
        for index in range(len(self.items)):
            ret.append(self.items[index].getText(index + 1))
        return ret

    def resetDatabase(self):
        pass

    @classmethod
    def __check_str(cls, value, allow_blank: bool = False):
        if type(value) is not str:
            raise ValueError("{} is not str.".format(value))
        if not allow_blank and value == "":
            raise ValueError("{} is invalid.".format(value))
        return value

    @classmethod
    def loadFromJson(cls, jdict: dict):
        """
        発生しうる例外をキャッチしない
        """
        logger = logging.getLogger("QuestionItem")
        logger.debug("Parsing Question")

        author: str = cls.__check_str(jdict["author"])
        logger.debug("- author: %s", author)

        title: str = cls.__check_str(jdict["title"])
        logger.debug("- title : %s", title)

        description: str = ""
        if "description" in jdict:
            if type(jdict["description"]) is list:
                description = "\n".join(jdict["description"])
            elif type(jdict["description"]) is str:
                description = jdict["description"]
        logger.debug("- description : %s", description)

        logger.debug("- Parsing QuestionItems.")

        question_items: List[QuestionItem] = []
        if "items" in jdict:
            for itm in jdict["items"]:
                logger.debug("- :: Item ::")

                text = itm["text"]
                logger.debug("-- text  : %s", text)

                description_item: str = ""
                if "description" in itm:
                    if type(itm["description"]) is list:
                        description_item = "\n".join(itm["description"])
                    elif type(itm["description"]) is str:
                        description_item = itm["description"]
                logger.debug("-- description: %s", description_item)

                answer_type: str = "string"
                if "type" in itm:
                    if itm["type"] in ["string", "number", "picture", "regex", "json"]:
                        answer_type = itm["type"]
                    else:
                        raise ValueError("invalid answer_type")
                logger.debug("-- type  : %s", answer_type)

                length: int = 200
                if "length" in itm:
                    length = int(itm["length"])
                    if length <= 0 or 256 < length:
                        raise ValueError("length value is out of bounds")
                logger.debug("-- length: %d", length)

                choice: Optional[list] = None
                if "choice" in itm:
                    if type(itm["choice"]) is list:
                        if len(itm["choice"]) > 1:
                            choice = []
                            for c in itm["choice"]:
                                if type(c) is str:
                                    choice.append(c)
                logger.debug("-- choice: %s", choice)

                is_required: bool = False
                if "is_required" in itm:
                    is_required = bool(itm["is_required"])
                logger.debug("-- is_required: %s", is_required)

                regex_rule: str = ".+"
                if "regex_rule" in itm:
                    regex_rule = itm["regex_rule"]
                    re.compile(regex_rule)
                logger.debug("-- regex_rule: %s", regex_rule)

                limit_phase: Optional[str] = None
                if "limit_phase" in itm:
                    if itm["limit_phase"] in ["entry", "submit", "publish"]:
                        limit_phase = cls.__check_str(itm["limit_phase"])
                    else:
                        raise ValueError("Invalid phase")
                logger.debug("-- limit_phase: %s", limit_phase)

                limit_datetime: Optional[datetime] = None
                if "limit_datetime" in itm:
                    limit_datetime = datetime.strptime(itm["limit_datetime"], "%Y-%m-%d %H:%M:%S")
                logger.debug("-- limit_datetime: %s",
                             limit_datetime.strftime("%Y-%m-%d %H:%M:%S") if limit_datetime else "None")

                question_items.append(QuestionItem(
                    text=text,
                    description=description_item,
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
