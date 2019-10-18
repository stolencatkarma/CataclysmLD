import socket
import select

import src.mastermind._mm_netutil as netutil
from src.mastermind._mm_constants import MM_TCP, MM_UDP, MM_UNKNOWN
from src.mastermind._mm_errors import (
    MastermindErrorClient,
    MastermindWarningClient,
    MastermindErrorSocket,
)


class MastermindClientBase(object):
    def __init__(self, connection_type, timeout_connect, timeout_receive):
        if connection_type not in [MM_TCP, MM_UDP]:
            raise MastermindErrorClient("Client type must be either MM_TCP or MM_UDP!")
        self._mm_connection_type = connection_type
        self._mm_ip = MM_UNKNOWN
        self._mm_port = MM_UNKNOWN
        self._mm_timeout_connect = timeout_connect
        self._mm_timeout_receive = timeout_receive
        self._mm_connected = False

    def __del__(self):
        if self._mm_connected:
            MastermindWarningClient(
                "In a client, .disconnect() was not called before destruction!  Calling automatically."
            )
            self.disconnect()

    def connect(self, ip, port):
        if self._mm_connected:
            MastermindWarningClient(
                "Client is already connected!  Ignoring .connect(...)."
            )
            return
        self._mm_make_connection(ip, port)
        self._mm_ip = ip
        self._mm_port = port
        self._mm_connected = True

    def disconnect(self):
        if not self._mm_connected:
            MastermindWarningClient("Client is already disconnected!")
            return
        self._mm_socket.close()
        self._mm_ip = MM_UNKNOWN
        self._mm_port = MM_UNKNOWN
        self._mm_connected = False

    def send(self, data, compression=None):
        if not self._mm_connected:
            raise MastermindErrorClient(
                "Client must be connected with .connect() to send data!"
            )
        if not netutil.packet_send(
            self._mm_socket, (self._mm_connection_type, None), data, compression
        ):
            raise MastermindErrorClient(
                "Client sending has failed!  Call .disconnect() and then .connect() to try to reestablish the connection."
            )

    def receive(self, blocking=True):
        if not self._mm_connected:
            raise MastermindErrorClient(
                "Client must be connected with .connect() to receive data!"
            )

        if blocking:
            if self._mm_timeout_receive == None:
                input_ready, output_ready, except_ready = select.select(
                    [self._mm_socket], [], []
                )
            else:
                input_ready, output_ready, except_ready = select.select(
                    [self._mm_socket], [], [], self._mm_timeout_receive
                )
                if len(input_ready) == 0:
                    raise MastermindErrorClient(
                        "Client receiving has timed out!  Call .disconnect() and then .connect() to try to reestablish the connection."
                    )
            data, status = self._mm_receive_func()
        else:
            input_ready, output_ready, except_ready = select.select(
                [self._mm_socket], [], [], 0.001
            )
            if len(input_ready) > 0:
                data, status = self._mm_receive_func()
            else:
                return None

        if status == False:
            raise MastermindErrorClient(
                "Client receiving has failed!  Call .disconnect() and then .connect() to try to reestablish the connection."
            )
        else:
            return data


class MastermindClientTCP(MastermindClientBase):
    def __init__(self, timeout_connect=None, timeout_receive=None):
        MastermindClientBase.__init__(self, MM_TCP, timeout_connect, timeout_receive)

    def _mm_make_connection(self, ip, port):
        self._mm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._mm_socket.settimeout(self._mm_timeout_connect)
        try:
            self._mm_socket.connect((ip, port))
        except:
            self._mm_socket.close()
            raise MastermindErrorSocket(
                'A TCP connection to "'
                + ip
                + '" on port '
                + str(port)
                + " could not be established."
            )

    def _mm_receive_func(self):
        data, status = netutil.packet_recv_tcp(self._mm_socket)
        return data, status

