import discord
import argparse


def setupSubCommand(subparser: argparse._SubParsersAction):
    parser = subparser.add_parser("+exit", help="BOTを終了します")
    parser.set_defaults(handler=exit)


async def exit(args, client, message: discord.message.Message):
    await message.channel.send('+OK, See you.')
    await client.close()
