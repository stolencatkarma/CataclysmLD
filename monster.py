from creature import Creature

class Monster(Creature):
    def __init__(self):
        Creature.__init__(self)
        self.wandf = 0
        self.hp = hp
        self.friendly = 0
        self.anger = 0
        self.morale = 2
        self.faction = mfaction_id( 0 )
        self.mission_id = -1
        self.no_extra_death_drops = False
        self.dead = False
        self.made_footstep = False
        self.unique_name = ""
        self.hallucination = False
        self.ignoring = 0
        self.upgrades = False
        self.upgrade_time = -1
        self.last_updated = 0

        type = id.obj()
        self.moves = self.speed
        Creature.set_speed_base(self.speed)
        hp = self.hp
        for sa in self.special_attacks:
            entry = special_attacks[sa.first]
            entry.cooldown = sa.second.cooldown
