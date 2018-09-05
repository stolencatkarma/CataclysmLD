# defines a A.I. controlled Creature. They should have their own personal goals as well as faction goals.
# factions will have a 'manager' NPC who decides how forts will be setup and hands outs jobs to npcs or players.
# forts are mini-cities that get built over time by factions.
from creature import Creature

class Npc(Creature):
    def __init__(self):
        Creature.__init__(self)
        self.wanted_item_pos = None # Position(x,y,z)
        self.guard_pos = None
        self.goal = None
        self.fetching_item = False
        self.my_fac = None
        self.fac_id = None
        self.miss_id = None
        self.marked_for_death = False
        self.dead = False
        self.mission = None


