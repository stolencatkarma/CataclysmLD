class Command:
    """A client to server command."""

    def __init__(self, ident, command_name, source_address, args):
        self.ident = ident
        self.command_name = command_name
        self.source_address = source_address
        self.args = args
