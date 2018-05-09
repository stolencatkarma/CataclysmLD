# defines body parts for creatures.
class Bodypart:
    def __init__(self, ident, vital_organ=False):
        self.ident = ident
        self.vital_organ = vital_organ # will the creature die without this body part?
        self.slot1 = None # Item(container or armor)
        self.slot2 = None
        self.armor = 0 # recaculate this when we wear or remove armor. the total armor value of worn items.

        # Body parts can hold a maximum of two items. 2 equipment or 2 container or one of each.
        # wearable_location on items is the check if we can equip it here.
        # weapons should be set to wearable_location: "HAND"
        # HAND locations will only allow 1 equipment from the group "weapon"


    def __str__(self):
        return str(self.ident)
