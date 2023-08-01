import select
import socket
import time
import threading

import src.mastermind._mm_netutil as netutil
from src.mastermind._mm_constants import MM_TCP, MM_UDP, MM_UNKNOWN
from src.mastermind._mm_errors import (
    MastermindErrorServer,
    MastermindWarningServer,
    MastermindErrorSocket,
)

class MastermindServerBase(object):
    def __init__(
        self,
        connection_type,
        time_server_refresh,
        time_connection_refresh,
        time_connection_timeout,
    ):
        if connection_type not in [MM_TCP, MM_UDP]:
            raise MastermindErrorServer("Server type must be either MM_TCP or MM_UDP!")
        self._mm_connection_type = connection_type

        self._mm_ip = MM_UNKNOWN
        self._mm_port = MM_UNKNOWN

        self._mm_time_server_refresh = time_server_refresh
        self._mm_time_connection_refresh = time_connection_refresh
        self._mm_time_connection_timeout = time_connection_timeout
        self._mm_connections = {}

        self._mm_accepting_new_connections = False
        self._mm_should_run = False
        self._mm_connected = False

    def __del__(self):
        if self._mm_accepting_new_connections:
            MastermindWarningServer(
                "For a server, .accepting_disallow() was not called before destruction!  Calling automatically."
            )
            self.accepting_disallow()
        if len(self._mm_connections) != 0:
            MastermindWarningServer(
                "For a server, there are still active connections at the time of destruction.  Automatically calling .disconnect_clients()."
            )
            self.disconnect_clients()
        if self._mm_connected:
            MastermindWarningServer(
                "For a server, .disconnect() was not called before destruction!  Calling automatically."
            )
            self.disconnect()

    def connect(self, ip, port):
        if self._mm_connected:
            MastermindWarningServer(
                "Server is already connected!  Ignoring .connect(...)."
            )
            return

        self._mm_make_connection(ip, port)

        self._mm_ip = ip
        self._mm_port = port

        self.callback_connect()

        self._mm_connected = True

    def disconnect(self):
        if not self._mm_connected:
            MastermindWarningServer(
                "Server is already disconnected!  Ignoring .disconnect()."
            )
            return
        if self._mm_accepting_new_connections:
            MastermindWarningServer(
                "Server disconnecting, but still accepting new connections!  Automatically calling .accepting_disallow()."
            )
            self.accepting_disallow()
        if len(self._mm_connections) != 0:
            MastermindWarningServer(
                "Server disconnecting, but has clients!  Automatically calling .disconnect_clients()."
            )
            self.disconnect_clients()

        self._mm_close_connection()

        self._mm_ip = MM_UNKNOWN
        self._mm_port = MM_UNKNOWN

        self.callback_disconnect()

        self._mm_connected = False

    def disconnect_clients(self):
        for connection in self._mm_connections.values():
            connection.terminate()
        for connection in self._mm_connections.values():
            connection.thread.join()
        self._mm_connections = {}

    def callback_connect(self):
        pass  # Called when the server connects                           CAN OVERRIDE

    def callback_disconnect(self):
        pass  # Called when the server disconnects                        CAN OVERRIDE

    def callback_connect_client(self, connection_object):
        pass  # Called when a new client connects                         CAN OVERRIDE

    def callback_disconnect_client(self, connection_object):
        pass  # Called when a client disconnects                          CAN OVERRIDE

    def callback_client_receive(self, connection_object):
        pass  # Called when data is about to be received from a client    CAN OVERRIDE      IF super() CALLED    (defined below)

    def callback_client_handle(self, connection_object, data):
        pass  # Called to handle a client's received data                 SHOULD OVERRIDE

    def callback_client_send(
        self, connection_object, data, compression=None):
        result = netutil.packet_send(
            connection_object.socket,
            (self._mm_connection_type, connection_object.address),
            data,
            compression,
        )
        if not result:
            connection_object.terminate()
        return result

    def accepting_allow(self):
        # Start a thread with the server.  That thread will then start a new thread for each new request
        self._mm_server_thread = threading.Thread(
            target=self.accepting_allow_wait_forever
        )
        self._mm_server_thread.start()
        while not self._mm_should_run:
            pass
        self._mm_accepting_new_connections = True

    def accepting_disallow(self):
        self._mm_should_run = False
        self._mm_server_thread.join()
        self._mm_accepting_new_connections = False


class MastermindServerTCP(MastermindServerBase):
    def __init__(
        self,
        time_server_refresh=0.5,
        time_connection_refresh=0.5,
        time_connection_timeout=5.0,
    ):
        MastermindServerBase.__init__(
            self,
            MM_TCP,
            time_server_refresh,
            time_connection_refresh,
            time_connection_timeout,
        )

    def _mm_make_connection(self, ip, port):
        self._mm_unconnected_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._mm_unconnected_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )
        self._mm_unconnected_socket.setsockopt(
            socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1
        )
        self._mm_unconnected_socket.setsockopt(
            socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 2 * 60
        )
        self._mm_unconnected_socket.setsockopt(
            socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3
        )
        try:
            self._mm_unconnected_socket.bind((ip, port))
            self._mm_unconnected_socket.listen(5)  # 5 is the maximum backlog allowed
        except:
            self._mm_unconnected_socket.close()
            raise MastermindErrorSocket(
                "Server could not connect on port "
                + str(port)
                + "!  Perhaps another instance is already running?"
            )

    def _mm_close_connection(self):
        # self._mm_unconnected_socket.shutdown(socket.SHUT_RD) # this line breaks windows on shutdown. is it needed?
        self._mm_unconnected_socket.close()

    def callback_client_receive(self, connection_object):
        return netutil.packet_recv_tcp(connection_object.socket)

    def accepting_allow_wait_forever(self):
        self._mm_should_run = True
        while self._mm_should_run:
            input_ready, output_ready, except_ready = select.select(
                [self._mm_unconnected_socket], [], [], self._mm_time_server_refresh
            )
            if input_ready == []:
                continue

            connected_socket, address = self._mm_unconnected_socket.accept()
            connection = MastermindConnectionThreadTCP(self, connected_socket, address)
            connection.thread = threading.Thread(
                target=connection.run_forever, name="TCPClientThread-{}".format(address)
            )
            connection.thread.start()
            while not connection.handling:
                pass
            self._mm_connections[address] = connection


class MastermindConnectionThread(object):
    def __init__(self, server, socket, address):
        self.server = server
        self.socket = socket
        self.address = address
        self.amount_waiting = 0.0
        self.handling = False

    def terminate(self):
        self.handling = False


class MastermindConnectionThreadTCP(MastermindConnectionThread):
    def __init__(self, server, socket, address):
        MastermindConnectionThread.__init__(self, server, socket, address)

    def run_forever(self):
        self.server.callback_connect_client(self)

        self.handling = True
        while self.handling:
            input_ready, output_ready, except_ready = select.select(
                [self.socket], [], [], self.server._mm_time_connection_refresh
            )
            if input_ready == []:
                self.amount_waiting += self.server._mm_time_connection_refresh
                if self.amount_waiting > self.server._mm_time_connection_timeout:
                    break
                continue

            try:
                data, status = self.server.callback_client_receive(self)
                if status == False:
                    break
            except:
                return

            self.server.callback_client_handle(self, data)

            self.amount_waiting = 0.0
        self.server.callback_disconnect_client(self)

