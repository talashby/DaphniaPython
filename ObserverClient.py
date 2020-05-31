import time
from socket import *
from typing import Final

from ServerProtocol import *


class ObserverClient(object):
    def __init__(self):
        # constants
        self.SERVER_IP: Final = '127.0.0.1'
        # vars
        self.m_is_simulation_running = False


    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ObserverClient, cls).__new__(cls)
        return cls.instance

    def start_simulation(self):
        self.m_is_simulation_running = True

        for port in range(CommonParams.CLIENT_UDP_PORT_START, CommonParams.CLIENT_UDP_PORT_START+CommonParams.MAX_CLIENTS):
            # Create a UDP socket
            client_socket = socket(AF_INET, SOCK_DGRAM)
            # Set a timeout value of 1 second
            client_socket.settimeout(1)
            # Ping to server
            addr = (self.SERVER_IP, port)
            message = MsgCheckVersion()
            message.m_client_version = CommonParams.PROTOCOL_VERSION
            message.m_observer_id = id(self)
            arr = message.get_buffer()
            message2 = MsgCheckVersion.unpack(arr)
            # Send
            client_socket.sendto(arr, addr)

            # If data is received back from server, print
            try:
                start = time.time()
                data, server = client_socket.recvfrom(1024)
                end = time.time()
                elapsed = end - start
                print(data + " " + elapsed)
                # If data is not received back from server, print it has timed out
            except timeout:
                print('REQUEST TIMED OUT')
        return


g_observer_client = ObserverClient()

# print("Object created", s)
# s1 = ObserverClient()
# print("Object created", s1)
# ObserverClient().start_simulation()
