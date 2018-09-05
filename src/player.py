from profession import Profession
from creature import Creature
#from .position import *

class Player(Creature):
    def __init__(self, name='John Doe'):
        Creature.__init__(self)
        self.name = name
        self.style_selected = None
        self.profession = Profession('Survivor')
        for bodyPart in self.body_parts:
            print(bodyPart)

        #TODO: need to figure out a system for starting equipment. (By profession probably.)
