

# a position. to get the chunk we are in it's for example: Position(162, 164, 0)
# it returns the modulous of the chunk size so 162 % is worldmap[10][10] remainder
# 2 and 4 or (worldmap[10][10].pos.x + 2 and .pos.y + 4)
class Position(dict):
    # that way Positions are related to worldmap and not individual chunks.
    def __init__(self, x, y, z):
        self['x'] = int(x)
        self['y'] = int(y)
        self['z'] = int(z)
        # self['previous'] = None # used for pathfinding.

    def __eq__(self, position):  # required to be hashable.
        if(position['x'] == self['x']):
            if(position['y'] == self['y']):
                if(position['z'] == self['z']):
                    return True
        return False

    # def asdict(self):
    #    return {'x': self.x, 'y': self.y, 'z': self.z}

    # def __str__(self):
    #    return '(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'
