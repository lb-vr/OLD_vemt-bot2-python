import discord
import argparse


def setupSubCommand(subparser: argparse._SubParsersAction):
    parser = subparser.add_parser("+init", help="Discordサーバーを初期化します")
    parser.set_defaults(handler=initcmd)


async def initcmd(args, client, message: discord.message.Message):
    await message.channel.send('Discordサーバーを初期化します')
