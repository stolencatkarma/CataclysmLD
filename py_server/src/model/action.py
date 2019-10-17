
class Action(dict):
    def __init__(self, action_type, args=[]):
        self['action_type'] = action_type
        self['args'] = args
