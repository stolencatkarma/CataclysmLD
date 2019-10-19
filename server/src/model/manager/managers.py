"""Container object for all managers.  A manager is an object that transforms json to an in-game object or creature, and stores it in memory."""


from src.model.manager.furniture import FurnitureManager
from src.model.manager.item import ItemManager
from src.model.manager.monster import MonsterManager
from src.model.manager.profession import ProfessionManager
from src.model.manager.recipe import RecipeManager


class Managers:
    def __init__(self):
        self.item_manager = ItemManager()
        self.recipe_manager = RecipeManager()
        self.monster_manager = MonsterManager()
        self.profession_manager = ProfessionManager()
        self.furniture_manager = FurnitureManager()
