from collections import defaultdict
import json
import os
import sys
import pprint


class Item(dict):
    def __init__(self, ident, reference):
        self['ident'] = ident
        self['reference'] = reference
        # you can create objects like this.
        # worldmap.put_object_at_position(Item(ItemManager.ITEM_TYPES[str(item['item'])]['ident']), Position)


# containers are types of Items and can do everything an item can do.
class Container(Item):
    def __init__(self, ident, reference):
        Item.__init__(self, ident, reference)
        self['contained_items'] = []
        self['opened'] = 'yes'
        # this plus all the contained items is how much the item weighs.
        self['base_weight'] = int(self['reference']['weight'])
        self['max_volume'] = int(self['reference']['volume'])
        self['contained_weight'] = 0
        self['contained_volume'] = 0

    def recalc_weight(self):
        # total weight is the weight of all contained items.
        weight = 0
        for item in self['contained_items']:
            weight = weight + int(item['reference']['weight'])
        weight = weight + self['base_weight']  # add the base weight
        self['contained_weight'] = weight

    def add_item(self, item):
        # TODO: check right item type and container type (liquids go in liquid containers.)

        # check volume
        if(int(item['reference']['volume']) + self['contained_volume'] < self['max_volume']):
            self['contained_items'].append(item)
            self.recalc_weight()
            print(' - added item to container successfully.')
            return True
        else:
            # TODO: send a message to the player that the container is full and they cannot do this.
            return False

    def remove_item(self, item):
        for item_to_check in self['contained_items'][:]:
            if item_to_check == item:
                self['contained_items'].remove(item_to_check)
                self.recalc_weight()
                # if we remove it then it needs to go somewhere. better return it so we can manage it.
                return item


class Blueprint(Container):
    # Blueprint is a type of container that's immovable.
    def __init__(self, type_of, recipe):
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

    def work_on(self):
        # when a creature 'works on' this blueprint
        # first check if the required materials are present.
        # do we have a threshold for removing materials or create a list from the materials once
        # we start and remove 1 every so often?
        #  e.g. recipe has 5 materials and takes 10 turns, remove 1 material every 2 turns.
        # (self.turns_worked_on / int(self.recipe['time']))

        # recipes have OR and AND components. how do we handle that?
        pass

    def add_item(self, item_or_list):
        print('Trying to add item to contained_items')

        # if item not in recipe items return False else return True
        if(isinstance(item_or_list, list)):
            # got a list of items to add
            for item in item_or_list:
                for component in self.recipe['components']:
                    if(component['ident'] == item['ident']):
                        # this item belongs in this recipe.
                        break
                else:
                    # item passed doesn't belong in to this recipe.
                    return False
            # if we made it this far then every item in the list belongs to the recipe.
            for item in item_or_list:
                self.contained_items.append(item)
            return True
        else:
            # add single item.
            for component in self.recipe['components']:
                if(component['ident'] == item_or_list['ident']):
                    # this item belongs in this recipe.
                    break
            else:
                return False  # item passed doesn't belong in to this recipe.
            # if we made it this far then every item in the list belongs to the recipe.
            for item in item_or_list:
                self.contained_items.append(item)
            return True



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
