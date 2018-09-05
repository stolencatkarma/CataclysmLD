from collections import defaultdict
import json
import pprint
import os
import sys

class Profession:
    def __init__(self, ident='generic'):
        self.ident = ident

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
                                print(key, value)
                                if(isinstance(value, list)):
                                    self.PROFESSIONS[item['ident']][key] = []
                                    for add_value in value:
                                        self.PROFESSIONS[item['ident']][key].append(str(add_value))
                                elif(isinstance(value, dict)):
                                    self.PROFESSIONS[item['ident']][key] = {}
                                    for add_key, add_value in value.items():
                                        self.PROFESSIONS[item['ident']][key][add_key] = add_value
                                else:
                                    self.PROFESSIONS[item['ident']][key] = str(value)
                            print(self.PROFESSIONS[item['ident']])
                        except Exception:
                            print()
                            print('!! couldn\'t parse: ' + str(item) + ' -- likely missing ident.')
                            print()
                            sys.exit()

        print('total PROFESSIONS loaded: ' + str(len(self.PROFESSIONS)))