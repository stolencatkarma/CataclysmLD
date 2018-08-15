from collections import defaultdict
import json
import pprint
import os
import sys

class Item:
    def __init__(self, ident, reference):
        # i think this needs to load it's own stats on creation so we can move it around and possibly make it into a container.
        self.ident = ident
        self.reference = reference
        # you can create objects like this.
        # self.put_object_at_position(Item(ItemManager.ITEM_TYPES[str(item['item'])]['ident']), position)

class Container(Item): # containers are types of Items and can do everything an item can do. # if a container shouldn't be an item make a new class for it.
    def __init__(self, ident):
        Item.__init__(self, ident)
        self.contained_items = []
        self.opened = 'yes' # I don't like using True/False in python.
        self.base_weight = self.reference['weight'] # this plus all the contained items is how much the item weighs.
        self.max_volume = self.reference['volume']
        self.contained_weight = 0
        self.contained_volume = 0

    def recalc_weight(self):
        # total weight is the weight of all contained items.
        weight = 0
        for item in self.contained_items:
            weight = weight + item.weight
        weight = weight + self.base_weight # add the base weight
        self.contained_weight = weight

    def add_item(self, item):
        # TODO: check right item type and container type (liquids go in liquid containers.)

        # check volume
        if(int(item['volume']) + self.contained_volume > self.max_volume):
            self.contained_items.append(item)
            self.recalc_weight()
        else:
            return False #TODO: send a message to the player that the container is full and they cannot do this.

    def remove_item(self, item):
        for item_to_check in self.contained_items[:]:
            if item_to_check == item:
                self.contained_items.remove(item_to_check)
                self.recalc_weight()
                return item # if we remove it then it needs to go somewhere. better return it so we can manage it.



class ItemManager:
    def __init__(self):
        self.ITEM_TYPES = defaultdict(dict)
        for root, dirs, files in os.walk('./data/json/items/'):
            for file_data in files:
                if file_data.endswith('.json'):
                    # print(root)
                    # print(dirs)
                    # print(file_data)
                    with open(root+'/'+file_data, encoding='utf-8') as data_file: # load tile config so we know what tile foes with what ident
                        data = json.load(data_file)
                    #unique_keys = []
                    for item in data:
                        try:
                            for key, value in item.items():
                                #print(type(value))
                                if(isinstance(value, list)):
                                    self.ITEM_TYPES[item['ident']][key] = []
                                    for add_value in value:
                                        self.ITEM_TYPES[item['ident']][key].append(str(add_value))
                                else:
                                    self.ITEM_TYPES[item['ident']][key] = str(value)
                                #print('.', end='')
                        except Exception:
                            print()
                            print('!! couldn\'t parse: ' + str(item) + ' -- likely missing ident.')
                            print()
                            sys.exit()
                            #print('x', end='')

        #print(unique_keys)
        #print()
        print('total ITEM_TYPES loaded: ' + str(len(self.ITEM_TYPES)))
