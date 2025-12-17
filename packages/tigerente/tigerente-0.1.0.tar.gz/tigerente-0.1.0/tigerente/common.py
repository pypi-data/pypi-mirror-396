import enum

HOST = "127.0.0.1"
PORT = 51656  # 656 = GSG

DEVICE_SEARCH_ROUND = 5
DEVICE_SEARCH_PAUSE = 1

DEVICE_TOO_OLD = 20

DEVICE_CONNECT_PAUSE = 3


class Querys(enum.Enum):
    GET_ALL_DEVICES = enum.auto()
    GET_NEAR_DEVICES = enum.auto()
    GET_DEVICE_BY_ADDRESS = enum.auto()
    SET_TARGET_DEVICE = enum.auto()
    UNSET_TARGET_DEVICE = enum.auto()
    GET_TARGET_DEVICE = enum.auto()
    KILL_DAEMON_PROCESS = enum.auto()
    GET_CONNECTION_STATE = enum.auto()

    HUB_REBOOT = enum.auto()
    HUB_SYNC = enum.auto()
    HUB_START_PROGRAM = enum.auto()
    HUB_STOP_PROGRAM = enum.auto()


class Success(enum.Enum):
    OK = enum.auto()
    FAILED = enum.auto()


class TaskManager(enum.Enum):
    STARTED = enum.auto()
    SET_MAX = enum.auto()
    SET_PROG = enum.auto()
    FINISHED = enum.auto()
    FAILED = enum.auto()
    DONE = enum.auto()


class ConnectionState(enum.Enum):
    DISCONNECTED = enum.auto()
    CONNECTING = enum.auto()
    CONNECTED = enum.auto()
    DISCONNECTING = enum.auto()
    INVALID = enum.auto()


def read_into[E: enum.Enum](byte: int | bytes, enum_class: type[E]) -> E:
    if isinstance(byte, bytes):
        assert len(byte) == 1
        byte = byte[0]
    return enum_class(byte)
