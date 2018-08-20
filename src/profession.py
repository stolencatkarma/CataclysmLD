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
