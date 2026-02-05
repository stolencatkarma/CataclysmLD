from typing import Dict, Any, Optional, List

class CharacterManager:
    def __init__(self):
        self.character_data = None
        self.known_recipes = []
        self.inventory = []
        self.equipment = {}
    def update_character(self, data: Dict[str, Any]):
        self.character_data = data
        if 'inventory' in data:
            self.inventory = data['inventory']
    def get_character(self) -> Optional[Dict[str, Any]]:
        return self.character_data
    def add_recipe(self, recipe_name: str):
        if recipe_name not in self.known_recipes:
            self.known_recipes.append(recipe_name)
    def has_recipe(self, recipe_name: str) -> bool:
        return recipe_name in self.known_recipes
    def add_item(self, item: Dict[str, Any]):
        self.inventory.append(item)
    def remove_item(self, item_id: str):
        self.inventory = [item for item in self.inventory if item.get('id') != item_id]
    def equip_item(self, item_id: str):
        item = next((item for item in self.inventory if item.get('id') == item_id), None)
        if item:
            self.equipment[item.get('slot')] = item
    def unequip_item(self, slot: str):
        if slot in self.equipment:
            del self.equipment[slot]
# CharacterManager implementation moved here from old location.
