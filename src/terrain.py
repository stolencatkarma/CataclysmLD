
class Terrain:
    def __init__(self, ident, impassable=False):
        self.ident = ident
        self.impassable = impassable

    def __str__(self):
        return str(self.ident)