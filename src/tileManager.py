import json
from collections import defaultdict
import pyglet

class TileManager: # holds all the tile types from tile_config.json as well as terrain.json information because terrain can have a fg and bg
    def __init__(self):
        self.tilemapPx = 32
        self.tilemapPy = 32
        #TODO: replace this direct link to a variable in options.
        pyglet.resource.path = ['tilesets/Chesthole32/tiles','tilesets/Chesthole32/tiles/background','tilesets/Chesthole32/tiles/monsters','tilesets/Chesthole32/tiles/terrain']
        pyglet.resource.reindex()
        self.TILE_TYPES = defaultdict(dict) # the dict of tiles loaded from the tile_config.json
        with open('./tilesets/Chesthole32/tile_config.json') as data_file: # load tile config so we know what tile goes with what ident
            data = json.load(data_file)
        for tiles in data['tiles-new']:
            for tile in tiles['tiles']:
                if(not 'bg' in tile.keys()): # some entries don't contain a bg, fixing this.
                    tile['bg'] = None
                if(not 'fg' in tile.keys()):
                    tile['fg'] = None
                if(not 'rotates' in tile.keys()):
                    tile['rotates'] = False
                try:
                    self.TILE_TYPES[tile['ident']]['fg'] = tile['fg'] # eg, tile['ident']['fg'] is a integer of the foreground of that ident
                    self.TILE_TYPES[tile['ident']]['bg'] = tile['bg']
                    self.TILE_TYPES[tile['ident']]['rotates'] = tile['rotates']
                    # tile['multitile']
                    # tile['additional_tiles']))
                except:
                    pass
        with open('./data/json/terrain.json') as data_file: # load tile config so we know what tile goes with what ident
            data = json.load(data_file)
        for terrain in data:
            #pprint(terrain)
            if(not 'name' in terrain.keys()):
                terrain['name'] = None
            self.TILE_TYPES[terrain['ident']]['name'] = terrain['name']
            if(not 'group' in terrain.keys()):
                terrain['group'] = None
            self.TILE_TYPES[terrain['ident']]['group'] = terrain['group']
            if(not 'move_cost' in terrain.keys()):
                terrain['move_cost'] = 0
            self.TILE_TYPES[terrain['ident']]['move_cost'] = terrain['move_cost']
            if(not 'open' in terrain.keys()):
                terrain['open'] = None
            self.TILE_TYPES[terrain['ident']]['open'] = terrain['open']
            if(not 'close' in terrain.keys()):
                terrain['close'] = None
            self.TILE_TYPES[terrain['ident']]['close'] = terrain['close']
            if(not 'description' in terrain.keys()):
                terrain['description'] = ''
            self.TILE_TYPES[terrain['ident']]['description'] = terrain['description']
            if(not 'flags' in terrain.keys()):
                terrain['flags'] = None
            self.TILE_TYPES[terrain['ident']]['flags'] = terrain['flags']
            if(not 'bash' in terrain.keys()):
                terrain['bash'] = None
            self.TILE_TYPES[terrain['ident']]['bash'] = terrain['bash']
            if(not 'transforms_into' in terrain.keys()):
                terrain['transforms_into'] = None
            self.TILE_TYPES[terrain['ident']]['transforms_into'] = terrain['transforms_into']
            if(not 'roof' in terrain.keys()):
                terrain['roof'] = None
            self.TILE_TYPES[terrain['ident']]['roof'] = terrain['roof']
            if(not 'harvest_season' in terrain.keys()):
                terrain['harvest_season'] = 'Summer'
            self.TILE_TYPES[terrain['ident']]['harvest_season'] = terrain['harvest_season']
            if(not 'deconstruct' in terrain.keys()):
                terrain['deconstruct'] = None
            self.TILE_TYPES[terrain['ident']]['deconstruct'] = terrain['deconstruct']

        # possible_keys = ['group', 'ident', 'subtype', 'entries', 'type', 'name', 'symbol', 'color', 'move_cost', 'trap', 'flags', 'roof', 'examine_action', 'bash', 'connects_to', 'comment', 'aliases', 'open', 'close', 'deconstruct', 'max_volume', 'transforms_into', 'harvest_by_season', 'description', 'harvest_season']
        # keys_we_care_about = ['group', 'ident', 'subtype', 'entries', 'type', 'name', 'symbol', 'move_cost', 'trap', 'flags', 'roof', 'examine_action', 'bash', 'connects_to', 'comment', 'aliases', 'open', 'close', 'deconstruct', 'max_volume', 'transforms_into', 'harvest_by_season', 'description', 'harvest_season']

        print('total TILE_TYPES loaded: ' + str(len(self.TILE_TYPES)))
