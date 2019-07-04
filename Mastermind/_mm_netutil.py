import json
import zlib
import struct

from Mastermind._mm_constants import MM_MAX, MM_TCP, MM_MAX_PAYLOAD_SIZE, MM_MIN_PAYLOAD_COMPRESSION_SIZE

def packet_send(sock, protocol_and_udpaddress, data, compression): #E.g.: =(MM_TCP,None)

    # Convert to JSON and get length
    data_str = json.dumps(data)
    length = len(data_str)
    data_str = data_str + '\r\n'

    #print(data_str.encode('ascii'))
    sock.send(data_str.encode('ascii'))
    return True



def packet_recv_tcp(sock):
    
    data_str = sock.recv(MM_MAX_PAYLOAD_SIZE)
    
    print("RECIEVED:" + str(data_str))
    data = json.loads(data_str.decode("utf-8"))
    
    return (data, True)
