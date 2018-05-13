from collections import defaultdict
import json

class Furniture: # we only need to store the furiture and the items it contains.
    def __init__(self, ident):
        self.ident = ident
        pass
    def __str__(self):
        return str(self.ident)

class FurnitureManager: # holds all the furniture types from furniture.json
    def __init__(self):
        self.FURNITURE_TYPES = defaultdict(dict) # the dict of tiles loaded from the tile_config.json
        with open('./data/json/furniture.json') as data_file: # load tile config so we know what tile foes with what ident
            data = json.load(data_file)
        for furniture in data:
            if(not 'move_cost_mod' in furniture.keys()): # some entries dont' contain a bg, use 0 for default. (which is blank)
                furniture['move_cost_mod'] = 0
            if(not 'name' in furniture.keys()):
                furniture['name'] = 'generic_furniture'
            if(not 'symbol' in furniture.keys()):
                furniture['symbol'] = '?'
            if(not 'required_str' in furniture.keys()):
                furniture['required_str'] = 1
            if(not 'description' in furniture.keys()):
                furniture['description'] = 'generic furniture'
            if(not 'bash' in furniture.keys()):
                furniture['bash'] = None
            if(not 'bg' in furniture.keys()):
                furniture['bg'] = None
            try:
                self.FURNITURE_TYPES[furniture['ident']]['move_cost_mod'] = furniture['move_cost_mod'] # ex, TILE_TYPES['ident']]['fg'] is a integer of the foreground of that ident
                self.FURNITURE_TYPES[furniture['ident']]['name'] = furniture['name']
                self.FURNITURE_TYPES[furniture['ident']]['symbol'] = furniture['symbol']
                self.FURNITURE_TYPES[furniture['ident']]['required_str'] = furniture['required_str']
                self.FURNITURE_TYPES[furniture['ident']]['description'] = furniture['description']
                self.FURNITURE_TYPES[furniture['ident']]['bash'] = furniture['bash']
            except:
                print('invalid furniture unsuccessfully loaded.' + str(furniture))
                pass


        print('total FURNITURE_TYPES loaded: ' + str(len(self.FURNITURE_TYPES)))
