import json

from src.mastermind._mm_constants import MM_MAX_PAYLOAD_SIZE


def packet_send(sock, protocol_and_udpaddress, data, compression): #E.g.: =(MM_TCP,None)

    data_str = json.dumps(data)

    #print(data_str.encode('ascii'))
    sock.send(data_str.encode('ascii'))
    return True


def packet_recv_tcp(sock):
    data_str = sock.recv(MM_MAX_PAYLOAD_SIZE)
    # print("RECIEVED:" + str(data_str))
    
    data_str = data_str.decode("utf-8")
    # print('###' + data_str)
    if len(data_str) < 1:
        return 'disconnect', True

    payload_end_index = get_payload_end_index(data_str)
    data = json.loads(data_str[:payload_end_index])
    
    return data, True


def get_payload_end_index(data_str):
    """This fixes the issue where the server will crash if the client sends too many batched requests.  However, this does
    highlight the opportunity for potential code injection."""
    # TODO: Batch requests properly by putting them in a collection rather than concatenating them.

    if data_str[0] is not '{':
        return -1
    bracket_count = 1
    index = 1
    while index < len(data_str) and bracket_count > 0:
        cur_char = data_str[index]
        bracket_count += 1 if cur_char is '{' else -1 if cur_char is '}' else 0
        index += 1
    return index if bracket_count == 0 else -1
