from enum import Enum, auto


class Direction(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()
    UP = auto()
    DOWN = auto()


class Position(dict):
    """A position in a regular 3D Cartesian grid.
    To get the position within chunk we are in, take the modulus of the (x, y) component of the position by the (x, y) dimensions of chunk size.
    For example if the position is (162, 164, 0) and the chunk size so (10, 10), then the position within the chunk is (162 % 10, 164 % 10) = (2, 4)"""

    def __init__(self, x, y, z):
        self['x'] = int(x)
        self['y'] = int(y)
        self['z'] = int(z)
        # self['previous'] = None # used for pathfinding.

    def __eq__(self, position):  # required to be hashable.
        return isinstance(position, Position) \
               and position['x'] == self['x'] \
               and position['y'] == self['y'] \
               and position['z'] == self['z']

    def __str__(self):
        return f"({self['x']}, {self['y']}, {self['z']})"
