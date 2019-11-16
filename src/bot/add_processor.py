from .init import InitProcess
from .exit import ExitProcess
from .reset import ResetProcess
from .config import ConfigProcess
from .help import HelpProcess


def addProcessors():
    InitProcess.addProcessor()
    ExitProcess.addProcessor()
    ResetProcess.addProcessor()
    ConfigProcess.addProcessor()
    HelpProcess.addProcessor()
