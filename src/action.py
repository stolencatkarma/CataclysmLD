
class Action(dict):
    def __init__(self, owner, target, type, args=[]):
        self["owner"] = owner
        self["target"] = target
        self["type"] = type
        self["args"] = args
