import argparse
import discord
import logging
import sys
import shlex

from bot.processor_base import MyArgumentParser, ProcessorBase, ShowHelp
from bot.processor_base import ProcessorError, ArgError, AuthenticationError, ForbiddenChannelError


class VemtClient(discord.Client):
    __parser: MyArgumentParser = MyArgumentParser(
        prog="",
        usage="VEMT",
        description="VEMT-BOTは、\"+\"文字を先頭に付けたコマンドをもとに処理を行います。\n"
        + "Discordのメッセージとしてコマンドを入力し、送信することで解釈を行います。 \n"
        + "コマンドによっては、権限によって制限されたものや、チャンネルが決まっています。\n",
        epilog="それぞれのコマンドについて詳しく知るには、`+<コマンド> --help`で見ることが可能です。",
        add_help=False)
    __subparser = None

    @classmethod
    def addSubCommand(cls, processor):
        logger = logging.getLogger("VemtClient")
        if not cls.__subparser:
            cls.__subparser = cls.__parser.add_subparsers(parser_class=MyArgumentParser)
        processor.setupSubCommand(cls.__subparser)
        logger.debug("loaded sub command: %s", processor.__class__.__name__)

    async def on_ready(self):
        logger = logging.getLogger()
        logger.info('Logged on as {0}!'.format(self.user))

    async def on_message(self, message: discord.Message):
        logger = logging.getLogger()

        if (not message.author.bot and message.content.startswith("+")):
            logger.debug('Message from {0.author} ({0.author.id}): {0.content}'.format(message))
            try:
                args = VemtClient.__parser.parse_args(shlex.split(message.content))
                logger.debug("arguments : %s", args)

                if hasattr(args, "handler"):
                    processor: ProcessorBase = args.handler()
                    await processor.authenticate(args, self, message)
                    if hasattr(args, "help") and args.help and hasattr(processor, "parser"):
                        await message.channel.send(processor.parser.format_help())
                    elif hasattr(args, "show_help") and not hasattr(args, "help_on_help"):
                        VemtClient.__parser.print_help()
                    else:
                        await processor.run(args, self, message)
                else:
                    raise ProcessorError("そのようなコマンドは存在しません")

            except ShowHelp as e:
                await message.channel.send(e.help_str)
            except ArgError as e:
                err_str: str = str(e)
                err_str = err_str.replace("unrecognized arguments:", "不明な引数が指定されました:") \
                    .replace("invalid choice:", "不正な引数選択です:") \
                    .replace("choose from", "次のうちから選んでください:") \
                    .replace("the following arguments are required:", "次の引数は必ず指定してください:")
                await message.channel.send(":x: " + err_str)
            except SystemExit as e:
                logger.debug("stopped to exit system.")
            except AuthenticationError as e:
                await message.channel.send(":x: **失敗** このコマンドを実行する権限がありません")
            except ForbiddenChannelError as e:
                await message.channel.send(":x: **失敗** このチャンネルではこのコマンドを実行できません")
            except ProcessorError as e:
                await message.channel.send(":x: **失敗** " + str(e))
