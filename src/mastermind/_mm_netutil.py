import json

from src.mastermind._mm_constants import MM_MAX_PAYLOAD_SIZE


def packet_send(sock, protocol_and_udpaddress, data, compression):  # E.g.: =(MM_TCP,None)

    # print(data_str.encode('ascii'))
    # data = data + '\r\n'

    try:
        sock.send(data.encode('ascii'))
        return True
    except:
        sock.close()  # client closed the connection without telling us.
        return


def packet_recv_tcp(sock):
    try:
        data_str = sock.recv(MM_MAX_PAYLOAD_SIZE)
    except:
        sock.close()  # client closed the connection without telling us.
        return

    # moving to a client-less system.
    data_str = data_str.decode("utf-8").rstrip()

    return str(data_str), True
