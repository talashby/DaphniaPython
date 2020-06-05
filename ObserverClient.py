import time
from socket import *
from threading import Thread, Lock
from typing import Final

from ServerProtocol import *


class ObserverClient(object):
    def __init__(self):
        # constants
        self.SERVER_IP: Final = '127.0.0.1'
        self.addr: Final = None
        self.EYE_IMAGE_DELAY: Final = 5000 # quantum of time. Eye inertia
        self.STATISTIC_REQUEST_PERIOD: Final = 900 # milliseconds

        # vars
        self.isSimulationRunning = False
        self.timeOfTheUniverse = 0
        self.eyeTextureMutex = Lock()
        self.isLeft = self.isRight = self.isUp = self.isDown = self.isForward = self.isBackward = 0
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
            t = Thread(target=self.thread_cycle)
            t.start()

        return

    def stop_simulation(self):
        if self.isSimulationRunning:
            # TODO stop thread
            pass

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
        message = MsgGetState()
        self.client_socket.sendto(message.get_buffer(), self.addr)
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
        # receive
        while True:
            try:
                data = self.client_socket.recv(CommonParams.DEFAULT_BUFLEN)
                if len(data) == 0:
                    break
                buf = bytearray(data)
                if data[0] == MsgType.GetStateResponse:
                    msg = MsgGetStateResponse.from_buffer(buf)
                    self.timeOfTheUniverse = msg.m_time
                elif data[0] == MsgType.SendPhoton:
                    msg = MsgSendPhoton.from_buffer(buf)
                    with self.eyeTextureMutex:
                        self.eyeColorArray[CommonParams.OBSERVER_EYE_SIZE - msg.m_posY - 1][msg.m_posX] = msg.m_color
                        self.eyeUpdateTimeArray[CommonParams.OBSERVER_EYE_SIZE - msg.m_posY - 1][
                            msg.m_posX] = self.timeOfTheUniverse
            except BlockingIOError:
                break


g_observer_client = ObserverClient()

