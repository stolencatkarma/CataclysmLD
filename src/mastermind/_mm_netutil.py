import json

from src.mastermind._mm_constants import MM_MAX_PAYLOAD_SIZE


def packet_send(sock, protocol_and_udpaddress, data, compression):  # E.g.: =(MM_TCP,None)

    # print(data_str.encode('ascii'))
    # data = data + '\r\n'

    sock.send(data.encode('ascii'))
    return True


def packet_recv_tcp(sock):

    data_str = sock.recv(MM_MAX_PAYLOAD_SIZE)

    # moving to a client-less system.
    data_str = data_str.decode("utf-8").rstrip()
    # if(len(data_str) < 1):
        # client sent blank line
        # return(
    #     return ('disconnect', True)
    # data = json.loads(data_str)
    # print("RECIEVED:" + str(data_str))

    return (str(data_str), True)
