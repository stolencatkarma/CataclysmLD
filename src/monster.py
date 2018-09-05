from collections import defaultdict
import json
import os
import sys
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

class MonsterManager:
    def __init__(self):
        self.MONSTER_TYPES = defaultdict(dict)
        for root, dirs, files in os.walk('./data/json/monsters/'):
            for file_data in files:
                if file_data.endswith('.json'):
                    with open(root+'/'+file_data, encoding='utf-8') as data_file: # load tile config so we know what tile foes with what ident
                        data = json.load(data_file)
                    for item in data:
                        try:
                            for key, value in item.items():
                                if(isinstance(value, list)):
                                    self.MONSTER_TYPES[item['ident']][key] = []
                                    for add_value in value:
                                        self.MONSTER_TYPES[item['ident']][key].append(str(add_value))
                                else:
                                    self.MONSTER_TYPES[item['ident']][key] = str(value)
                        except Exception:
                            print()
                            print('!! couldn\'t parse: ' + str(item) + ' -- likely missing ident.')
                            print()
                            sys.exit()
        print('total MONSTER_TYPES loaded: ' + str(len(self.MONSTER_TYPES)))
