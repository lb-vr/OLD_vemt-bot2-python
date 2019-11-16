import discord
import argparse
import logging

from typing import NoReturn, List, Tuple, Optional

from .const import Definitions
from ..bot_config import Config
from ..client import VemtClient

from .processor_base import ProcessorBase, ProcessorError, AuthenticationError


class HelpProcess(ProcessorBase):
    __logger = logging.getLogger("HelpProcess")

    @classmethod
    def setupSubCommand(cls, subparser: argparse._SubParsersAction) -> NoReturn:
        parser = subparser.add_parser("+help", help="BOTヘルプを表示します")
        parser.set_defaults(handler=HelpProcess)
        parser.set_defaults(show_help=True)

    @classmethod
    async def authenticate(cls, args, client: discord.Client, message: discord.Message) -> NoReturn:
        pass

    @classmethod
    async def run(cls, args, client, message: discord.Message) -> NoReturn:
        pass  # ここに処理は来ない。

    @classmethod
    def addProcessor(cls):
        VemtClient.addSubCommand(HelpProcess)
