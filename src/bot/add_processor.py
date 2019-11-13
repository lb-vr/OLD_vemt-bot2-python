from .init import InitProcess
from .exit import ExitProcess


def addProcessors():
    InitProcess.addProcessor()
    ExitProcess.addProcessor()
    pass
