import sys

# is a physical representation of a recipe while it's being built in the world.
# # once built it 'turns' into the type and fills the worldmap with it.


class Blueprint(Container):
    # valid_types = ['Terrain', 'Furniture', 'Item']

    def __init__(self, type_of, recipe):
        self['ident'] = 'blueprint'
        self["recipe"] = recipe
        # when this reaches self.recipe['time'] then we need to 'turn' it into the object.
        self["turns_worked_on"] = 0
        self["contained_items"] = list()

        if(str(type_of) not in valid_types):
            self.type_of = None
            print()
            print('!!! COULDN\'T set type. Invalid')
            print(str(type_of))
            print()
            sys.exit()
        else:
            print('set type',  str(self.type_of))
            self.type_of = type_of

    def __str__(self):
        return str(self.type_of + ' ' + self['ident'])

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
