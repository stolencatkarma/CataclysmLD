import json
import jsonpickle


class ChunkEncoder(json.JSONEncoder):
    """Custom simplified class encoder."""
    def default(self, obj):
        return obj.__class__.__name__, obj.__dict__


class ChunkDecoder(json.JSONDecoder):
    def decode(self, s, _w=json.decoder.WHITESPACE.match):
        pass


def encode_packet(*args, **kwargs):
    """Stub for jsonpickle"""
    return jsonpickle.encode(*args, **kwargs)


def decode_packet(*args, **kwargs):
    """Stub for jsonpickle"""
    return jsonpickle.decode(*args, **kwargs)
