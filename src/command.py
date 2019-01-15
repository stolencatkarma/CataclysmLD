class Command(dict):
    """A client to server command"""

    __slots__ = 'ident', 'command', 'args'

    def __init__(self, ident, command, args):
        super().__init__()
        self['ident'] = ident
        self['command'] = command
        self['args'] = args
