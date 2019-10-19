from collections import defaultdict
import json
import os
import sys
from src.creature import Creature


class Monster(Creature):
    def __init__(self):
        Creature.__init__(self)
        

class MonsterManager:
    def __init__(self):
        self.MONSTER_TYPES = defaultdict(dict)
        for root, dirs, files in os.walk('./data/json/monsters/'):
            for file_data in files:
                if file_data.endswith('.json'):
                    # load tile config so we know what tile foes with what ident
                    with open(f"{root}/{file_data}", encoding='utf-8') as data_file:
                        data = json.load(data_file)
                    for item in data:
                        try:
                            for key, value in item.items():
                                if isinstance(value, list):
                                    self.MONSTER_TYPES[item['ident']][key] = list()
                                    for add_value in value:
                                        self.MONSTER_TYPES[item['ident']][key].append(str(add_value))
                                else:
                                    self.MONSTER_TYPES[item['ident']][key] = str(value)
                        except Exception:
                            raise Exception(f"!! couldn't parse: {item}.")
        print(f'Total MONSTER_TYPES loaded: {len(self.MONSTER_TYPES)}')
