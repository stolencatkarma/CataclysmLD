from profession import *
from creature import *
from position import *

class Player(Creature):
    def __init__(self, name='John Doe'):
        Creature.__init__(self)
        self.name = name
        self.style_selected = None
