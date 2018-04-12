from collections import defaultdict
import json
import pprint
import os

class Item:
    def __init__(self, ident):
        self.ident = ident
        # you can create objects like this.
        # self.put_object_at_position(Item(ItemManager.ITEM_TYPES[str(item['item'])]['ident']), position)

class Container(Item): # containers are types of objects and can do everything an item can do.
    def __init__(self, ident):
        Item.__init__(self, ident)
        self.base_weight = 1 #TODO: pull this from ItemManager
        self.contained_items = []

    def recalc_weight(self):
        # total weight is the weight of all contained items.
        weight = 0
        for item in self.contained_items:
            weight = weight + item.weight
        weight = weight + self.base_weight # readd the base weight
        pass

    def add_item(self, item):
        self.contained_items.append(item)
        self.recalc_weight()
        pass

    def remove_item(self, item):
        for item_to_check in self.contained_items[:]:
            if item_to_check == item:
                self.contained_items.remove(item_to_check)
                self.recalc_weight()
                return
        pass


class ItemManager:
    def __init__(self):
        self.ITEM_TYPES = defaultdict(dict)
        for root, dirs, files in os.walk('./data/json/items/'):
            for file_data in files:
                if file_data.endswith('.json'):
                    # print(root)
                    # print(dirs)
                    # print(file_data)
                    with open(root+'/'+file_data) as data_file: # load tile config so we know what tile foes with what ident
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
                            pass
                            #print('x', end='')

        #print(unique_keys)
        #print()
        print('total ITEM_TYPES loaded: ' + str(len(self.ITEM_TYPES)))
