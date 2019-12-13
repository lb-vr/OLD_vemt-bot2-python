from bot.init import InitProcess
from bot.exit import ExitProcess
from bot.reset import ResetProcess
from bot.config import ConfigProcess
from bot.help import HelpProcess


def addProcessors(is_dev: bool = False):
    InitProcess.addProcessor()
    if is_dev:
        ExitProcess.addProcessor()
        ResetProcess.addProcessor()

    ConfigProcess.addProcessor()
    HelpProcess.addProcessor()
