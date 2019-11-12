import argparse
import logging

from src.setup_log import setupLogger
from src.client import VemtClient


if __name__ == '__main__':

    # setup logger
    # logger = setupLogger("vemt", stdout_level=logging.INFO, logfile_level=logging.DEBUG)

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
