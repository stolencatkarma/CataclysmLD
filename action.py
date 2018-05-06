
class Action:
    def __init__(self, owner, action_type, args=[]):
        self.owner = owner
        self.action_type = action_type
        self.args = args

    def __str__(self):
        return str(self.action_type)
