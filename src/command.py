# defines a client to server command.
class Command:
    # types of commands 'move',
    def __init__(self, ident, command, args=[]):
        self.ident = ident
        self.command = command
        self.args = args # expects a list e.g Command(player, 'move', ['up'])

    def __str__(self):
        ret = self.ident
        ret = ret + ' : ' + str(self.command)
        for arg in self.args:
            ret = ret + ' : ' + str(arg)
        return ret
