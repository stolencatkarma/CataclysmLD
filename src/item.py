from collections import defaultdict
import json
import pprint
import os
import sys

class Item:
    def __init__(self, ident, reference):
        self.ident = ident
        self.reference = reference
        # you can create objects like this.
        # worldmap.put_object_at_position(Item(ItemManager.ITEM_TYPES[str(item['item'])]['ident']), Position)

class Container(Item): # containers are types of Items and can do everything an item can do.
    def __init__(self, ident, reference):
        Item.__init__(self, ident, reference)
        self.contained_items = []
        self.opened = 'yes' # I don't like using True/False in python.
        self.base_weight = int(self.reference['weight']) # this plus all the contained items is how much the item weighs.
        self.max_volume = int(self.reference['volume'])
        self.contained_weight = 0
        self.contained_volume = 0

    def recalc_weight(self):
        # total weight is the weight of all contained items.
        weight = 0
        for item in self.contained_items:
            weight = weight + int(item.reference['weight'])
        weight = weight + self.base_weight # add the base weight
        self.contained_weight = weight

    def add_item(self, item):
        # TODO: check right item type and container type (liquids go in liquid containers.)

        # check volume
        if(int(item.reference['volume']) + self.contained_volume < self.max_volume):
            self.contained_items.append(item)
            self.recalc_weight()
            print(' - added item to container successfully.')
            return True
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
                    with open(root+'/'+file_data, encoding='utf-8') as data_file:
                        data = json.load(data_file)
                    for item in data:
                        try:
                            for key, value in item.items():
                                if(isinstance(value, list)):
                                    self.ITEM_TYPES[item['ident']][key] = []
                                    for add_value in value:
                                        self.ITEM_TYPES[item['ident']][key].append(str(add_value))
                                else:
                                    self.ITEM_TYPES[item['ident']][key] = str(value)
                        except Exception:
                            print()
                            print('!! couldn\'t parse: ' + str(item) + ' -- likely missing ident.')
                            print()
                            sys.exit()
        print('total ITEM_TYPES loaded: ' + str(len(self.ITEM_TYPES)))
