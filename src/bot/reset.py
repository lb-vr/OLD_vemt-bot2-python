import discord
import argparse

from typing import NoReturn, List, Tuple, Optional

from .const import Definitions
from ..bot_config import Config
from ..client import VemtClient

from .processor_base import ProcessorBase, ProcessorError, AuthenticationError


class ResetProcess(ProcessorBase):

    @classmethod
    def setupSubCommand(cls, subparser: argparse._SubParsersAction) -> NoReturn:
        parser = subparser.add_parser("+reset", help="【BOT開発専用】Discordサーバーをもとの状態に戻します", add_help=False)
        parser.set_defaults(handler=ResetProcess)

    @classmethod
    async def authenticate(cls, args, client: discord.Client, message: discord.Message) -> NoReturn:
        pass

    @classmethod
    async def run(cls, args, client, message: discord.Message) -> NoReturn:
        await message.channel.send('Discordサーバーをもとに戻しています')

        if not message.guild:
            raise ProcessorError("ギルドの取得に失敗しました")
        guild: discord.Guild = message.guild

        # 作成済みのチャンネルを削除
        # あえて名前一致で削除する
        current_channels: List[discord.TextChannel] = guild.channels
        def_channels: Tuple[str] = Definitions.getAllChannels()
        for ch in current_channels:
            for dc in def_channels:
                if ch.name == dc:
                    await ch.delete()

        # 作成済みのチャンネルを削除
        current_roles: List[discord.Role] = guild.roles
        def_roles: Tuple[str] = Definitions.getAllRoles()
        for rl in current_roles:
            for drl in def_roles:
                if rl.name == drl:
                    await rl.delete()

        # ニックネーム戻す
        await guild.me.edit(nick=None)

        # Json削除
        Config.remove(guild.id)

        await message.channel.send("**成功** サーバーをもとに戻しました\n")

    @classmethod
    def addProcessor(cls):
        VemtClient.addSubCommand(ResetProcess)
