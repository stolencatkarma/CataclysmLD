from collections import defaultdict
import json


# we only need to store the furiture and the items it contains.
class Furniture(dict):
    def __init__(self, ident):
        self['ident'] = ident

    def __str__(self):
        return str(self['ident'])


class FurnitureManager:  # holds all the furniture types from furniture.json
    def __init__(self):
        # the dict of tiles loaded from the tile_config.json
        self.FURNITURE_TYPES = defaultdict(dict)
        # load tile config, so we know what tile goes with what ident
        with open('./data/json/furniture.json') as data_file:
            data = json.load(data_file)
        for furniture in data:
            # some entries don't contain a bg, use 0 for default. (which is blank)
            if('move_cost_mod' not in furniture.keys()):
                furniture['move_cost_mod'] = 0
            if('name' not in furniture.keys()):
                furniture['name'] = 'generic_furniture'
            if('symbol' not in furniture.keys()):
                furniture['symbol'] = '?'
            if('required_str' not in furniture.keys()):
                furniture['required_str'] = 1
            if('description' not in furniture.keys()):
                furniture['description'] = 'generic furniture'
            if('bash' not in furniture.keys()):
                furniture['bash'] = None
            if('bg' not in furniture.keys()):
                furniture['bg'] = None
            if('flags' not in furniture.keys()):
                furniture['flags'] = None
            if('color' not in furniture.keys()):
                furniture['flags'] = "200"

            try:
                # ex, TILE_TYPES['ident']]['fg'] is a integer of the foreground of that ident
                self.FURNITURE_TYPES[furniture['ident']
                                     ]['move_cost_mod'] = furniture['move_cost_mod']
                self.FURNITURE_TYPES[furniture['ident']
                                     ]['name'] = furniture['name']
                self.FURNITURE_TYPES[furniture['ident']
                                     ]['symbol'] = furniture['symbol']
                self.FURNITURE_TYPES[furniture['ident']
                                     ]['required_str'] = furniture['required_str']
                self.FURNITURE_TYPES[furniture['ident']
                                     ]['description'] = furniture['description']
                self.FURNITURE_TYPES[furniture['ident']]['bash'] = furniture['bash']
                self.FURNITURE_TYPES[furniture['ident']]['color'] = furniture['color']
                self.FURNITURE_TYPES[furniture['ident']]['flags'] = list()
                for flag in furniture['flags']:
                    self.FURNITURE_TYPES[furniture['ident']
                                         ]['flags'].append(flag)
            except Exception:
                print('invalid furniture unsuccessfully loaded.' + str(furniture))
                pass

        print('total FURNITURE_TYPES loaded: ' +
              str(len(self.FURNITURE_TYPES)))
