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


class VectorInt32Math(Structure):
    def __init__(self, x_, y_, z_):
        self.m_posX = x_
        self.m_posY = y_
        self.m_posZ = z_

    @staticmethod
    def ZeroVector():
        return VectorInt32Math(0, 0, 0)

    _pack_ = 1
    _fields_ = [
        ('m_posX', c_uint32),
        ('m_posY', c_uint32),
        ('m_posZ', c_uint32)
    ]


class EtherColor(Structure):
    def __init__(self, r_, g_, b_):
        self.m_colorR = r_
        self.m_colorG = g_
        self.m_colorB = b_
        self.m_colorA = 0

    _pack_ = 1
    _fields_ = [
        ('m_colorR', c_uint8),
        ('m_colorG', c_uint8),
        ('m_colorB', c_uint8),
        ('m_colorA', c_uint8),
    ]


class MsgBase(Structure):
    def __init__(self, type_):
        self.m_type = type_

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
        ('m_clientVersion', c_uint32),
        ('m_observerId', c_uint64)  # used to restore connection after restart client. If not need this send 0
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


class MsgGetStateExt(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.GetStateExt

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


class MsgRotateRight(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.RotateRight

    def __init__(self):
        super().__init__(self.get_type())

    _fields_ = [
        ('m_value', c_uint8)
    ]


class MsgRotateUp(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.RotateUp

    def __init__(self):
        super().__init__(self.get_type())

    _fields_ = [
        ('m_value', c_uint8)
    ]


class MsgRotateDown(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.RotateDown

    def __init__(self):
        super().__init__(self.get_type())

    _fields_ = [
        ('m_value', c_uint8)
    ]


class MsgMoveForward(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.MoveForward

    def __init__(self):
        super().__init__(self.get_type())

    _fields_ = [
        ('m_value', c_uint8)
    ]


class MsgMoveBackward(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.MoveBackward

    def __init__(self):
        super().__init__(self.get_type())

    _fields_ = [
        ('m_value', c_uint8)
    ]


# **************************************************************************************
# ************************************** Server ****************************************
# **************************************************************************************
class MsgCheckVersionResponse(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.CheckVersionResponse

    def __init__(self):
        super().__init__(self.get_type())

    _fields_ = [
        ('m_serverVersion', c_uint32),
        ('m_observerId', c_uint64)
    ]


class MsgSocketBusyByAnotherObserver(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.SocketBusyByAnotherObserver

    def __init__(self):
        super().__init__(self.get_type())

    _fields_ = [
        ('m_serverVersion', c_uint32)
    ]


class MsgGetStatisticsResponse(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.GetStatisticsResponse

    def __init__(self):
        super().__init__(self.get_type())

    _fields_ = [
        ('m_universeThreadsCount', c_uint16),
        ('m_fps', c_uint32),  # quantum of time per second
        ('m_observerThreadTickTime', c_uint32),
        ('m_universeThreadMaxTickTime', c_uint32),
        ('m_universeThreadMinTickTime', c_uint32),
        ('m_clientServerPerformanceRatio', c_uint32),
        ('m_serverClientPerformanceRatio', c_uint32)
    ]


class MsgGetStateResponse(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.GetStateResponse

    def __init__(self):
        super().__init__(self.get_type())

    _fields_ = [
        ('m_time', c_uint64)
    ]


class MsgGetStateExtResponse(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.GetStateExtResponse

    def __init__(self):
        super().__init__(self.get_type())

    _fields_ = [
        ('m_pos', VectorInt32Math),
        ('m_movingProgress', c_uint16),
        ('m_latitude', c_int16),
        ('m_longitude', c_int16),
        ('m_eatenCrumbNum', c_uint32),
        ('m_eatenCrumbPos', VectorInt32Math),
    ]


class MsgSendPhoton(MsgBase):
    @staticmethod
    def get_type():
        return MsgType.SendPhoton

    def __init__(self):
        super().__init__(self.get_type())

    _fields_ = [
        ('m_color', EtherColor),
        ('m_posX', c_uint8),
        ('m_posY', c_uint8)
    ]
