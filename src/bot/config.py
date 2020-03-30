from bot.processor_base import ProcessorBase, ProcessorError, AuthenticationError, MyArgumentParser, ForbiddenChannelError
import discord
import argparse
import logging
import json

from typing import NoReturn, List, Tuple, Optional, Dict

# from bot.const import Definitions
# from bot_config import Config
from definitions import CategoryName, ChannelName, RoleName

from db.database import Database
from db.registry.guild import RegistryGuild
from db.registry.schedule import RegistrySchedule
from db.registry.server import RegistryServer
from db.registry.event import RegistryEvent
from db.registry.submit import RegistrySubmit
from db.question.prologue import PrologueDB
from db.question.question_item import QuestionItemDB
from db.utility import getDBFilepath

from client import VemtClient
# from question import Question

from configs.loader import parseConfigFromJson
from configs.event import Event
from configs.schedule import Schedule
from configs.question import Question
from configs.submit import Submit

from bot.query import QueryProcess


class ConfigProcess(ProcessorBase):
    __logger = logging.getLogger("ConfigProcess")

    parser = None

    @classmethod
    def setupSubCommand(cls, subparser: argparse._SubParsersAction):
        cls.parser = subparser.add_parser("+config", help="BOTの設定を変更します")
        cls.parser.set_defaults(handler=ConfigProcess)
        subp = cls.parser.add_subparsers(parser_class=MyArgumentParser)

        # -- サーバー設定subparser
        parser_set = subp.add_parser("set", help="サーバー設定すべての設定")
        parser_set.set_defaults(proc=cls.setServerConfiguration)

        # -- questionのsubparser
        # parser_question = subp.add_parser("question", help="質問関連の設定")
        # subp_question = parser_question.add_subparsers(parser_class=MyArgumentParser)

        # +config question upload
        # parser_question_upload = subp_question.add_parser("upload", help="jsonファイルから質問を設定します")
        # parser_question_upload.add_argument("--preview", action="store_true", help="質問を更新しませんが、最終的な見た目を確認することができます")
        # parser_question_upload.set_defaults(proc=cls.uploadQuestion)

        # +config question add
        # parser_question_add = subp_question.add_parser("add",
        #                                                help="任意回答の質問を末尾に追加します",
        #                                                description="新しい質問を、既存の質問の末尾に追加します。\n追加できる質問はすべて**任意回答**となります。")
        # parser_question_add.add_argument("text", type=str, help="簡潔な質問文")
        # parser_question_add.add_argument("--details", nargs="+", type=str, help="質問文の補足などを行います。行ごとに空白で区切ってください。")
        # parser_question_add.add_argument("--type", type=str, default="string",
        #                                  choices=["string", "number", "picture", "regex", "json"], help="期待する回答の種類を指定します")
        # parser_question_add.add_argument("--choise", type=str, nargs="+", default=[], help="回答を選択式にします")
        # parser_question_add.add_argument("--length", type=int, default=200, help="回答の最大文字数を入力します")
        # parser_question_add.add_argument("--regex_rule", type=str, default=".+", help="回答を受理する正規表現を指定します")
        # parser_question_add.set_defaults(proc=cls.addOptionalQuestion)

    @classmethod
    async def authenticate(cls, args, client: discord.Client, message: discord.Message):
        # そもそもGuild上か
        if message.guild is None:
            raise ForbiddenChannelError("コマンドはDiscordサーバーにて発行してください")

        with Database(getDBFilepath(message.guild.id)) as db:
            reg_server = RegistryServer(db)
            if not reg_server.isInitializedServer():
                raise ProcessorError("このサーバーはまだ初期化されていません")

            # Guildオーナーのみ
            if message.guild.owner.id != message.author.id:
                raise AuthenticationError("+init command is permitted for guild owner.")

    @classmethod
    async def setServerConfiguration(cls, args, client: discord.Client, message: discord.Message):
        cls.__logger.debug("start to setup server from json.")
        if len(message.attachments) != 1:
            raise ProcessorError("jsonファイルが添付されていないか、複数添付されています")

        json_obj: dict = {}
        try:
            json_bytes = await message.attachments[0].read()
            cls.__logger.debug("- json data length: %d", len(json_bytes))
            json_str = json_bytes.decode("utf-8")
            json_obj = json.loads(json_str)
            cls.__logger.debug("- json parsed.")

        except UnicodeDecodeError:
            cls.__logger.error("Json file must be wrote with utf-8.")
            raise ProcessorError("JSONファイルはUTF-8で記述されている必要があります")
        except json.JSONDecodeError as e:
            cls.__logger.error("Failed to parse JSON. %s", e)
            raise ProcessorError("JSONのパース中にエラーが発生しました\n" + str(e))

        # json parse
        try:
            event: Event = parseConfigFromJson(json_obj["event"], Event)
            schedule: Schedule = parseConfigFromJson(json_obj["schedule"], Schedule)
            question: Question = parseConfigFromJson(json_obj["question"], Question)
            submit: Submit = parseConfigFromJson(json_obj["submit"], Submit)

            # DBに登録
            with Database(getDBFilepath(message.guild.id), isolation_level="EXCLUSIVE") as db:
                reg_event = RegistryEvent(db)
                reg_event.setEvent(event)

                reg_schedule = RegistrySchedule(db)
                reg_schedule.setSchedule(schedule)

                db_prologue = PrologueDB(db)
                db_prologue.setPrologue(question.prologue)

                db_qitem = QuestionItemDB(db)
                db_qitem.clearAllQuestionItems()
                qitem_id = 1
                for qitem in question.require:
                    qitem.id = qitem_id
                    db_qitem.setQuestionItem(qitem, True)
                    qitem_id += 1

                for qitem in question.optional:
                    qitem.id = qitem_id
                    db_qitem.setQuestionItem(qitem, False)
                    qitem_id += 1

                reg_submit = RegistrySubmit(db)
                reg_submit.setSubmit(submit)

                db.commit()

        except (KeyError, TypeError) as e:
            cls.__logger.error("Json content error. %s", e)
            raise ProcessorError("JSON記述内容に誤りがあります\n" + str(e))
        pass

        await message.channel.send("設定が完了しました - 以下設定内容を表示します")
        # await Queryの表示
        setattr(args, "hide", [])
        await QueryProcess.showServerSettings(args, client, message)

    @classmethod
    async def run(cls, args, client, message: discord.Message):
        if hasattr(args, "proc"):
            await args.proc(args, client, message)
        else:
            await message.channel.send(cls.__parser.format_help())

    @classmethod
    def addProcessor(cls):
        VemtClient.addSubCommand(ConfigProcess)
