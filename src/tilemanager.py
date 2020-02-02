import json
from collections import defaultdict


# holds all the tile types from tile_config.json as well as terrain.json information
# because terrain can have a fg and bg
class TileManager:
    def __init__(self):
        # the dict of tiles loaded from the tile_config.json
        self.TILE_TYPES = defaultdict(dict)
        # load terrain data.
        with open('./data/json/terrain.json') as data_file:
            data = json.load(data_file)
        for terrain in data:
            if('name' not in terrain.keys()):
                terrain['name'] = None
            self.TILE_TYPES[terrain['ident']]['name'] = terrain['name']
            if('group' not in terrain.keys()):
                terrain['group'] = None
            self.TILE_TYPES[terrain['ident']]['group'] = terrain['group']
            if('move_cost' not in terrain.keys()):
                terrain['move_cost'] = 0
            self.TILE_TYPES[terrain['ident']
                            ]['move_cost'] = terrain['move_cost']
            if('open' not in terrain.keys()):
                terrain['open'] = None
            self.TILE_TYPES[terrain['ident']]['open'] = terrain['open']
            if('close' not in terrain.keys()):
                terrain['close'] = None
            self.TILE_TYPES[terrain['ident']]['close'] = terrain['close']
            if('description' not in terrain.keys()):
                terrain['description'] = ''
            self.TILE_TYPES[terrain['ident']
                            ]['description'] = terrain['description']
            if('flags' not in terrain.keys()):
                terrain['flags'] = None
            self.TILE_TYPES[terrain['ident']]['flags'] = terrain['flags']
            if('bash' not in terrain.keys()):
                terrain['bash'] = None
            self.TILE_TYPES[terrain['ident']]['bash'] = terrain['bash']
            if('transforms_into' not in terrain.keys()):
                terrain['transforms_into'] = None
            self.TILE_TYPES[terrain['ident']
                            ]['transforms_into'] = terrain['transforms_into']
            if('roof' not in terrain.keys()):
                terrain['roof'] = None
            self.TILE_TYPES[terrain['ident']]['roof'] = terrain['roof']
            if('harvest_season' not in terrain.keys()):
                terrain['harvest_season'] = 'Summer'
            self.TILE_TYPES[terrain['ident']]['harvest_season'] = terrain['harvest_season']
            if('deconstruct' not in terrain.keys()):
                terrain['deconstruct'] = None
            self.TILE_TYPES[terrain['ident']]['deconstruct'] = terrain['deconstruct']
            if('symbol' not in terrain.keys()):
                terrain['symbol'] = ' '
            self.TILE_TYPES[terrain['ident']]['symbol'] = terrain['symbol']
            if('color' not in terrain.keys()):
                terrain['color'] = '200'
            self.TILE_TYPES[terrain['ident']]['color'] = terrain['color']

        # possible_keys = ['group', 'ident', 'subtype', 'entries', 'type', 'name', 'symbol', 'color', 'move_cost',
        # 'trap', 'flags', 'roof', 'examine_action', 'bash', 'connects_to', 'comment', 'aliases', 'open', 'close',
        # 'deconstruct', 'max_volume', 'transforms_into', 'harvest_by_season', 'description', 'harvest_season']

        # keys_we_care_about = ['group', 'ident', 'subtype', 'entries', 'type', 'name', 'symbol', 'move_cost',
        # 'trap', 'flags', 'roof', 'examine_action', 'bash', 'connects_to', 'comment', 'aliases', 'open', 'close',
        # 'deconstruct', 'max_volume', 'transforms_into', 'harvest_by_season', 'description', 'harvest_season']

        print('total TILE_TYPES loaded: ' + str(len(self.TILE_TYPES)))
