# defines body parts for creatures.
class Bodypart(dict):
    def __init__(self, ident, vital_organ=False):
        # print(ident)
        self['ident'] = ident
        # will the creature die without this body part?
        self['vital_organ'] = vital_organ
        self['slot0'] = None  # (container or armor)
        self['slot1'] = None
        if(self['ident'].split('_')[0] == 'HAND'):
            # hands have an extra slot for grabbed items.
            self['slot_equipped'] = None

        # Body parts can hold a maximum of two items. 2 equipment or 2 container or one of each.
        # wearable_location on items is the check if we can equip it here.
        # weapons should be set to wearable_location: "EQUIPABLE"
        # HAND locations will only allow 1 equipment from the group "weapon"
