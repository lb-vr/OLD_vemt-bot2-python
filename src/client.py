import argparse
import discord
import logging
import sys

from .bot.processor_base import ProcessorBase, AuthenticationError, ProcessorError


class ArgError(Exception):
    pass


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        exc = sys.exc_info()[1]
        raise ArgError(exc)


class VemtClient(discord.Client):
    __parser: ArgumentParser = ArgumentParser()
    __subparser = None
    @classmethod
    def addSubCommand(cls, processor: ProcessorBase):
        logger = logging.getLogger(__file__)
        if not cls.__subparser:
            cls.__subparser = cls.__parser.add_subparsers()
        processor.setupSubCommand(cls.__subparser)
        logger.debug("loaded sub command: %s", processor.__class__.__name__)

    async def on_ready(self):
        logger = logging.getLogger()
        logger.info('Logged on as {0}!'.format(self.user))

    async def on_message(self, message: discord.Message):
        logger = logging.getLogger()
        logger.debug('Message from {0.author}: {0.content}'.format(message))

        if (not message.author.bot and message.content.startswith("+")):
            try:
                args = VemtClient.__parser.parse_args(message.content.split())

                if (hasattr(args, "handler")):
                    processor: ProcessorBase = args.handler()
                    await processor.authenticate(args, self, message)
                    await processor.run(args, self, message)
            except ArgError as e:
                print(e)
                await message.channel.send(str(e))
            except AuthenticationError as e:
                pass
            except ProcessorError as e:
                pass

            else:
                # print(VemtClient.__parser.format_help())
                pass
                # await message.channel.send(VemtClient.__parser.format_help())
