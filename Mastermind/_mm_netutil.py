import json
import zlib
import struct

from Mastermind._mm_constants import MM_MAX, MM_TCP, MM_MAX_PAYLOAD_SIZE, MM_MIN_PAYLOAD_COMPRESSION_SIZE

def packet_send(sock, protocol_and_udpaddress, data, compression): #E.g.: =(MM_TCP,None)
    if   compression ==  False: compression = 0
    elif compression ==   None: compression = 0
    elif compression ==   True: compression = 9
    elif compression == MM_MAX: compression = 9
    elif compression >       9: compression = 9

    # Convert to JSON and get length
    data_str = json.dumps(data)
    length = len(data_str)

    # Enable compression as required and satisfies criteria
    if compression > 0 and length >= MM_MIN_PAYLOAD_COMPRESSION_SIZE:
        data_str = struct.pack( '!b', compression ) + zlib.compress(data_str.encode())
    else:
        data_str = struct.pack( '!b', 0 ) + data_str.encode()

    # Binary encode the length prefix in network byte order - allowing for universal length decode
    length = len(data_str)
    data_to_send = struct.pack('!I', length) + data_str

    print(data_to_send)

    try:
        if protocol_and_udpaddress[0] == MM_TCP:
            sock.send(data_to_send)
        else:
            if protocol_and_udpaddress[1] == None:
                sock.send(data_to_send)
            else:
                sock.sendto(data_to_send, protocol_and_udpaddress[1])
        return True

    except:
        return False


def packet_recv_tcp(sock):
    #TODO: In all this, if recv returns 0, then shutdown *nicely*
    info = b""
    length_prefix_size = struct.calcsize('!I')
    try:
        while( len(info) ) < length_prefix_size:
            got = sock.recv( length_prefix_size )
            if got == b"": return (None,False)
            info += got

    except:
        return (None,False)

    if info == "": return (None,False)
    length = int(struct.unpack('!I', info[:length_prefix_size])[0])

    # Make sure we don't have a massive payload size provided to defend
    # against potential DOS attempt. This may result in stream desync
    # but it should never happen without a bug or malicous payload
    if length > MM_MAX_PAYLOAD_SIZE:
        return (None, False)

    data_str = b""
    try:
        while len(data_str) < length:
            got = sock.recv(length - len(data_str))
            if got == b"": return (None,False)
            data_str += got
    except:
        return (None,False)

    # Get our compression level and skip past it to the first data byte
    compression = int(struct.unpack( '!b', data_str[:1] )[0])
    data_str = data_str[1:]

    if compression != 0:
        data_str = zlib.decompress(data_str)

    data = json.loads(data_str)

    return (data, True)
