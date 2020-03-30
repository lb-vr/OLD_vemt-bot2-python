from db.database import Database
from configs.event import Event, Owner
from configs.lang import Lang
from configs.question import QuestionItem
from typing import Optional, List
import logging


class QuestionItemDB:
    kTypeId: dict = {
        1: "integer",
        2: "boolean",
        3: "numeric",
        10: "string",
        11: "regex",
        50: "switch",
        100: "picture",
        101: "id-choice",
        102: "json",
        103: "userlist",
        104: "catalog"

    }

    def __init__(self, database: Database):
        self.__database = database
        self.__logger: logging.Logger = logging.getLogger("QuestionItemDB")

    @classmethod
    def nargsStrToListInt(cls, nargs_str: Optional[str]) -> List[int]:
        if nargs_str is None:
            return [1]
        return [int(i) for i in nargs_str.split(",")]

    def __getQuestionItem(self, db_record) -> Optional[QuestionItem]:
        ret = None
        try:
            for qitem in db_record:
                # 選択肢
                db_choices = self.__database.select("question_choices", columns=["itemvalue"],
                                                    condition={"question_item_id": qitem["id"]})
                choices = None
                if len(db_choices) >= 1:
                    choices = []
                    for c in db_choices:
                        choices.append(c["itemvalue"])

                ret = QuestionItem(
                    id=qitem["id"],
                    header=Lang(
                        jp=qitem["header_jp"],
                        en=qitem["header_en"],
                        ko=qitem["header_ko"]
                    ),
                    description=Lang(
                        jp=qitem["detail_jp"],
                        en=qitem["detail_en"],
                        ko=qitem["detail_ko"]
                    ),
                    type=QuestionItemDB.kTypeId[qitem["valid_type"]],
                    nargs=QuestionItemDB.nargsStrToListInt(qitem["nargs_string"]),
                    length=qitem["max_length"],
                    choice=choices,
                    regex_rule=qitem["regex"],
                    limit_phase=qitem["required_when_phase"],
                    allow_multiline=(qitem["allow_multiline"] == 1),
                    key=qitem["key_string"],
                    min=qitem["min_numeric"],
                    max=qitem["max_numeric"]
                )

        except TypeError as e:
            self.__logger.warning("Failed to get prologue. %s", e)
        return ret

    def getQuestionItem(self, id: int, is_request: bool) -> Optional[QuestionItem]:
        db_ret = self.__database.select("question_items",
                                        condition={"id": id, "is_required": 1 if is_request else 0})
        return self.__getQuestionItem(db_ret)

    def clearAllQuestionItems(self):
        self.__database.delete("question_choices")
        self.__database.delete("question_items")

    def setQuestionItem(self, item: QuestionItem, is_request: bool):
        type_int: int = 0
        for k, v in QuestionItemDB.kTypeId.items():
            if item.type == v:
                type_int = k
                break
        else:
            assert True, item.type

        self.__database.insert(
            "question_items",
            {
                "id": item.id,
                "header_jp": item.header.jp,
                "header_en": item.header.en,
                "header_ko": item.header.ko,
                "detail_jp": item.description.jp,
                "detail_en": item.description.en,
                "detail_ko": item.description.ko,
                "valid_type": type_int,
                "regex": item.regex_rule,
                "max_length": item.length,
                "required_when_phase": item.limit_phase,
                "allow_multiline": item.allow_multiline,
                "is_required": 1 if is_request else 0,
                "key_string": item.key,
                "min_numeric": item.min,
                "max_numeric": item.max
            })
        if item.choice:
            for c in item.choice:
                self.__database.insert("question_choices", {"question_item_id": item.id, "itemvalue": c})

    def getAllQuestions(self, is_request: bool) -> List[QuestionItem]:
        ret_db = self.__database.select("question_items", condition={"is_required": 1 if is_request else 0})
        ret: List[QuestionItem] = []
        for rec in ret_db:
            ret.append(self.__getQuestionItem([rec]))
        return ret
