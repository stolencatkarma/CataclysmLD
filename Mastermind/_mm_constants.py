MM_TCP = 1
MM_UDP = 2

MM_UNKNOWN = -1

MM_MAX = -2 #Cannot be in [0,9] because these are already valid arguments for compression.

# Maximum payload to attempt to extract from the stream. This serves as minor DOS protection
MM_MAX_PAYLOAD_SIZE = 65535

# Minimum payload size to consider compression. Otherwise the payload may result in a net loss.
MM_MIN_PAYLOAD_COMPRESSION_SIZE = 128
