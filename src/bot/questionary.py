import discord
import argparse
import logging
import subprocess
import datetime
import os

from typing import NoReturn, List, Tuple, Optional

# from bot.const import Definitions
# from bot_config import Config
from client import VemtClient

from bot.processor_base import ProcessorBase, ProcessorError, AuthenticationError
from bot.processor_base import ForbiddenChannelError, MyArgumentParser, PeriodError

from db.database import Database
from db.registry.server import RegistryServer
from db.registry.schedule import RegistrySchedule
from db.registry.guild import RegistryGuild
from db.utility import getDBFilepath
from db.user.entries import Entries


class QuestionaryProcess(ProcessorBase):
    __logger = logging.getLogger("QuestionaryProcess")
    parser = None

    @classmethod
    def setupSubCommand(cls, subparser: argparse._SubParsersAction):
        cls.parser = subparser.add_parser("+entry",
                                          help="エントリーを行います",
                                          description="出展エントリーを行います。\n"
                                          + "このコマンドは、エントリー期間のみ、イベントに出展予定の方が使用します。")
        cls.parser.set_defaults(handler=QuestionaryProcess)

    @classmethod
    async def authenticate(cls, args, client: discord.Client, message: discord.Message):
        # サーバーは初期化済みか
        with Database(getDBFilepath(message.guild.id)) as db:
            reg_server = RegistryServer(db)
            if not reg_server.isInitializedServer():
                raise ProcessorError("このサーバーはまだ初期化されていません")

            # 既にエントリーしていない？
            user = Entries(db).getEntryInfoFromDiscordID(message.author.id)
            if user is not None:
                raise ProcessorError("既にエントリーが完了しています")

            # エントリー期間か？
            now = datetime.datetime.now()
            entry_period = RegistrySchedule(db).getEntryPeriod()
            if not entry_period.isWithin(now):
                raise PeriodError("現在エントリー可能期間ではありません")

            # エントリーチャンネルか
            reg_guild = RegistryGuild(db)
            assert message.channel.id is not None
            channel_id = reg_guild.getChannelEntryId()
            if message.channel.id != channel_id:
                raise ForbiddenChannelError("エントリーは<#{}>チャンネルのみで受け付けています".format(channel_id))

    @classmethod
    async def run(cls, args, client, message: discord.Message):
        with Database(getDBFilepath(message.guild.id)) as db:
            reg_guild = RegistryGuild(db)

            # 役職「Exhibitor」を与える
            exhibitor_role_id = reg_guild.getRoleExhibitorId()
            assert exhibitor_role_id is not None, "Database Error"
            exhibitor_role = message.guild.get_role(exhibitor_role_id)
            await message.author.add_roles(exhibitor_role)

            # 役職「Manager」を取得
            manager_role_id = reg_guild.getRoleManagerId()
            assert manager_role_id is not None, "Database Error"
            manager_role = message.guild.get_role(manager_role_id)

            # Contactカテゴリ取得
            contact_category_id = reg_guild.getCategoryContactId()
            assert contact_category_id is not None, "Database Error"
            contact_category = message.guild.get_channel(contact_category_id)

            # チャンネルを作成
            channel_name = message.author.nick if message.author.nick is not None else str(message.author.name)
            contact_channel = await message.guild.create_text_channel(
                name="{}-{}".format(channel_name, message.author.id),
                overwrites={
                    message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    message.author: discord.PermissionOverwrite(read_messages=True),
                    manager_role: discord.PermissionOverwrite(read_messages=True)
                },
                category=contact_category
            )

            # チャンネルにテキストチャット
            await contact_channel.send("<@!{}>さん、こちらがコンタクトチャンネルです。".format(message.author.id))

        with Database(getDBFilepath(message.guild.id), isolation_level="EXCLUSIVE") as db:
            # エントリーをDBに
            user = Entries(db).addNewUser(message.author.id, contact_channel.id)
            cls.__logger.info("Entried! User=%s", user)
            db.commit()

        # レス
        await message.add_reaction("✅")
        await message.channel.send(
            "<@!{}>さん、仮エントリーを受け付けました。CONTACTチャンネルにて、手続きを続行してください。".format(message.author.id))

    @classmethod
    def addProcessor(cls):
        VemtClient.addSubCommand(EntryProcess)
