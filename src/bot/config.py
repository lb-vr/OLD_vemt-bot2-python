import discord
import argparse
import logging

from typing import NoReturn, List, Tuple, Optional

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
        cls.__logger.info("uploadQuestion")

    @classmethod
    async def addOptionalQuestion(cls, args, client: discord.Client, message: discord.Message) -> NoReturn:
        cls.__logger.info("addOptionalQuestion")

    @classmethod
    async def run(cls, args, client, message: discord.Message) -> NoReturn:
        if hasattr(args, "proc"):
            args.proc(args, client, message)
        else:
            await message.channel.send(cls.__parser.format_help())

    @classmethod
    def addProcessor(cls):
        VemtClient.addSubCommand(ConfigProcess)
