import discord
import argparse

from typing import NoReturn

from .const import Definitions
from ..client import VemtClient


class InitProcess:

    @classmethod
    def setupSubCommand(cls, subparser: argparse._SubParsersAction) -> NoReturn:
        parser = subparser.add_parser("+init", help="Discordサーバーを初期化します")
        parser.set_defaults(handler=InitProcess)

    @classmethod
    async def authenticate(cls, args, client: discord.Client, message: discord.Message) -> NoReturn:
        pass

    @classmethod
    async def run(cls, args, client, message: discord.message.Message) -> NoReturn:
        await message.channel.send('Discordサーバーを初期化します')

    @classmethod
    def addProcessor(cls):
        VemtClient.addSubCommand(InitProcess)
