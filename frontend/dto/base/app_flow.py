from enum import Enum, auto

class AppFlowSignal(Enum):
    GO = auto()
    NO_GO = auto()
    ERROR = auto()
    RERUN = auto()