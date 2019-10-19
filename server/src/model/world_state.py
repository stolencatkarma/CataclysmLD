from src.worldmap import Worldmap


class WorldState:
    def __init__(self):
        self.localmaps = dict()  # the localmaps for each character.
        self.overmaps = dict()  # the dict of all overmaps by character
        self.characters = dict()  # all the Character()s that exist in the worlds whether connected or not.
        self.worldmap = Worldmap(26)
