# defines body parts for creatures.
class Bodypart:
    def __init__(self, ident, vital_organ=False):
        self.ident = ident
        self.vital_organ = vital_organ # can the creature live without this body part?
        self.equipped = [] # kind of a waste to have a list for two items but i want to iterate it and append and remove.

        # Body parts can hold a maximum of two items. 2 equipment or 2 container or one of each.
        # wearable_location on items is the check if we can equip it here.
        # weapons should be set to wearable_location: "HAND"
        # HAND locations will only allow 1 equipment from the group "weapon"
        

    def __str__(self):
        return str(self.ident)
