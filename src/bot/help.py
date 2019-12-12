import discord
import argparse
import logging

from typing import NoReturn, List, Tuple, Optional

from bot.const import Definitions
from bot_config import Config
from client import VemtClient

from bot.processor_base import ProcessorBase, ProcessorError, AuthenticationError


class HelpProcess(ProcessorBase):
    __logger = logging.getLogger("HelpProcess")
    parser = None

    @classmethod
    def setupSubCommand(cls, subparser: argparse._SubParsersAction):
        cls.parser = subparser.add_parser("+help", help="BOTヘルプを表示します", add_help=False)
        cls.parser.add_argument("-h", "--help", action="store_true", dest="help_on_help")
        cls.parser.set_defaults(handler=HelpProcess)
        cls.parser.set_defaults(show_help=True)

    @classmethod
    async def authenticate(cls, args, client: discord.Client, message: discord.Message):
        pass

    @classmethod
    async def run(cls, args, client, message: discord.Message):
        await message.channel.send("ヘルプのヘルプ…:thinking_face:\n"
                                   + "もし何か困りごとがあれば、開発者の<@!462643174087720971>に聞いてみてね！")

    @classmethod
    def addProcessor(cls):
        VemtClient.addSubCommand(HelpProcess)
