import time
from socket import *
from threading import Thread, Lock
from typing import Final

from ServerProtocol import *


class ObserverClient(object):
    def __init__(self):
        # constants
        self.SERVER_IP: Final = '127.0.0.1'
        self.EYE_IMAGE_DELAY: Final = 5000  # quantum of time. Eye inertia
        self.STATISTIC_REQUEST_PERIOD: Final = 900  # milliseconds

        # vars
        self.isSimulationRunning = False
        self.addr = None
        self.mainThread = Thread(target=self.thread_cycle)
        self.timeOfTheUniverse = 0
        self.lastUpdateStateExtTime = 0
        self.lastStatisticRequestTime = 0
        self.eyeTextureMutex = Lock()
        self.observerStateParamsMutex = Lock()
        self.position = VectorInt32Math.ZeroVector()
        self.movingProgress = 0
        self.latitude = 0
        self.longitude = 0
        self.isEatenCrumb = False
        self.eatenCrumbNum = 0
        self.eatenCrumbPos = VectorInt32Math.ZeroVector()
        self.isLeft = self.isRight = self.isUp = self.isDown = self.isForward = self.isBackward = 0
        # statistics
        self.serverStatisticsMutex = Lock()
        self.quantumOfTimePerSecond = 0
        self.universeThreadsNum = 0
        self.tickTimeMusAverageUniverseThreadsMin = 0
        self.tickTimeMusAverageUniverseThreadsMax = 0
        self.tickTimeMusAverageObserverThread = 0
        self.clientServerPerformanceRatio = 0
        self.serverClientPerformanceRatio = 0
        # init eye color array
        self.eyeColorArray = []
        self.eyeUpdateTimeArray = []
        for i in range(CommonParams.OBSERVER_EYE_SIZE):
            row_color = []
            row_time = []
            for j in range(CommonParams.OBSERVER_EYE_SIZE):
                row_color.append(EtherColor(0, 0, 0))
                row_time.append(0)
            self.eyeColorArray.append(row_color)
            self.eyeUpdateTimeArray.append(row_time)
        # Create a UDP socket
        self.client_socket = socket(AF_INET, SOCK_DGRAM)

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ObserverClient, cls).__new__(cls)
        return cls.instance

    def get_state_ext_params(self):
        with self.observerStateParamsMutex:
            return self.position, self.movingProgress, self.latitude, self.longitude, self.isEatenCrumb

    def get_statistics_params(self):
        with self.serverStatisticsMutex:
            return self.quantumOfTimePerSecond, self.universeThreadsNum, self.tickTimeMusAverageUniverseThreadsMin,\
                   self.tickTimeMusAverageUniverseThreadsMax, self.tickTimeMusAverageObserverThread,\
                   self.clientServerPerformanceRatio, self.serverClientPerformanceRatio

    def grab_eaten_crumb_pos(self):
        with self.observerStateParamsMutex:
            if self.isEatenCrumb:
                self.isEatenCrumb = False
                return self.eatenCrumbPos

    def start_simulation(self):
        self.isSimulationRunning = True
        # Set a timeout value of 1 second
        self.client_socket.settimeout(1)

        for port in range(CommonParams.CLIENT_UDP_PORT_START,
                          CommonParams.CLIENT_UDP_PORT_START + CommonParams.MAX_CLIENTS):
            self.client_socket.setblocking(True)

            self.addr = (self.SERVER_IP, port)
            message = MsgCheckVersion()
            message.m_clientVersion = CommonParams.PROTOCOL_VERSION
            message.m_observerId = 0
            # Send
            self.client_socket.sendto(message.get_buffer(), self.addr)

            # If data is received back from server, print
            try:
                data = self.client_socket.recv(CommonParams.DEFAULT_BUFLEN)
                if data[0] == MsgType.CheckVersionResponse:
                    received_array = bytearray(data)
                    msg_receive = MsgCheckVersionResponse.from_buffer(received_array)
                    if msg_receive.m_serverVersion == CommonParams.PROTOCOL_VERSION:
                        break
                    else:
                        print('Wrong protocol')
                        self.addr = None
                        break

            except timeout:
                print('REQUEST TIMED OUT')
                self.addr = None

        if self.addr is not None:
            self.client_socket.setblocking(False)
            self.mainThread.start()

        return

    def stop_simulation(self):
        if self.isSimulationRunning:
            self.isSimulationRunning = False
            self.mainThread.join()

    def set_is_left(self, value):
        self.isLeft = value

    def set_is_right(self, value):
        self.isRight = value

    def set_is_up(self, value):
        self.isUp = value

    def set_is_down(self, value):
        self.isDown = value

    def set_is_forward(self, value):
        self.isForward = value

    def set_is_backward(self, value):
        self.isBackward = value

    def get_eye_texture(self):
        eye_color_array = []
        eye_update_time_array = []
        with self.eyeTextureMutex:
            eye_color_array = self.eyeColorArray
            eye_update_time_array = self.eyeUpdateTimeArray
        for xx in range(CommonParams.OBSERVER_EYE_SIZE):
            for yy in range(CommonParams.OBSERVER_EYE_SIZE):
                time_diff = self.timeOfTheUniverse - eye_update_time_array[yy][xx]
                alpha = self.eyeColorArray[yy][xx].m_colorA
                if time_diff < self.EYE_IMAGE_DELAY:
                    alpha = int((alpha * (self.EYE_IMAGE_DELAY - time_diff) / self.EYE_IMAGE_DELAY))
                else:
                    alpha = 0
                eye_color_array[yy][xx].m_colorA = alpha
        return eye_color_array

    @staticmethod
    def get_time_ms():
        return time.time_ns() // 1000000

    def thread_cycle(self):
        while self.isSimulationRunning:
            self.pph_tick()

    def pph_tick(self):
        # Send
        # State and StateExt
        message = MsgGetState()
        self.client_socket.sendto(message.get_buffer(), self.addr)
        if self.get_time_ms() - self.lastUpdateStateExtTime > 20:  # get position / orientation data every n milliseconds
            self.lastUpdateStateExtTime = self.get_time_ms()
            message = MsgGetStateExt()
            self.client_socket.sendto(message.get_buffer(), self.addr)
        # statistics
        if self.get_time_ms() - self.lastStatisticRequestTime > self.STATISTIC_REQUEST_PERIOD:
            self.lastStatisticRequestTime = self.get_time_ms()
            message = MsgGetStatistics()
            self.client_socket.sendto(message.get_buffer(), self.addr)
        # motor neurons
        if self.isLeft:
            message = MsgRotateLeft()
            message.m_value = 4
            self.client_socket.sendto(message.get_buffer(), self.addr)
        if self.isRight:
            message = MsgRotateRight()
            message.m_value = 4
            self.client_socket.sendto(message.get_buffer(), self.addr)
        if self.isUp:
            message = MsgRotateDown()
            message.m_value = 4
            self.client_socket.sendto(message.get_buffer(), self.addr)
        if self.isDown:
            message = MsgRotateUp()
            message.m_value = 4
            self.client_socket.sendto(message.get_buffer(), self.addr)
        if self.isForward:
            message = MsgMoveForward()
            message.m_value = 16
            self.client_socket.sendto(message.get_buffer(), self.addr)
        if self.isBackward:
            message = MsgMoveBackward()
            message.m_value = 16
            self.client_socket.sendto(message.get_buffer(), self.addr)
        # Receive
        while True:
            try:
                data = self.client_socket.recv(CommonParams.DEFAULT_BUFLEN)
                if len(data) == 0:
                    break
                buf = bytearray(data)
                # State and StateExt
                if data[0] == MsgType.GetStateResponse:
                    msg = MsgGetStateResponse.from_buffer(buf)
                    self.timeOfTheUniverse = msg.m_time
                elif data[0] == MsgType.GetStateExtResponse:
                    msg = MsgGetStateExtResponse.from_buffer(buf)
                    with self.observerStateParamsMutex:
                        self.latitude = msg.m_latitude
                        self.longitude = msg.m_longitude
                        self.position = msg.m_pos
                        self.movingProgress = msg.m_movingProgress
                        if self.eatenCrumbNum < msg.m_eatenCrumbNum:
                            self.eatenCrumbNum = msg.m_eatenCrumbNum
                            self.eatenCrumbPos = msg.m_eatenCrumbPos
                            self.isEatenCrumb = True
                # photons received
                elif data[0] == MsgType.SendPhoton:
                    msg = MsgSendPhoton.from_buffer(buf)
                    with self.eyeTextureMutex:
                        self.eyeColorArray[CommonParams.OBSERVER_EYE_SIZE - msg.m_posY - 1][msg.m_posX] = msg.m_color
                        self.eyeUpdateTimeArray[CommonParams.OBSERVER_EYE_SIZE - msg.m_posY - 1][
                            msg.m_posX] = self.timeOfTheUniverse
                # statistics
                elif data[0] == MsgType.GetStatisticsResponse:
                    msg = MsgGetStatisticsResponse.from_buffer(buf)
                    with self.serverStatisticsMutex:
                        self.quantumOfTimePerSecond = msg.m_fps
                        self.tickTimeMusAverageObserverThread = msg.m_observerThreadTickTime
                        self.tickTimeMusAverageUniverseThreadsMin = msg.m_universeThreadMinTickTime
                        self.tickTimeMusAverageUniverseThreadsMax = msg.m_universeThreadMaxTickTime
                        self.universeThreadsNum = msg.m_universeThreadsCount
                        self.clientServerPerformanceRatio = msg.m_clientServerPerformanceRatio
                        self.serverClientPerformanceRatio = msg.m_serverClientPerformanceRatio
            except BlockingIOError:
                break


g_observer_client = ObserverClient()
