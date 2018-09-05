from collections import defaultdict
import json
import pprint
import os
import sys

class Profession:
    def __init__(self, ident='generic'):
        self.ident = ident
        self._name_male = 'generic'
        self._name_female = 'generic'
        self._description_male = 'None'
        self._description_female = 'None'

        self.starting_items = []

        # need a way to equip starting items by default.
        # give a tuple of idents and whether they are equipped or not.
        # self. starting_items.append('2x4', )

    def __str__(self):
        return self.ident


class ProfessionManager:
    def __init__(self):
        # load professions from file and save references to them.
        self.PROFESSIONS = defaultdict(dict)
        for root, dirs, files in os.walk('./data/json/professions/'):
            for file_data in files:
                if file_data.endswith('.json'):
                    with open(root+'/'+file_data, encoding='utf-8') as data_file: 
                        data = json.load(data_file)
                    for item in data:
                        try:
                            for key, value in item.items():
                                if(isinstance(value, list)):
                                    self.PROFESSIONS[item['ident']][key] = []
                                    for add_value in value:
                                        self.PROFESSIONS[item['ident']][key].append(str(add_value))
                                else:
                                    self.PROFESSIONS[item['ident']][key] = str(value)
                        except Exception:
                            print()
                            print('!! couldn\'t parse: ' + str(item) + ' -- likely missing ident.')
                            print()
                            sys.exit()

        print('total PROFESSIONS loaded: ' + str(len(self.PROFESSIONS)))