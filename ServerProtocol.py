from typing import Final
from ctypes import *


class CommonParams:
    MY_CONSTANT: Final = 12407

    PROTOCOL_VERSION: Final = 1
    DEFAULT_BUFLEN: Final = 512
    CLIENT_UDP_PORT_START: Final = 50000
    MAX_CLIENTS: Final = 10
    OBSERVER_EYE_SIZE: Final = 16  # pixels


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


# Animal = enum('ant', 'bee', 'cat', 'dog')

MsgType = enum('CheckVersion',
               'GetStatistics',
               'GetState',
               'GetStateExt',
               'RotateLeft',
               'RotateRight',
               'RotateUp',
               'RotateDown',
               'MoveForward',
               'MoveBackward',
               'ClientToServerEnd',  # !!!Always last
               'CheckVersionResponse',
               'SocketBusyByAnotherObserver',
               'GetStatisticsResponse',
               'GetStateResponse',
               'GetStateExtResponse',
               'SendPhoton',
               'ToAdminSomeObserverPosChanged'
               )


class MsgBase(Structure):
    def __init__(self, my_type):
        self.m_type = my_type

    def get_buffer(self):
        return bytearray(self)

    _pack_ = 1
    _fields_ = [
        ('m_type', c_uint8)]


# **************************************************************************************
# ************************************** Client ****************************************
# **************************************************************************************
class MsgCheckVersion(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.CheckVersion

    def __init__(self):
        super().__init__(self.get_type())

    _fields_ = [
        ('m_client_version', c_uint32),
        ('m_observer_id', c_uint64)
    ]


class MsgGetStatistics(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.GetStatistics

    def __init__(self):
        super().__init__(self.get_type())


class MsgGetState(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.GetState

    def __init__(self):
        super().__init__(self.get_type())


class MsgGetStateEx(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.GetStateEx

    def __init__(self):
        super().__init__(self.get_type())


class MsgRotateLeft(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.RotateLeft

    def __init__(self):
        super().__init__(self.get_type())

    _fields_ = [
        ('m_value', c_uint8)
    ]