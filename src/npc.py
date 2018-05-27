# defines a A.I. controlled Creature. They should have their own personal goals as well as faction goals.
# factions will have a 'manager' NPC who decides how forts will be setup and hands outs jobs to npcs or players.
# forts are mini-cities that get built over time by factions.

class Npc(Creature):
    def __init__(self):
        Creature.__init__(self)
        self.wanted_item_pos = None # Position(x,y,z)
        self.guard_pos = None
        self.goal = None
        self.fetching_item = False
        self.my_fac = None
        self.fac_id = None
        self.miss_id = mission_type_id.NULL_ID()
        self.marked_for_death = False
        self.dead = False
        self.hit_by_player = False
        self.mission = NPC_MISSION_NULL
        self.myclass = npc_class_id.NULL_ID()
        self.companion_mission = ""
        self.companion_mission_time = 0
        self.last_updated = calendar.turn
        self.path_settings = pathfinding_settings( 0, 1000, 1000, 10, True, True, True )
