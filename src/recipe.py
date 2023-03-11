from collections import defaultdict
import json
import os


class Recipe(dict):
    def __init__(self, ident):
        self['ident'] = ident


class RecipeManager:
    def __init__(self):
        # the dict of tiles loaded from the tile_config.json
        self.RECIPE_TYPES = defaultdict(dict)
        for root, dirs, files in os.walk('./data/json/recipes/'):
            for file_data in files:
                if file_data.endswith('.json'):
                    # load tile config, so we know what tile foes with what ident
                    with open(root+'/'+file_data) as data_file:
                        data = json.load(data_file)
                    for item in data:
                        for key, value in item.items():
                            # components are list(dict or list) if it's a list then it's a OR
                            # type recipe for that component.
                            if(key == 'components'):
                                # init the components list in the dict for result.
                                self.RECIPE_TYPES[item['result']][key] = []
                                for dict_or_list in value:  # will be a dict or a list.
                                    # this is an OR list of items.
                                    if(type(dict_or_list) == list):
                                        tmp_list = []
                                        for item2 in dict_or_list:
                                            tmp_list.append(item2)
                                        self.RECIPE_TYPES[item['result']][key].append(
                                            tmp_list)
                                    # this is just a regular key/value pair. just add it as is.
                                    else:
                                        self.RECIPE_TYPES[item['result']][key].append(
                                            dict_or_list)
                            # this is just a regular key/value pair. just add it as is.
                            else:
                                self.RECIPE_TYPES[item['result']][key] = value

                    # print()

        '''for result in self.RECIPE_TYPES.keys():
            #print(str(result))
            print('----------------------------------------------------------')
            for key, value in self.RECIPE_TYPES[str(result)].items():
                print(str(key) + ': ' + str(value)) # + ': ' + str(value))
                #if(type(value) is list):
                    #for sub_value in value:
                        #print(str(sub_value) + ' --- ' + str(type(sub_value)))'''

        # print('------------------------------------------------------------------------------')
        print('total RECIPE_TYPES loaded: ' + str(len(self.RECIPE_TYPES)))
