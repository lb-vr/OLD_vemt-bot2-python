import argparse
import discord
import logging

from .bot import exit


class VemtClient(discord.Client):
    async def on_ready(self):
        logger = logging.Logger("on_ready")
        logger.info('Logged on as {0}!'.format(self.user))

    async def on_message(self, message: discord.message.Message):
        logger = logging.Logger("on_message")
        logger.debug('Message from {0.author}: {0.content}'.format(message))

        if (not message.author.bot):
            parser = argparse.ArgumentParser()
            subparser = parser.add_subparsers()
            exit.setupSubCommand(subparser)

            args = parser.parse_args(message.content.split())

            if (hasattr(args, "handler")):
                await args.handler(args, self, message)

            else:
                await self.close()
