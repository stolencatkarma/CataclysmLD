from .profession import Profession
from .creature import Creature
import pprint
#from .position import *

class Player(Creature):
    def __init__(self, name='John Doe'):
        Creature.__init__(self)
        self.name = name
        self.style_selected = None
        self.profession = Profession('survivor')
        for bodyPart in self.body_parts:
            print(bodyPart)

        print(self.profession)
    
    def __str__(self):
        return self.name + ' the ' + str(self.profession)
