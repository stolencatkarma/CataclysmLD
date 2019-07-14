#tile config checker - attempts to convert an old style tile_config into C:LD format.
import json
from collections import defaultdict

from tile import TileManager

with open('tile_config.json') as data_file: # load tile config so we know what tile goes with what ident
    data = json.load(data_file)

export = {}
export['tile_info'] = list()
tmp_dict = {}
tmp_dict['height'] = 24
tmp_dict['width'] = 24
export['tile_info'].append(tmp_dict)

export['tiles-new'] = list()
tmp_dict2 = {}
tmp_dict2['file'] = 'tiles.png'
tmp_dict2['tiles'] = list()




for tiles in data['tiles-new']:
    for tile in tiles['tiles']:
        # print(tile)
        var_dict = dict()
        if(not 'bg' in tile.keys()):
            print('does not contain a bg. fixing.')
            tile['bg'] = 0
        if(not 'fg' in tile.keys()):
            print('does not contain a fg. fixing.')
            tile['fg'] = 0
        if(not 'rotates' in tile.keys()):
            tile['rotates'] = False

        #print(str(type(tile['ident'])))
        if(isinstance(tile['ident'], list)):
            for item in tile['ident']:
                var_dict['ident'] = item
                var_dict['fg'] = tile['fg'] # eg, tile['ident']['fg'] is a integer of the foreground of that ident
                var_dict['bg'] = tile['bg']
                var_dict['rotates'] = tile['rotates']
        else:
            var_dict['ident'] = tile['ident']
            var_dict['fg'] = tile['fg'] # eg, tile['ident']['fg'] is a integer of the foreground of that ident
            var_dict['bg'] = tile['bg']
            var_dict['rotates'] = tile['rotates']

        tmp_dict2['tiles'].append(var_dict)


export['tiles-new'].append(tmp_dict2)

with open('new_tile_config.json', 'w') as outfile:
    json.dump(export, outfile, indent=2)
