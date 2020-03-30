import discord
import argparse

from typing import NoReturn, List, Tuple, Optional

# from bot.const import Definitions
from client import VemtClient
from definitions import CategoryName, ChannelName, RoleName

from bot.processor_base import ProcessorBase, ProcessorError, AuthenticationError, ForbiddenChannelError

from db.user.entries import Entries
from db.database import Database
from db.utility import getDBFilepath


class ResetProcess(ProcessorBase):

    @classmethod
    def setupSubCommand(cls, subparser: argparse._SubParsersAction):
        parser = subparser.add_parser("+reset", help="【BOT開発専用】Discordサーバーをもとの状態に戻します", add_help=False)
        parser.set_defaults(handler=ResetProcess)

    @classmethod
    async def authenticate(cls, args, client: discord.Client, message: discord.Message):
        if message.guild is None:
            raise ForbiddenChannelError("+resetコマンドはサーバーのテキストチャンネルでのみ実行可能です")
        if message.guild.owner.id != message.author.id:
            raise AuthenticationError("+resetコマンドはサーバーのオーナーのみが発行可能です")

    @classmethod
    async def run(cls, args, client, message: discord.Message):
        await message.channel.send('Discordサーバーをもとに戻しています')

        if not message.guild:
            raise ProcessorError("ギルドの取得に失敗しました")
        guild: discord.Guild = message.guild

        # 作成済みのチャンネルを削除
        # あえて名前一致で削除する
        current_channels: List[discord.TextChannel] = guild.channels
        def_channels: List[str] = ChannelName.getAll() + CategoryName.getAll()
        for ch in current_channels:
            for dc in def_channels:
                if ch.name == dc:
                    await ch.delete()

        # コンタクトチャンネル
        with Database(getDBFilepath(message.guild.id)) as db:
            def_contact_channels: List[str] = \
                [item["contact_channel_id"] for item in db.select("entries", columns=["contact_channel_id"])]
            for ch in current_channels:
                for dc in def_contact_channels:
                    if ch.name == dc:
                        await ch.delete()

        # 作成済みのロールを削除
        current_roles: List[discord.Role] = guild.roles
        def_roles: Tuple[str] = RoleName.getAll()
        for rl in current_roles:
            for drl in def_roles:
                if rl.name == drl:
                    await rl.delete()

        # ニックネーム戻す
        await guild.me.edit(nick=None)
        await message.channel.send("**成功** サーバーをもとに戻しました\n")

    @classmethod
    def addProcessor(cls):
        VemtClient.addSubCommand(ResetProcess)
