import json
import os

from src.request_handler.state.command_handler import CommandHandler
from src.character import Character


class CompletedCharacterHandler(CommandHandler):
    def __init__(self, profession_manager, item_manager, logger):
        super().__init__()
        self.profession_manager = profession_manager
        self.item_manager = item_manager
        self.logger = logger

    def handle_request(self, command, world_state):
        response = super().handle_request(command, world_state)
        if command.ident not in world_state.characters:
            # this character doesn't exist in the worlds yet.
            try:
                self.handle_new_character(command.ident, command.args, world_state)
                self.logger.info(f"Server: character created: {command.args} From client {command.source_address}")
                return response.set_response_success(True)
            except:
                self.logger.info(f"Server: An error occurred while creating: {command.args} From client {command.source_address}")
        else:
            self.logger.info(f"Server: character NOT created.  Already exists: {command.args} From client {command.source_address}")
        return response.set_response_success(False)

    def handle_new_character(self, ident, character_name, world_state):
        characters = world_state.characters
        worldmap = world_state.worldmap
        character = characters[character_name] = Character(character_name)

        character["position"] = worldmap.find_spawn_point_for_new_character()
        worldmap.put_object_at_position(character, character["position"])
        world_state.localmaps[character_name] = worldmap.get_chunks_near_position(character["position"])

        # give the character their starting items by referencing their profession.
        profession = self.profession_manager.get_profession(character["profession"]["ident"])
        self.equip_items(profession, character)
        self.put_items_in_containers(profession, character)

        character_dir = f"./accounts/{ident}/characters"
        os.makedirs(character_dir, exist_ok=True)

        character_resource_path = f"{character_dir}/{character_name}.character"
        with open(character_resource_path, "w") as fp:
            json.dump(character, fp)
            print(f"New character added to world: {character_name}")

    def equip_items(self, profession, character):
        for body_part_ident, item_ident in profession["equipped_items"].items():
            body_part = next(part for part in character["body_parts"] if part['ident'] == body_part_ident)
            for slot in ["slot0", "slot1"]:
                if body_part[slot] is None:
                    body_part[slot] = self.item_manager.create_item(item_ident)
                    break
            else:
                self.logger.warning(f"character tried to equip {item_ident}, but no free {body_part_ident} slots found")

    def put_items_in_containers(self, profession, character):
        for container_ident, item_ident in profession["items_in_containers"].items():
            body_part_ident = self.item_manager.get_item(container_ident)["wearable_location"]
            body_part = next(part for part in character["body_parts"] if part['ident'] == body_part_ident)
            for slot in ["slot0", "slot1"]:
                worn_item = body_part[slot]
                if worn_item["ident"] == container_ident:
                    worn_item.add_item(self.item_manager.create_item(item_ident))
                    break
            else:
                self.logger.warning(f"character tried to put {item_ident} in {container_ident}, but an error occurred")
