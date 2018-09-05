import sys

from .furniture import Furniture
from .item import Container, Item
from .terrain import Terrain


class Blueprint(Container): # is a physical representation of a recipe while it's being built in the world. # once built it 'turns' into the type and fills the worldmap with it.
    def __init__(self, type_of, recipe):
        Container.__init__(self, 'Blueprint')
        valid_types = ['Terrain', 'Furniture', 'Item']
        self.recipe = recipe
        self.turns_worked_on = 0 # when this reaches self.recipe['time'] then we need to 'turn' it into the object.

        if(str(type_of) not in valid_types):
            self.type_of = None
            print()
            print('!!! COULDN\'T set type. Invalid')
            print(str(type_of))
            print()
            sys.exit()
        else:
            print('set type')
            self.type_of = type_of

    def __str__(self):
        return self.ident

    def work_on(self):
        # when a creature 'works on' this blueprint
        # first check if the required materials are present.
        # do we have a threshold for removing materials or create a list from the materials once we start and remove 1 every so often?
        #  e.g. recipe has 5 materials and takes 10 turns, remove 1 material every 2 turns. (self.turns_worked_on / int(self.recipe['time']))

        # recipes have OR and AND components. how do we handle that?
        pass
