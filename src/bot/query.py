from bot.processor_base import ProcessorBase, ProcessorError, AuthenticationError, MyArgumentParser, ForbiddenChannelError
import discord
import argparse
import logging
import json
import datetime

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


class QueryProcess(ProcessorBase):
    __logger = logging.getLogger("QueryProcess")

    parser = None

    @classmethod
    def setupSubCommand(cls, subparser: argparse._SubParsersAction):
        cls.parser = subparser.add_parser("+query", help="様々な情報を問い合わせます")
        cls.parser.set_defaults(handler=QueryProcess)
        subp = cls.parser.add_subparsers(parser_class=MyArgumentParser)

        # -- サーバー設定subparser
        parser_server: argparse.ArgumentParser = subp.add_parser("server", help="サーバー設定")
        parser_server.add_argument("--hide", nargs="+",
                                   choices=["event", "schedule", "question", "submit"],
                                   help="表示しない項目を指定します",
                                   default=[])
        parser_server.set_defaults(proc=cls.showServerSettings)

    @classmethod
    async def authenticate(cls, args, client: discord.Client, message: discord.Message):
        # そもそもGuild上か
        if message.guild is None:
            raise ForbiddenChannelError("コマンドはDiscordサーバーにて発行してください")

        with Database(getDBFilepath(message.guild.id)) as db:
            reg_server = RegistryServer(db)
            if not reg_server.isInitializedServer():
                raise ProcessorError("このサーバーはまだ初期化されていません")

            # Managerのみ
            roles = message.author.roles
            reg_guild = RegistryGuild(db)
            manager_role_id = reg_guild.getRoleManagerId()
            assert manager_role_id is not None
            for role in roles:
                if role.id == manager_role_id:
                    break
            else:
                raise AuthenticationError("Only manager can call +query command.")

    @classmethod
    async def showServerSettings(cls, args, client: discord.Client, message: discord.Message):
        cls.__logger.debug("show server settings.")
        text: List[str] = []
        with Database(getDBFilepath(message.guild.id)) as db:
            if "event" not in args.hide:
                event = RegistryEvent(db).getEvent()
                if event is not None:
                    text += [
                        "+ Event",
                        "|---+ Owner",
                        "|   |---: name   = {}".format(event.owner.name),
                        "|   |---: discord= {}".format(event.owner.discord),
                        "|",
                        "|---: website={}".format(event.website),
                        "|---+ title",
                        "|   |---: jp ={}".format(event.title.jp),
                        "|   |---: en ={}".format(event.title.en),
                        "|   |---: ko ={}".format(event.title.ko),
                        "|",
                        "|---+ description",
                        "|   |---: jp ===",
                        str(event.description.jp),
                        "|   |---: en ===",
                        str(event.description.en),
                        "|   |---: ko ===",
                        str(event.description.ko),
                        "|"
                    ]

            if "schedule" not in args.hide:
                schedule = RegistrySchedule(db).getSchedule()

                def _timestr(dt: datetime.datetime) -> str:
                    assert dt is None or type(dt) is datetime.datetime
                    if dt is not None:
                        return dt.strftime("%Y-%m-%d %H:%M:%S")
                    return "<NOT SET>"

                if schedule is not None:
                    text += [
                        "+ Schedule",
                        "|---+ Date",
                        "|   |---: since = " + _timestr(schedule.date.since),
                        "|   |---: until = " + _timestr(schedule.date.until),
                        "|",
                        "|---+ Limitation",
                        "|   |---+ Entry",
                        "|   |   |---: since = " + _timestr(schedule.limitation.entry.since),
                        "|   |   |---: until = " + _timestr(schedule.limitation.entry.until),
                        "|   |",
                        "|   |---+ Attend",
                        "|   |   |---: since =  " + _timestr(schedule.limitation.attend.since),
                        "|   |   |---: until =  " + _timestr(schedule.limitation.attend.until),
                        "|   |",
                        "|   |---+ Submit",
                        "|   |   |---: since =  " + _timestr(schedule.limitation.submit.since),
                        "|   |   |---: until =  " + _timestr(schedule.limitation.submit.until),
                        "|   |",
                        "|   |---+ FinalSubmit",
                        "|   |   |---: since =  " + _timestr(schedule.limitation.final_submit.since),
                        "|   |   |---: until =  " + _timestr(schedule.limitation.final_submit.until),
                        "|   |",
                        "|   |---+ Catalog",
                        "|   |   |---: since =  " + _timestr(schedule.limitation.catalog.since),
                        "|   |   |---: until = " + _timestr(schedule.limitation.catalog.until),
                        "|   |",
                        "|"
                    ]

            if "question" not in args.hide:
                prologue = PrologueDB(db).getPrologue()
                text += [
                    "+ Question",
                    "|---: prologue.jp === ",
                    prologue.jp if prologue.jp is not None else "<NOT SET>",
                    "|---: prologue.en === ",
                    prologue.en if prologue.en is not None else "<NOT SET>",
                    "|---: prologue.ko === ",
                    prologue.ko if prologue.ko is not None else "<NOT SET>",
                    "|"
                ]

                def _printQuestionItem(question_item_db: QuestionItemDB, is_request: bool) -> List[str]:
                    ret: List[str] = []
                    questions = question_item_db.getAllQuestions(is_request=is_request)
                    for qitem in questions:
                        ret += [
                            "|   |---+ QuestionItem[{}]".format(qitem.id),
                            "|   |   |---: header = [{0.jp}, {0.en}, {0.ko}]".format(qitem.header),
                            "|   |   |---: detail_jp ===",
                            str(qitem.description.jp),
                            "|   |   |---: detail_en ===",
                            str(qitem.description.en),
                            "|   |   |---: detail_ko ===",
                            str(qitem.description.ko),
                            "|   |   |---: nargs_string   ={0.nargs}".format(qitem),
                            "|   |   |---: type           ={0.type}".format(qitem),
                            "|   |   |---: regex          ={0.regex_rule}".format(qitem),
                            "|   |   |---: length         ={0.length}".format(qitem),
                            "|   |   |---: limit_phase    ={0.limit_phase}".format(qitem),
                            "|   |   |---: allow_multiline={0.allow_multiline}".format(qitem),
                            "|   |   |---: choices        ={0.choice}".format(qitem),
                            "|   |   |---: key            ={0.key}".format(qitem),
                            "|   |   |---: min, max       =[{0.min}, {0.max}]".format(qitem),
                            "|   |"]
                    return ret

                question_item_db = QuestionItemDB(db)
                text += ["|---+ Reqired"] + _printQuestionItem(question_item_db, True) + ["|"]
                text += ["|---+ Optional"] + _printQuestionItem(question_item_db, False) + ["|"]

        # 文字数ごとに切り分ける
        message_str: str = ""
        for t in text:
            assert len(t) < 1990
            if len(message_str + t) >= 1990:
                await message.channel.send("```" + message_str.strip() + "```")
                message_str = ""
            message_str += t + "\n"
        if message_str:
            await message.channel.send("```" + message_str.strip() + "```")
        await message.channel.send("=== 【以上】 ===")

    @classmethod
    async def run(cls, args, client, message: discord.Message):
        if hasattr(args, "proc"):
            await args.proc(args, client, message)
        else:
            await message.channel.send(cls.__parser.format_help())

    @classmethod
    def addProcessor(cls):
        VemtClient.addSubCommand(QueryProcess)
