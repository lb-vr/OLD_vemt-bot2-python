import discord
import argparse
import logging
import subprocess
import os

from typing import NoReturn, List, Tuple, Optional

from bot.const import Definitions
from bot_config import Config
from client import VemtClient

from bot.processor_base import ProcessorBase, ProcessorError, AuthenticationError, ForbiddenChannelError, MyArgumentParser


class InitProcess(ProcessorBase):
    __logger = logging.getLogger("InitProcess")
    parser = None

    @classmethod
    def setupSubCommand(cls, subparser: argparse._SubParsersAction):
        cls.parser = subparser.add_parser("+init",
                                          help="Discordサーバーを初期化します",
                                          description="Discordサーバーにおいて、チャンネル、ロールなどを作成します。\n"
                                          + "このコマンドは、**サーバーのオーナーのみ**が発行することができます。")
        cls.parser.add_argument("server_name", help="確認のためサーバー名を入力してください", type=str, default="")
        cls.parser.set_defaults(handler=InitProcess)

    @classmethod
    async def authenticate(cls, args, client: discord.Client, message: discord.Message):
        # Guildオーナーのみ
        if message.guild:
            if message.guild.owner.id != message.author.id:
                raise AuthenticationError("+initコマンドはサーバーのオーナーのみが発行可能です")
        else:
            raise ForbiddenChannelError("+initコマンドはサーバーのテキストチャンネルのみで実行可能です")

    @classmethod
    async def run(cls, args, client, message: discord.Message):
        cls.__logger.info("Start to initialize discord server.")
        await message.channel.send('Discordサーバーを初期化します\n初期化中はサーバー設定の変更や、別のコマンドの発行をしないでください')

        if not message.guild:
            raise ProcessorError("ギルドの取得に失敗しました")
        guild: discord.Guild = message.guild
        cls.__logger.debug("- Guild ID = %d", guild.id)

        # 予約済みのチャンネルがあるか
        current_channels: List[discord.TextChannel] = guild.channels
        def_channels: Tuple[str] = Definitions.getAllChannels()
        cls.__logger.debug("- Listup guild channels.")
        for ch in current_channels:
            cls.__logger.debug("-- %s (%d)", ch.name, ch.id)
            for dc in def_channels:
                if ch.name == dc:
                    cls.__logger.error("Already exists reserved channel. Channel name = %s", ch.name)
                    raise ProcessorError("既に予約された名前のチャンネルが存在します")

        # 予約済みのロールがあるか
        everyone_role: Optional[discord.Role] = None
        current_roles: List[discord.Role] = guild.roles
        def_roles: Tuple[str] = Definitions.getAllRoles()
        cls.__logger.debug("- Listup guild roles.")
        for rl in current_roles:
            cls.__logger.debug("-- %s (%d)", rl.name, rl.id)
            for drl in def_roles:
                if rl.name == "@everyone":
                    everyone_role = rl
                elif rl.name == drl:
                    cls.__logger.error("Already exists reserved role. Role name = %s", rl.name)
                    raise ProcessorError("既に予約された名前のロールが存在します")

        if not everyone_role:
            cls.__logger.error("Not found @everyone role.", rl.name)
            raise ProcessorError("@everyoneロールが見つかりません")

        # ニックネーム
        cls.__logger.debug("- Changing BOT nickname to VEMT.")
        await guild.me.edit(nick="VEMT")
        cls.__logger.info("- Changed BOT nickname to VEMT.")

        # ロールを作る
        cls.__logger.debug("- Creating roles.")
        bot_admin_role: discord.Role = await guild.create_role(name=Definitions.getBotAdminRoleName(), hoist=True, mentionable=True, colour=discord.Color(0x3498db))
        manager_role: discord.Role = await guild.create_role(name=Definitions.getManagerRoleName(), hoist=True, mentionable=True, colour=discord.Color(0xe74c3c))
        exhibitor_role: discord.Role = await guild.create_role(name=Definitions.getExhibitorRoleName(), hoist=True, mentionable=True, colour=discord.Color(0x2ecc71))
        cls.__logger.info("- Created roles.")

        # カテゴリを作る
        cls.__logger.debug("- Creating categories.")
        bot_category: discord.CategoryChannel = await guild.create_category_channel(Definitions.getBotCategoryName())
        contact_category: discord.CategoryChannel = await guild.create_category_channel(
            Definitions.getContactCategoryName(),
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False)
            })
        cls.__logger.info("- Created categories.")

        # チャンネルを作る
        # BOTの管理用チャンネル
        cls.__logger.debug("- Creating channels.")
        bot_manage_channel: discord.TextChannel = await guild.create_text_channel(
            name=Definitions.getBotControlChannelName(),
            category=bot_category,
            topic="BOTの設定変更など、BOT管理を行うチャンネルです。`+config --help`でヘルプを表示します。",
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                bot_admin_role: discord.PermissionOverwrite(read_messages=True)
            }
        )

        # 出展応募用チャンネル
        entry_channel: discord.TextChannel = await guild.create_text_channel(
            name=Definitions.getEntryChannelName(),
            category=bot_category,
            topic="仮エントリーを申し込むためのチャンネルです。エントリー受付期間中、`+entry`で仮エントリーが可能です。",
            overwrites={
                guild.default_role: discord.PermissionOverwrite(send_messages=False)
            }
        )

        # 情報問い合わせ用チャンネル
        query_channel: discord.TextChannel = await guild.create_text_channel(
            name=Definitions.getQueryChannelName(),
            category=bot_category,
            topic="様々な情報を取得することができます。運営専用チャンネルです。`+query --help`でヘルプを表示します。",
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                manager_role: discord.PermissionOverwrite(read_messages=True)
            }
        )

        # ステータス確認用のチャンネル
        status_channel: discord.TextChannel = await guild.create_text_channel(
            name=Definitions.getStatusChannelName(),
            category=bot_category,
            topic="サーバーに関するステータス確認用のチャンネルです。",
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)
            }
        )
        cls.__logger.info("- Created channels.")

        # DBを作成
        db_proc = subprocess.Popen("sqlite3 {} < {}".format(Definitions.getDatabaseFilename(
            guild.id), os.path.abspath("src/db/scheme.sql")), shell=True)
        db_proc.wait()

        # サーバー固有のIDを記録する
        cls.__logger.debug("- Registing IDs.")
        cfg: Config = Config.getConfig(guild.id)
        cfg.setVal(Definitions.getGuildIdKey(), guild.id)
        cfg.setVal(Definitions.getBotCategoryKey(), bot_category.id)
        cfg.setVal(Definitions.getContactCategoryKey(), contact_category.id)
        cfg.setVal(Definitions.getBotControlChannelKey(), bot_manage_channel.id)
        cfg.setVal(Definitions.getEntryChannelKey(), entry_channel.id)
        cfg.setVal(Definitions.getQueryChannelKey(), query_channel.id)
        cfg.setVal(Definitions.getStatusChannelKey(), status_channel.id)
        cfg.setVal(Definitions.getBotAdminRoleKey(), bot_admin_role.id)
        cfg.setVal(Definitions.getManagerRoleKey(), manager_role.id)
        cfg.setVal(Definitions.getExhibitorRoleKey(), exhibitor_role.id)
        cls.__logger.info("- Registed.")

        await message.channel.send(
            "**成功** サーバーの初期化が完了しました\n" +
            "BOTコマンドについては、`+help`コマンドから参照することができます。（ただし<@&{}>か<@&{}>のみが発行可能です）\n".format(bot_admin_role.id, manager_role.id) +
            "質問の登録や期間設定などを<#{}>チャンネルで設定後、エントリーを開始してください".format(bot_manage_channel.id))
        cls.__logger.info("- Finished initializing guild. Guild : %s (%d)", guild.name, guild.id)

    @classmethod
    def addProcessor(cls):
        VemtClient.addSubCommand(InitProcess)
