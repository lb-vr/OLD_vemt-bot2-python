import discord
import argparse
import logging
import json

from typing import NoReturn, List, Tuple, Optional, Dict

from .const import Definitions
from ..bot_config import Config
from ..client import VemtClient

from .processor_base import ProcessorBase, ProcessorError, AuthenticationError, MyArgumentParser


class ConfigProcess(ProcessorBase):
    __logger = logging.getLogger("ConfigProcess")

    parser = None

    @classmethod
    def setupSubCommand(cls, subparser: argparse._SubParsersAction) -> NoReturn:
        cls.parser = subparser.add_parser("+config", help="BOTの設定を変更します")
        cls.parser.set_defaults(handler=ConfigProcess)
        subp = cls.parser.add_subparsers(parser_class=MyArgumentParser)

        # -- questionのsubparser
        parser_question = subp.add_parser("question", help="質問関連の設定")
        subp_question = parser_question.add_subparsers(parser_class=MyArgumentParser)

        # +config question upload
        parser_question_upload = subp_question.add_parser("upload", help="jsonファイルから質問を設定します")
        parser_question_upload.add_argument("--preview", action="store_true", help="質問を更新しませんが、最終的な見た目を確認することができます")
        parser_question_upload.set_defaults(proc=cls.uploadQuestion)

        # +config question add
        parser_question_add = subp_question.add_parser("add",
                                                       help="任意回答の質問を末尾に追加します",
                                                       description="新しい質問を、既存の質問の末尾に追加します。\n追加できる質問はすべて**任意回答**となります。")
        parser_question_add.add_argument("text", type=str, help="簡潔な質問文")
        parser_question_add.add_argument("--details", nargs="+", type=str, help="質問文の補足などを行います。行ごとに空白で区切ってください。")
        parser_question_add.add_argument("--type", type=str, default="string", choices=["string", "number", "picture", "regex", "json"], help="期待する回答の種類を指定します")
        parser_question_add.add_argument("--choise", type=str, nargs="+", default=[], help="回答を選択式にします")
        parser_question_add.add_argument("--length", type=int, default=200, help="回答の最大文字数を入力します")
        parser_question_add.add_argument("--regex_rule", type=str, default=".+", help="回答を受理する正規表現を指定します")
        parser_question_add.set_defaults(proc=cls.addOptionalQuestion)

    @classmethod
    async def authenticate(cls, args, client: discord.Client, message: discord.Message) -> NoReturn:
        # Guildオーナーのみ
        if message.guild.owner.id != message.author.id:
            raise AuthenticationError("+init command is permitted for guild owner.")

    @classmethod
    async def uploadQuestion(cls, args, client: discord.Client, message: discord.Message) -> NoReturn:
        cls.__logger.debug("start to upload Question.")
        if len(message.attachments) != 1:
            raise ProcessorError("jsonファイルが添付されていないか、複数添付されています")

        error_msgs: List[str] = []
        question_header: Dict[str] = {}
        try:
            json_bytes = await message.attachments[0].read()
            json_str = json_bytes.decode("utf-8")
            cls.__logger.debug("- json length: %d", len(json_str))
            json_obj = json.loads(json_str)
            cls.__logger.debug("- json parsed.")

            question, errors = cls.parseQuestionJson(json_obj)

            # ロギング
            cls.__logger.debug("- loaded json.")

            if len(errors) > 0:
                error_msg = "\n".join(errors)
                raise ProcessorError("質問設定にエラーがありました。以下はエラーの詳細です。\n" + error_msg)

            cls.__logger.debug("- parsed json successfully.")

            if not args.preview:
                # Databaseに登録
                cls.__logger.debug("- add database.")
                # TODO

            # プレビューデータを表示

            print(question)

        except UnicodeDecodeError as e:
            raise ProcessorError("jsonファイルの文字エンコードはUTF-8にしてください")
        except json.JSONDecodeError as e:
            raise ProcessError("json文法にエラーがあります\n{0.msg} ({0.lineno}行, {0.colno}列)".format(e))

        cls.__logger.info("uploadQuestion")

    @classmethod
    async def addOptionalQuestion(cls, args, client: discord.Client, message: discord.Message) -> NoReturn:
        cls.__logger.info("addOptionalQuestion")

    @classmethod
    async def run(cls, args, client, message: discord.Message) -> NoReturn:
        if hasattr(args, "proc"):
            await args.proc(args, client, message)
        else:
            await message.channel.send(cls.__parser.format_help())

    @classmethod
    def addProcessor(cls):
        VemtClient.addSubCommand(ConfigProcess)

    @classmethod
    def parseQuestionJson(cls, json_obj: dict) -> Tuple[dict, List[str]]:
        """ 質問をまとめたjsonのエラーチェックする """
        # エラーチェック
        question: dict = {}
        error_msgs: List[str] = []
        cls.__logger.debug("-- Parsing question json.")
        if "title" in json_obj:
            question["title"] = json_obj["title"]
        else:
            error_msgs.append("項目\"title\"がありません")

        question["description"] = ""
        if "descriptions" in json_obj:
            if type(json_obj["descriptions"]) is list:
                for dline in json_obj["descriptions"]:
                    if type(dline) is str:
                        question["description"] += dline + "\n"
                    else:
                        error_msgs.append("項目\"description\"は文字列である必要があります")
                        break
            else:
                error_msgs.append("項目\"description\"は行ごとのリストである必要があります")

        cls.__logger.debug("-- Parsed question header json.")
        index = 1
        if "items" in json_obj:
            question["items"] = []
            for itm in json_obj["items"]:
                # text
                q_item: dict = {}
                q_item["text"] = ""
                if "text" in itm:
                    q_item["text"] = itm["text"]
                else:
                    error_msgs.append(str(index) + "問目:項目\"items\"には、\"text\"が必ず必要です")

                # type
                itm["type"] = "string"
                if "type" in itm:
                    if itm["type"] in ["string", "number", "picture", "regex", "json"]:
                        q_item["type"] = itm["type"]
                    else:
                        error_msgs.append(str(index) + "問目:項目\"type\"はstring, number, picture, regex, jsonの中から選択する必要があります")
                else:
                    error_msgs.append(str(index) + "問目:項目\"items\"には、\"type\"が必ず必要です")

                # length
                q_item["length"] = 200
                if "length" in itm:
                    if type(itm["length"]) is int:
                        if 0 < itm["length"] and itm["length"] <= 200:
                            q_item["length"] = itm["length"]
                        else:
                            error_msgs.append(str(index) + "問目:項目\"length\"には、1文字以上、200文字以下を指定してください")
                    else:
                        error_msgs.append(str(index) + "問目:項目\"length\"には、回答文字列の制限長を整数で入力する必要があります")

                # choise
                q_item["choise"] = None
                if "choise" in itm:
                    if type(itm["choise"]) is list:
                        if len(itm["choise"]) > 1:
                            q_item["choise"]: List[str] = []
                            for c in itm["choise"]:
                                if type(c) is str:
                                    q_item["choise"].append(c)
                                else:
                                    error_msgs.append(str(index) + "問目:選択肢\"choise\"は文字列のみです ({})".format(c))
                        else:
                            error_msgs.append(str(index) + "問目:選択肢\"choise\"は2つ以上用意しなければなりません")
                    else:
                        error_msgs.append(str(index) + "問目:選択肢\"choise\"はリストを指定します")

                # is_required
                q_item["is_required"] = False
                if "is_required" in itm:
                    if type(itm["is_required"]) is bool:
                        q_item["is_required"] = itm["is_required"]
                    else:
                        error_msgs.append(str(index) + "問目:項目\"is_required\"はboolean型です")

                # regex_rule
                q_item["regex_rule"] = ".+"
                if "regex_rule" in itm:
                    if type(itm["regex_rule"]) is str:
                        q_item["regex_rule"] = itm["regex_rule"]
                    else:
                        error_msgs.append(str(index) + "問目:項目\"regex\"は文字列です")

                # limit_phase
                q_item["limit_phase"] = None
                if "limit_phase" in itm:
                    if type(itm["limit_phase"]) is str:
                        if itm["limit_phase"] in ["entry", "submit", "publish"]:
                            q_item["limit_phase"] = itm["limit_phase"]
                        else:
                            error_msgs.append(str(index) + "問目:項目\"limit_phase\"はentry, submit, publishから選んでください")
                    else:
                        error_msgs.append(str(index) + "問目:項目\"limit_phase\"はentry, submit, publishから選んでください")
                if q_item["is_required"] and q_item["limit_phase"] is None:
                    error_msgs.append(str(index) + "問目:項目\"is_required\"がTrueの場合は、項目\"limit_phase\"は必須です")

                # limit_datetime
                q_item["limit_datetime"] = None
                if "limit_datetime" in itm:
                    if type(itm["limit_datetime"]) is str:
                        # ここでlimit-datetimeのフォーマットをチェック
                        # 時間がdatetimeの、現在以降であることをチェック
                        q_item["limit_datetime"] = itm["limit_datetime"]  # 日付
                    else:
                        error_msgs.append(str(index) + "問目:項目\"limit_datetime\"は文字列で指定してください")
                question["items"].append(q_item)

                cls.__logger.debug("-- Parsed [%d] question item.")
                index += 1

        cls.__logger.info("-- Parsed question json. %d errors.", len(error_msgs))
        return (question, error_msgs)
