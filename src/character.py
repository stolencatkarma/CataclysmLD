from src.profession import Profession
from src.creature import Creature


class Character(Creature):
    def __init__(self, name="John Doe"):
        Creature.__init__(self)
        # Handle empty or whitespace-only names
        if not name or not name.strip():
            name = "John Doe"
        self['name'] = name
        self['style_selected'] = None
        self['profession'] = Profession("survivor")

    def __str__(self):
        return self['name'] + " the " + str(self['profession'])
