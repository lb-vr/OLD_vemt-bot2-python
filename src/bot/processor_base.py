import abc
import argparse
import discord

from typing import NoReturn


class AuthenticationError(Exception):
    pass


class ProcessorError(Exception):
    pass


class ProcessorBase(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def addSubCommand(cls, subparser: argparse._SubParsersAction) -> NoReturn:
        pass

    @classmethod
    @abc.abstractmethod
    def authenticate(cls, args, client: discord.Client, message: discord.Message) -> NoReturn:
        pass

    @classmethod
    @abc.abstractmethod
    def run(cls, args, client: discord.Client, message: discord.Message) -> NoReturn:
        pass
