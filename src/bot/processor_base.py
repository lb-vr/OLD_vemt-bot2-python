import abc
import argparse
import discord
import logging
import sys

from typing import NoReturn


class ArgError(Exception):
    pass


class ShowHelp(Exception):
    def __init__(self, help_str: str):
        self.__help_str: str = help_str
        super().__init__("It's ok.")

    @property
    def help_str(self) -> str:
        return self.__help_str


class AuthenticationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        logging.getLogger("AuthenticationError").error(message)


class ForbiddenChannelError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        logging.getLogger("ForbiddenChannelError").error(message)


class ProcessorError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        logging.getLogger("ProcessorError").error(message)


class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print(message)
        print(sys.exc_info())
        exc = sys.exc_info()[1]
        raise ArgError(exc)

    def _print_message(self, message, file=None):
        if message:
            #print(message, file=sys.stderr)
            raise ShowHelp(message)


class ProcessorBase(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def setupSubCommand(cls, subparser: argparse._SubParsersAction) -> NoReturn:
        pass

    @classmethod
    @abc.abstractmethod
    def authenticate(cls, args, client: discord.Client, message: discord.Message) -> NoReturn:
        pass

    @classmethod
    @abc.abstractmethod
    def run(cls, args, client: discord.Client, message: discord.Message) -> NoReturn:
        pass
