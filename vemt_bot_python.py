import argparse
import logging

from src.setup_log import setupLogger
from src.client import VemtClient
from src.bot.add_processor import addProcessors

if __name__ == '__main__':

    # setup logger
    logger = setupLogger("vemt", stdout_level=logging.DEBUG, logfile_level=logging.DEBUG)

    # suppress logger
    for logger_name in (
        "discord.client",
        "discord.gateway",
        "discord.http",
        "websockets.protocol",
        "asyncio"
    ):
        discord_logger = logging.getLogger(logger_name)
        discord_logger.setLevel(logging.WARNING)

    # setup processor
    addProcessors()

    # TODO: ここに説明を書く
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default="config/discord_token.txt", type=str, help="Filepath of token file.")
    args = parser.parse_args()

    # load token
    token_str: str = ""
    with open(args.token, mode="r", encoding="utf-8") as token_f:
        token_str = token_f.readline().strip()

    client = VemtClient()
    client.run(token_str)
