from .creature import Creature

class Monster(Creature):
    def __init__(self):
        Creature.__init__(self)
        self.hp = 1
        self.friendly = 0
        self.anger = 0
        self.morale = 2
        self.faction = None
        self.mission_id = None
        self.no_extra_death_drops = False
        self.dead = False
        self.made_footstep = False
        self.unique_name = ""
        self.hallucination = False
        self.ignoring = 0
        self.upgrades = False
        self.upgrade_time = -1
        self.last_updated = 0

        self.speed = 1
