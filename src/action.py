
class Action(dict):
    def __init__(self, owner, action_type, args=[]):
        self['owner'] = owner
        self['action_type'] = action_type
        self['args'] = args
