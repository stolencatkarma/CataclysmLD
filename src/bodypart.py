# defines body parts for creatures.
class Bodypart:
    def __init__(self, ident, vital_organ=False):
        #print(ident)
        self.ident = ident
        self.vital_organ = vital_organ # will the creature die without this body part?
        self.slot0 = None # Item(container or armor)
        self.slot1 = None
        self.armor = 0 # recaculate this when we wear or remove armor. the total armor value of worn items.
        if(ident.split('_')[0] == 'HAND'):
            self.slot_equipped = None # hands have an extra slot for gripped items.

        # Body parts can hold a maximum of two items. 2 equipment or 2 container or one of each.
        # wearable_location on items is the check if we can equip it here.
        # weapons should be set to wearable_location: "EQUIPABLE"
        # HAND locations will only allow 1 equipment from the group "weapon"

    def asdict(self):
        return {'ident': self.ident, 'vital_organ': self.vital_organ, 'armor': self.armor, 'slot0': self.slot1, 'slot0': self.slot1}

    def __str__(self):
        return str(self.ident)
