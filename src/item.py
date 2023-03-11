from collections import defaultdict
import json
import os
import sys
import pprint


class Item(dict):
    def __init__(self, ident):
        self['ident'] = ident
        # you can create objects like this.
        # _position = Position(5,5,0) # (world coordinates)
        # _newobject = Item('ident') # ident of items is found in /data/json/
        # worldmap.put_object_at_position(_newobject, _position)


# containers are types of Items and can do everything an item can do.
class Container(Item):
    def __init__(self, ident):
        Item.__init__(self, ident)
        self['contained_items'] = []
        self['opened'] = 'yes'
        # this plus all the contained items is how much the item weighs.
        self['base_weight'] = 0  # int(self['reference']['weight'])
        self['max_volume'] = 0  # int(self['reference']['volume'])
        self['contained_weight'] = 0
        self['contained_volume'] = 0


'''
    def recalc_weight(self):
        # total weight is the weight of all contained items.
        weight = 0
        for item in self['contained_items']:
            weight = weight + int(item['reference']['weight'])
        weight = weight + self['base_weight']  # add the base weight
        self['contained_weight'] = weight
'''


class Blueprint(Container):
    # Blueprint is a type of container that's immovable.
    def __init__(self, type_of, recipe, ident):
        super().__init__(ident)
        valid_types = ["Terrain", "Furniture", "Item"]
        self["ident"] = "blueprint"
        self["recipe"] = recipe
        self["type_of"] = type_of

        # when this reaches self.recipe['time'] then we need to 'turn' it into the object.
        self["turns_worked_on"] = 0
        self["contained_items"] = list()

        if self["type_of"] not in valid_types:
            self.type_of = None
            print()
            print("FATAL ERROR:  COULD NOT set type_of for Blueprint. Invalid.")
            pprint.pprint(recipe)
            print()
            sys.exit()

    def __str__(self):
        return str(self.type_of + ': ' + self["ident"])


# loads JSON data into memory.
class ItemManager:
    def __init__(self):
        self.ITEM_TYPES = defaultdict(dict)
        for root, dirs, files in os.walk('./data/json/items/'):
            for file_data in files:
                if file_data.endswith('.json'):
                    with open(root + '/' + file_data, encoding='utf-8') as data_file:
                        data = json.load(data_file)
                    for item in data:
                        try:
                            for key, value in item.items():
                                if isinstance(value, list):
                                    self.ITEM_TYPES[item['ident']][key] = []
                                    for add_value in value:
                                        self.ITEM_TYPES[item['ident']][key].append(
                                            str(add_value))
                                else:
                                    self.ITEM_TYPES[item['ident']][key] = str(
                                        value)
                        except Exception:
                            print()
                            print('!! couldn\'t parse: ' + str(item) +
                                  ' -- likely missing ident.')
                            print()
                            sys.exit()
        print('total ITEM_TYPES loaded: ' + str(len(self.ITEM_TYPES)))
