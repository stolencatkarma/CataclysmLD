# /usr/bin/env python3

import argparse
import json
import os
import random
import sys
import time
from pprint import pprint
import configparser
# import logging.config
import re

from src.mastermind._mm_server import MastermindServerTCP
from src.action import Action
from src.game_calendar import GameCalendar
from src.command import Command
from src.furniture import FurnitureManager
from src.item import Container, Item, ItemManager, Blueprint
from src.character import Character
from src.position import Position
from src.recipe import RecipeManager
from src.profession import ProfessionManager
from src.monster import MonsterManager
from src.worldmap import Worldmap
from src.tilemanager import TileManager
from src.passhash import hashPassword as hashpass
from src.terrain import Terrain
from src.furniture import Furniture


# when the character pulls up the OverMap.
class OverMap:
    def __init__(self):  # the ident of the character who owns this overmap.
        # over map size is the worldmap size
        # build the overmap from seen tiles, roadmaps, maps.
        # if a character sees a chunk loaded it's safe to say they 'saw' that overmap tile.
        return


class Server(MastermindServerTCP):
    def monster_ai_turn(self):
        """Process AI for all monsters, adding actions to their command queues"""
        for monster_name, monster in self.monsters.items():
            if not monster or not isinstance(monster, dict):
                continue
            
            # Skip dead monsters
            if not monster.get('alive', True):
                continue
            
            # Clear previous AI commands (keep only 1 action queued)
            if len(monster.get("command_queue", [])) > 0:
                continue  # Monster already has an action queued
            
            # Find nearby players to attack
            monster_pos = monster.get("position")
            if not monster_pos:
                continue
            
            # Get tiles within aggression range
            aggression_range = 5  # Monsters can detect players within 5 tiles
            nearby_tiles = self.worldmap.get_tiles_near_position(monster_pos, aggression_range)
            
            target_player = None
            target_distance = float('inf')
            
            # Look for player characters in nearby tiles
            for tile_info in nearby_tiles:
                tile, distance = tile_info
                if not tile or not tile.get('creature'):
                    continue
                
                creature = tile['creature']
                # Check if this creature is a player character
                if creature.get('name') in self.characters and distance < target_distance:
                    target_player = creature
                    target_distance = distance
            
            if target_player:
                # Calculate direction to target
                player_pos = target_player.get("position")
                if player_pos:
                    direction = self.calculate_direction(monster_pos, player_pos)
                    
                    if target_distance <= 1:
                        # Adjacent - attack
                        from src.action import Action
                        attack_action = Action(monster['name'], monster['name'], "attack", [direction])
                        monster["command_queue"].append(attack_action)
                    else:
                        # Move towards player
                        from src.action import Action
                        move_action = Action(monster['name'], monster['name'], "move", [direction])
                        monster["command_queue"].append(move_action)

    def calculate_direction(self, from_pos, to_pos):
        """Calculate the primary direction from one position to another"""
        dx = to_pos["x"] - from_pos["x"]
        dy = to_pos["y"] - from_pos["y"]
        
        # Determine primary direction
        if abs(dx) > abs(dy):
            return "east" if dx > 0 else "west"
        else:
            return "south" if dy > 0 else "north"

    def compute_turn(self):
        """Process all player and monster command queues for this turn."""
        # First, run AI for all monsters
        self.monster_ai_turn()
        
        # Process all player characters
        for character_name, character in self.characters.items():
            if not character or not isinstance(character, dict):
                continue
            # Defensive: ensure command_queue exists
            if "command_queue" not in character or not isinstance(character["command_queue"], list):
                character["command_queue"] = []
            # Process commands quietly - characters can move even when offline
            self.process_creature_command_queue(character)
        # Process all monsters (if they have AI/commands)
        for monster_name, monster in self.monsters.items():
            if not monster or not isinstance(monster, dict):
                continue
            if "command_queue" not in monster or not isinstance(monster["command_queue"], list):
                monster["command_queue"] = []
            self.process_creature_command_queue(monster)
        # Advance the calendar (time)
        if hasattr(self, "calendar") and hasattr(self.calendar, "advance_turn"):
            self.calendar.advance_turn()
        # Optionally, handle world events, stasis, etc. here
        # print("Turn processed.")
    def __init__(self, config, logger=None):
        MastermindServerTCP.__init__(self, 0.5, 0.5, 600.0)
        self._config = config
        if logger is None:
            pass
        else:
            self._log = logger

        # all the Character()s that exist in the world whether connected or not.
        self.characters = dict()
        # all the monsters that exist in the world. 
        self.monsters = dict()
        # account to character mapping
        self.account_characters = dict()  # {username: [character_names]}

        self.localmaps = dict()  # the localmaps for each character.
        self.overmaps = dict()  # the dict of all overmaps by character

        self.worldmap = Worldmap()
        # Load characters from world chunks after worldmap is initialized
        self.load_characters_from_world()
        self.RecipeManager = RecipeManager()
        self.ProfessionManager = ProfessionManager()
        self.MonsterManager = MonsterManager()
        self.ItemManager = ItemManager()
        self.FurnitureManager = FurnitureManager()
        self.TileManager = TileManager()

        self.calendar = GameCalendar(0,0,0,0,0,0)
        self.calendar.load_calendar()
        
        # Load account-character mapping and migrate any existing characters
        self.load_account_mappings()
        self.migrate_existing_characters()

    def calculate_route(self, pos0, pos1, consider_impassable=True):
        # normally we will want to consider impassable terrain in movement calculations.
        # Creatures that can walk or break through walls don't need to though.
        path = [pos0]
        goal = pos1

        while path[len(path) - 1] != goal:
            # print("loop")
            # get reachable positions from the last point on the map.
            new_reachable = self.worldmap.get_adjacent_positions_non_impassable(
                path[len(path) - 1]
            )

            # get the tile in those that is closest to the goal.
            next_pos = None
            for adjacent in new_reachable:
                if next_pos is None:
                    next_pos = adjacent
                    continue
                if (abs(adjacent["x"] - goal["x"]) + abs(adjacent["y"] - goal["y"])) < (
                        abs(next_pos["x"] - goal["x"]) +
                        abs(next_pos["y"] - goal["y"])
                ):
                    next_pos = adjacent
            # print(path[len(path) - 1])
            path.append(next_pos)

            if len(path) > 9:
                break

        return path

    def find_spawn_point_for_new_character(self):
        _possible = list()
        starting_chunks = list()
        for chunk in self.worldmap['CHUNKS']:
            starting_chunks.append(chunk)
        random.shuffle(starting_chunks)
        chunk = self.worldmap['CHUNKS'][starting_chunks[0]]
        pprint(chunk)
        path = str("./world/" + str(starting_chunks[0]) + ".chunk")
        if(chunk['stasis']):
            print("thawing chunk ", starting_chunks[0])
            with open(path) as json_file:
                self.worldmap["CHUNKS"][starting_chunks[0]] = json.load(json_file)
                self.worldmap["CHUNKS"][starting_chunks[0]]["stasis"] = False
                self.worldmap["CHUNKS"][starting_chunks[0]]["should_stasis"] = False
                self.worldmap["CHUNKS"][starting_chunks[0]]["time_to_stasis"] = 100

        for tile in self.worldmap["CHUNKS"][starting_chunks[0]]["tiles"]:
            if tile["position"]["z"] != 0:
                continue
            if tile["terrain"]["impassable"]:
                continue
            if tile["creature"] is not None:
                continue
            if tile["terrain"]["ident"] == "t_open_air":
                continue
            _possible.append(tile)
        random.shuffle(_possible)
        return _possible[0]["position"]

    def handle_new_character(self, ident, character):
        self.characters[character] = Character(character)

        # find a spot for them to spawn and fill their server side settings.
        self.characters[character]["position"] = self.find_spawn_point_for_new_character()
        self.worldmap.put_object_at_position(self.characters[character], self.characters[character]["position"])
        self.localmaps[character] = self.worldmap.get_chunks_near_position(self.characters[character]["position"])

        # give the character their starting items by referencing the ProfessionManager.
        for key, value in self.ProfessionManager.PROFESSIONS[str(self.characters[character]["profession"])].items():
            if key == "known_recipes":  # list
                for recipe in value:
                    # print("adding recipe")
                    self.characters[character]["known_recipes"].append(recipe)

            if key == "equipped_items":
                for equip_location, item_ident in value.items():
                    for bodypart in self.characters[character]["body_parts"]:
                        if bodypart["ident"].split("_")[0] == equip_location:
                            if bodypart["slot0"] is None:
                                if "container_type" in self.ItemManager.ITEM_TYPES[item_ident]:
                                    bodypart["slot0"] = Container(item_ident)
                                else:
                                    bodypart["slot0"] = Item(item_ident)
                                break
                            elif bodypart["slot1"] is None:
                                if "container_type" in self.ItemManager.ITEM_TYPES[item_ident]:
                                    bodypart["slot1"] = Container(item_ident)
                                else:
                                    bodypart["slot1"] = Item(item_ident)
                                break
                    else:
                        print("character needed an item but no free slots found")
            elif key == "items_in_containers":  # load the items_in_containers into their containers we just created.
                for location_ident, item_ident in value.items():
                    # first find the location_ident, so we can load a new item into it.
                    for bodypart in self.characters[character]["body_parts"]:
                        if bodypart["slot0"] is not None:
                            if "contained_items" in bodypart["slot0"] and bodypart["ident"] == location_ident:
                                bodypart["slot0"]["contained_items"].append(Item(item_ident))
                        if bodypart["slot1"] is not None:
                            if "contained_items" in bodypart["slot1"] and bodypart["ident"] == location_ident:
                                bodypart["slot1"]["contained_items"].append(Item(item_ident))

        # Add character to account mapping
        self.add_character_to_account(ident, character)
        print("New character added to world: {}".format(character))
        return

    def load_characters_from_world(self):
        """Load all characters from world chunks into memory."""
        print("Loading characters from world chunks...")
        for chunk_key, chunk in self.worldmap["CHUNKS"].items():
            for tile in chunk["tiles"]:
                if tile.get("creature") is not None:
                    creature = tile["creature"]
                    # Check if this is a player character (has name attribute)
                    if isinstance(creature, dict) and "name" in creature:
                        character_name = creature["name"]
                        self.characters[character_name] = creature
                        print(f"Loaded character: {character_name} at {creature.get('position', 'unknown position')}")
        print(f"Loaded {len(self.characters)} characters from world")

    def load_account_mappings(self):
        """Load account-character mappings from account files."""
        print("Loading account-character mappings...")
        try:
            for root, dirs, files in os.walk("./accounts/"):
                for dir_name in dirs:
                    account_path = os.path.join(root, dir_name)
                    mapping_file = os.path.join(account_path, "characters.json")
                    
                    if os.path.exists(mapping_file):
                        try:
                            with open(mapping_file, 'r') as f:
                                characters = json.load(f)
                                self.account_characters[dir_name] = characters
                                print(f"Loaded {len(characters)} characters for account {dir_name}")
                        except json.JSONDecodeError:
                            print(f"Warning: Invalid JSON in {mapping_file}")
                            self.account_characters[dir_name] = []
                    else:
                        # Initialize empty character list for this account
                        self.account_characters[dir_name] = []
        except Exception as e:
            print(f"Error loading account mappings: {e}")
        print(f"Loaded mappings for {len(self.account_characters)} accounts")

    def add_character_to_account(self, username, character_name):
        """Add a character to an account's character list."""
        if username not in self.account_characters:
            self.account_characters[username] = []
        
        if character_name not in self.account_characters[username]:
            self.account_characters[username].append(character_name)
            self.save_account_mapping(username)

    def save_account_mapping(self, username):
        """Save account-character mapping to file."""
        account_dir = f"./accounts/{username}"
        os.makedirs(account_dir, exist_ok=True)
        mapping_file = os.path.join(account_dir, "characters.json")
        
        try:
            with open(mapping_file, 'w') as f:
                json.dump(self.account_characters[username], f)
        except Exception as e:
            print(f"Error saving account mapping for {username}: {e}")

    def migrate_existing_characters(self):
        """Migrate any existing .character files to the new system."""
        print("Checking for existing character files to migrate...")
        migrated_count = 0
        
        try:
            for root, dirs, files in os.walk("./accounts/"):
                for file in files:
                    if file.endswith(".character"):
                        char_file_path = os.path.join(root, file)
                        character_name = file[:-10]  # Remove .character extension
                        
                        # Extract username from path
                        path_parts = root.split(os.sep)
                        if "accounts" in path_parts:
                            accounts_index = path_parts.index("accounts")
                            if accounts_index + 1 < len(path_parts):
                                username = path_parts[accounts_index + 1]
                                
                                try:
                                    # Load character data from file
                                    with open(char_file_path, 'r') as f:
                                        character_data = json.load(f)
                                    
                                    # Only migrate if character is not already in world
                                    if character_name not in self.characters:
                                        # Add to world at the saved position
                                        self.characters[character_name] = character_data
                                        position = character_data.get("position")
                                        if position:
                                            self.worldmap.put_object_at_position(character_data, position)
                                        
                                        # Add to account mapping
                                        self.add_character_to_account(username, character_name)
                                        
                                        migrated_count += 1
                                        print(f"Migrated character {character_name} for account {username}")
                                    
                                    # Remove old character file
                                    os.remove(char_file_path)
                                    print(f"Removed old character file: {char_file_path}")
                                    
                                except Exception as e:
                                    print(f"Error migrating character file {char_file_path}: {e}")
        except Exception as e:
            print(f"Error during character migration: {e}")
        
        if migrated_count > 0:
            print(f"Successfully migrated {migrated_count} characters to new system")
        else:
            print("No character files found to migrate")

    # where most data is handled from the client.
    def callback_client_handle(self, connection_object, data):
        for i in (re.findall(r"\{(.*?)\}", data)):
            print(i)
            data = ("{" + i + "}") # re-add the brackets we stripped with findall()
            data = json.loads(data) # convert the data back to json
            try:
                _command = Command(data["ident"], data["command"], data["args"])
                print(_command)
            except Exception:
                print("Server: invalid data from client {}.".format(connection_object.address))
                return

            # we recieved a valid command. process it.
            if isinstance(_command, Command):
                if _command["command"] == "login":
                    # this will be the client's username.
                    connection_object.username = data['ident']
                    print(connection_object.username + " entered login")
                    connection_object.password = data['args'][1] # assign only the password string

                    _path = "./accounts/" + connection_object.username + "/"
                    if os.path.isdir(_path):
                        # account exists. check the received password against the saved one.
                        with open(str(_path + "SALT"), "r") as _salt_file:
                            salt = _salt_file.read().strip()
                        with open(str(_path + "HASHED_PASSWORD"), "r") as _password:
                            stored_hash = _password.read().strip()
                        # hash the received password with the stored salt
                        check_hash = hashpass(connection_object.password, salt)
                        if check_hash == stored_hash:
                            print("password accepted for " + connection_object.username)
                            _accepted = Command("server", "login", "accepted")
                            self.callback_client_send(connection_object, json.dumps(_accepted))
                        else:
                            print("Password NOT accepted for " + connection_object.username)
                            connection_object.terminate()
                            return
                    else:
                        # account doesn't exist. create a directory for them.
                        try:
                            os.mkdir(_path)
                        except OSError:
                            print("Creation of the directory %s failed" % _path)
                        else:
                            print("Successfully created the directory %s " % _path)
                        # generate salt and hash password
                        import random, string
                        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
                        hashed = hashpass(connection_object.password, salt)
                        with open(str(_path + "SALT"), "w") as f:
                            f.write(salt)
                        with open(str(_path + "HASHED_PASSWORD"), "w") as f:
                            f.write(hashed)
                        _path_char = _path + "characters/"
                        try:
                            os.mkdir(_path_char)
                        except OSError:
                            print("Creation of the directory %s failed" % _path_char)
                        else:
                            print("Successfully created the directory %s " % _path_char)
                        _accepted = Command("server", "login", "accepted")
                        self.callback_client_send(connection_object, json.dumps(_accepted))
                        return
                
                if _command["command"] == "request_character_list":
                    print('client is requesting character list')
                    _tmp_list = list()
                    username = _command["ident"]
                    
                    # Get characters for this account from mapping
                    if username in self.account_characters:
                        for character_name in self.account_characters[username]:
                            # Get character data from world
                            if character_name in self.characters:
                                character_data = self.characters[character_name]
                                # Convert to JSON string for client compatibility
                                _raw = json.dumps(character_data)
                                _tmp_list.append(_raw)
                            else:
                                print(f"Warning: Character {character_name} in account mapping but not found in world")

                    _command = Command('server', 'character_list', _tmp_list)
                    self.callback_client_send(connection_object, json.dumps(_command))
                    return

                if _command["command"] == "choose_character":
                    print(connection_object.username + " entered choose_character")
                    self.clear_stale_character_connections(_command['args'], connection_object)
                    connection_object.character = _command['args']
                    _command = Command('server', 'enter_game', [])
                    self.callback_client_send(connection_object, json.dumps(_command))
                    return

                if _command["command"] == "completed_character":
                    print(connection_object.username + " entered completed_character")
                    # _command["args"] should be the character name or data
                    character_name = _command["args"]
                    # Ensure we have a valid character name
                    if not character_name or not character_name.strip():
                        character_name = f"Player_{connection_object.username}_{int(time.time())}"
                        print(f"Generated default name: {character_name}")
                    
                    if not character_name in self.characters:
                        # this character doesn't exist in the world yet.
                        self.handle_new_character(connection_object.username, character_name)
                        self.clear_stale_character_connections(character_name, connection_object)
                        # Select the newly created character
                        connection_object.character = character_name
                        _command = Command('server', 'enter_game', [])
                        self.callback_client_send(connection_object, json.dumps(_command))
                        print(f"Server: character created for {connection_object.username}.")
                    else:
                        print(f"Server: character NOT created. Already Exists: {character_name}")
                    return


                if _command["command"] == "request_localmap": # player wants their local map
                    # Check if character is selected
                    if not hasattr(connection_object, "character") or connection_object.character is None:
                        print(f"Warning: {connection_object.username} requested localmap without selecting character")
                        return
                    chunks = self.worldmap.get_chunks_near_position(self.characters[connection_object.character]["position"])
                    _command = Command('server', 'localmap_update', chunks)
                    #print(_command)
                    self.callback_client_send(connection_object, json.dumps(_command))
                    print('sent ' + connection_object.username + " their localmap")
                    return


                ### all the commands below are Action() and need to be put into the creature's command_queue
                ### compute_turn() will loop through each queue each turn and process the Action()
                if _command["command"] == "move":
                    # Check if character is selected
                    if not hasattr(connection_object, "character") or connection_object.character is None:
                        print(f"Warning: {connection_object.username} tried to move without selecting character")
                        return
                    # Only allow one move/action to be queued at a time to prevent spamming.
                    if len(self.characters[connection_object.character]["command_queue"]) > 0:
                        # Optionally, you can send a message to the client here.
                        print(f"Move command blocked: {connection_object.character} already has {len(self.characters[connection_object.character]['command_queue'])} queued commands")
                        return
                    action = Action(connection_object.character, connection_object.character, "move", _command["args"])
                    self.characters[connection_object.character]["command_queue"].append(action)
                    return
            # The commands above this line should all be working. please open an issue if you find a problem.
                
                if _command["command"] == "bash":
                    # Check if character is selected
                    if not hasattr(connection_object, "character") or connection_object.character is None:
                        print(f"Warning: {connection_object.username} tried to bash without selecting character")
                        return
                    if len(_command["args"]) == 0:
                        self.callback_client_send(connection_object, "What do you want to bash?\r\n")
                        return
                    # Only allow one action to be queued at a time
                    if len(self.characters[connection_object.character]["command_queue"]) > 0:
                        return
                    _target = _command["args"][0]
                    _action = Action(connection_object.character, _target, 'bash', _command["args"])
                    self.characters[connection_object.character]["command_queue"].append(_action)
                    return

                if _command["command"] == "attack":
                    # Check if character is selected
                    if not hasattr(connection_object, "character") or connection_object.character is None:
                        print(f"Warning: {connection_object.username} tried to attack without selecting character")
                        return
                    if len(_command["args"]) == 0:
                        self.callback_client_send(connection_object, "What direction do you want to attack?\r\n")
                        return
                    # Only allow one action to be queued at a time
                    if len(self.characters[connection_object.character]["command_queue"]) > 0:
                        print(f"Attack command blocked: {connection_object.character} already has {len(self.characters[connection_object.character]['command_queue'])} queued commands")
                        return
                    action = Action(connection_object.character, connection_object.character, "attack", _command["args"])
                    self.characters[connection_object.character]["command_queue"].append(action)
                    return

                if _command["command"] == "look":
                    # Check if character is selected
                    if not hasattr(connection_object, "character") or connection_object.character is None:
                        print(f"Warning: {connection_object.username} tried to look without selecting character")
                        return
                    if len(_command["args"]) > 0:  # character is trying to look into a container or blueprint.
                        if _command["args"][0] == "in":
                            # find a container that matches the [1] arg
                            _ident = _command["args"][1]
                            _open_containers = []

                            # make a list of open_containers the character has.
                            for bodyPart in self.characters[connection_object.character]["body_parts"]:
                                if (bodyPart["slot0"] is not None and "opened" in bodyPart["slot0"] and bodyPart["slot0"][
                                    "opened"] == "yes"):
                                    _open_containers.append(bodyPart["slot0"])
                                if (bodyPart["slot1"] is not None and "opened" in bodyPart["slot1"] and bodyPart["slot1"][
                                    "opened"] == "yes"):
                                    _open_containers.append(bodyPart["slot1"])

                            if len(_open_containers) <= 0:
                                self.callback_client_send(connection_object, "You have no open containers.\r\n")
                                return  # no open containers.

                            for container in _open_containers:
                                if _ident in self.ItemManager.ITEM_TYPES[container["ident"]]["name"].lower().split(" "):
                                    if len(container["contained_items"]) == 0:
                                        self.callback_client_send(connection_object,
                                                                "There is no items in this container.\r\n")
                                    else:
                                        for item in container["contained_items"]:
                                            self.callback_client_send(connection_object,
                                                                    self.ItemManager.ITEM_TYPES[item["ident"]][
                                                                        "name"] + "\r\n")
                                    return


                    _tile = self.worldmap.get_tile_by_position(self.characters[connection_object.character]["position"])
                    if not _tile:
                        self.callback_client_send(connection_object, "You see nothing here.\r\n")
                        return
                    self.callback_client_send(connection_object, "You are standing on " +
                                            self.TileManager.TILE_TYPES.get(_tile['terrain']['ident'], {}).get('name', 'Unknown') + "\r\n")

                    if _tile.get("items") and len(_tile["items"]) > 0:
                        self.callback_client_send(connection_object, "---- Items ----\r\n")
                        for item in _tile["items"]:
                            if item["ident"] == "blueprint":
                                self.callback_client_send(connection_object,
                                                        item["ident"] + ": " + item["recipe"]["result"] + "\r\n")
                            else:
                                self.callback_client_send(connection_object,
                                                        self.ItemManager.ITEM_TYPES.get(item["ident"], {}).get("name", "Unknown") + "\r\n")

                    if _tile.get("furniture") is not None:
                        self.callback_client_send(connection_object, "-- Furniture --\r\n")
                        _furniture = self.FurnitureManager.FURNITURE_TYPES.get(_tile["furniture"]["ident"], {})
                        self.callback_client_send(connection_object,
                                                _furniture.get("name", "Unknown") + ": " + _furniture.get("description", "") + "\r\n")

                    # send_prompt sends a prompt to the client after each request. Don't forget to add it for new commands.
                    return

                if _command["command"] == "character":  # character sheet
                    # Check if character is selected
                    if not hasattr(connection_object, "character") or connection_object.character is None:
                        print(f"Warning: {connection_object.username} requested character sheet without selecting character")
                        return
                    _character = self.characters[connection_object.character]
                    self.callback_client_send(connection_object, "### Character Sheet\r\n")
                    self.callback_client_send(connection_object, "# Name: " + _character["name"] + "\r\n")
                    self.callback_client_send(connection_object, "#\r\n")
                    self.callback_client_send(connection_object, "# Strength: " + str(_character["strength"]) + "\r\n")
                    self.callback_client_send(connection_object, "# Dexterity: " + str(_character["dexterity"]) + "\r\n")
                    self.callback_client_send(connection_object,
                                            "# Intelligence: " + str(_character["intelligence"]) + "\r\n")
                    self.callback_client_send(connection_object, "# Perception: " + str(_character["perception"]) + "\r\n")
                    self.callback_client_send(connection_object,
                                            "# Constitution: " + str(_character["constitution"]) + "\r\n")
                    for body_part in _character["body_parts"]:
                        self.callback_client_send(connection_object, "# " + body_part["ident"] + "\r\n")
                        if body_part["slot0"] is not None:
                            self.callback_client_send(connection_object, "#  " + body_part["slot0"]["ident"] + "\r\n")
                        if body_part["slot1"] is not None:
                            self.callback_client_send(connection_object, "#  " + body_part["slot1"]["ident"] + "\r\n")
                        if "slot_equipped" in _character:
                            if body_part["slot_equipped"] is not None:
                                self.callback_client_send(connection_object,
                                                        "#  " + body_part["slot_equipped"]["ident"] + "\r\n")

                    return

                if _command["command"] == "craft":  # 2-3 args (craft, <recipe>, direction)
                    # Check if character is selected
                    if not hasattr(connection_object, "character") or connection_object.character is None:
                        print(f"Warning: {connection_object.username} tried to craft without selecting character")
                        return

                    if len(_command["args"]) < 2:
                        self.callback_client_send(connection_object, "syntax is \'craft recipe direction\'\r\n")
                        return

                    if _command["args"][0] not in self.characters[connection_object.character]["known_recipes"]:
                        self.callback_client_send(connection_object,
                                                "You do not know how to craft" + _command["args"][0] + ".\r\n")
                        return
                    # args 0 is ident args 1 is direction.
                    # blueprint rules
                    # * there should be blueprints for terrain, furniture, items, and anything else that takes a slot up in a tile.
                    # * they act as placeholders and then 'transform' into the type they are once completed.
                    # Blueprint(type_of, recipe)
                    position_to_create_at = self.characters[connection_object.character]["position"]
                    if _command["args"][1] == "south":
                        position_to_create_at = Position(
                            position_to_create_at["x"],
                            position_to_create_at["y"] + 1,
                            position_to_create_at["z"],
                        )
                    elif _command["args"][1] == "north":
                        position_to_create_at = Position(
                            position_to_create_at["x"],
                            position_to_create_at["y"] - 1,
                            position_to_create_at["z"],
                        )
                    elif _command["args"][1] == "east":
                        position_to_create_at = Position(
                            position_to_create_at["x"] + 1,
                            position_to_create_at["y"],
                            position_to_create_at["z"],
                        )
                    elif _command["args"][1] == "west":
                        position_to_create_at = Position(
                            position_to_create_at["x"] - 1,
                            position_to_create_at["y"],
                            position_to_create_at["z"],
                        )
                    else:
                        self.callback_client_send(connection_object,
                                                "That is not a valid direction. try north, south, east, or west.\r\n")
                        return

                    _tile = self.worldmap.get_tile_by_position(position_to_create_at)
                    if not _tile or not _tile.get("terrain") or _tile["terrain"].get("impassable"):
                        self.callback_client_send(connection_object,
                                                "You cannot create a blueprint on impassable terrain.\r\n")
                        return

                    if not _tile.get("items"):
                        self.callback_client_send(connection_object, "There are no items on this tile.\r\n")
                        return
                    if _tile and _tile.get("items"):
                        for item in _tile["items"]:
                            if item["ident"] == "blueprint":
                                self.callback_client_send(connection_object,
                                                        "You cannot create two blueprints on one tile.\r\n")
                                return

                    _recipe = self.RecipeManager.RECIPE_TYPES[_command["args"][0]]
                    type_of = _recipe["type_of"]

                    # Blueprint likely needs an ident, type_of, recipe. Use recipe["result"] as ident.
                    bp_to_create = Blueprint(_recipe["result"], type_of, _recipe)

                    self.worldmap.put_object_at_position(bp_to_create, position_to_create_at)
                    self.callback_client_send(connection_object,
                                            "You created a blueprint for " + _command["args"][0] + ".\r\n")
                    return

                if _command["command"] == "take":  # take an item from current tile and put it in players open inventory. (take, <item>)
                    # Check if character is selected
                    if not hasattr(connection_object, "character") or connection_object.character is None:
                        print(f"Warning: {connection_object.username} tried to take without selecting character")
                        return
                    _from_pos = self.characters[connection_object.character]["position"]
                    if len(_command["args"]) == 0:
                        self.callback_client_send(connection_object, "What do you want to take?\r\n")
                        return

                    _item_ident = _command["args"][0]
                    _from_item = None
                    _open_containers = []

                    # find the item that the character is requesting.
                    _tile = self.worldmap.get_tile_by_position(_from_pos)
                    if not _tile or not _tile.get("items"):
                        self.callback_client_send(connection_object, "There are no items here.\r\n")
                        return
                    for item in _tile["items"]:
                        if _item_ident in self.ItemManager.ITEM_TYPES.get(item["ident"], {}).get("name", "").split(" "):
                            _from_item = item
                            break

                    if _from_item is None:
                        self.callback_client_send(connection_object, "I could not find what you are looking for.\r\n")
                        return

                    for bodyPart in self.characters[connection_object.character]["body_parts"]:
                        if (bodyPart["slot0"] is not None and "opened" in bodyPart["slot0"] and bodyPart["slot0"]["opened"] == "yes"):
                            _open_containers.append(bodyPart["slot0"])
                        if (bodyPart["slot1"] is not None and "opened" in bodyPart["slot1"] and bodyPart["slot1"]["opened"] == "yes"):
                            _open_containers.append(bodyPart["slot1"])

                    if len(_open_containers) <= 0:
                        self.callback_client_send(connection_object, "You have no open containers.\r\n")
                        return

                    # add it to the first open container and remove it from the world.
                    container = _open_containers[0]
                    container["contained_items"].append(_from_item)
                    _tile["items"].remove(_from_item)
                    self.worldmap.get_chunk_by_position(_from_pos)["is_dirty"] = True

                    self.callback_client_send(connection_object,
                        str("You take the " + self.ItemManager.ITEM_TYPES.get(_from_item["ident"], {}).get("name", "item") +
                            " and put it in your " + self.ItemManager.ITEM_TYPES.get(container["ident"], {}).get("name", "container") + "\r\n"))
                    return

                if _command["command"] == "transfer":  # (transfer, <item_ident>, <container_ident>) *Requires two open containers or taking from tile['items'].
                    # client sends 'hey server. can you move item from this to that?'
                    if len(_command["args"]) < 2:
                        self.callback_client_send(connection_object, "Requires an item and an open container.\r\n")
                        return

                    _character_requesting = self.characters[connection_object.character]

                    _item = None  # the item we are moving. parse this

                    # the container the item is coming from. parse this
                    # either the player's character inventory or the player occupied tile["items"]
                    _from_container = None

                    # the container the item will end up. parse this as well.
                    contained_item = None

                    # find _from_container and _item, either equipped containers or items on the ground.
                    _tile = self.worldmap.get_tile_by_position(_character_requesting["position"])
                    if _tile and _tile.get("items"):
                        for ground_item in _tile["items"][:]:  # parse copy
                            # check if item is laying on the ground. tile["items"]
                            if _command["args"][0] in ground_item.get("name", "").split(" "):
                                _item = ground_item
                                _from_container = _tile["items"]
                                break
                    # if we didn't find it there let's check the player's own inventory.
                    else:
                        for bodypart in _character_requesting["body_parts"][:]:
                            if bodypart["slot0"] is not None and hasattr(bodypart["slot0"], "__iter__"):
                                for body_item in bodypart["slot0"]:
                                    if isinstance(body_item, Container):
                                        for contained_item in body_item["contained_items"]:
                                            if _command["args"][0] in contained_item.get("name", "").split(" "):
                                                _item = contained_item
                                                _from_container = bodypart["slot0"]
                                                break
                            if bodypart["slot1"] is not None and hasattr(bodypart["slot1"], "__iter__"):
                                for body_item in bodypart["slot1"]:
                                    if isinstance(body_item, Container):
                                        for contained_item in body_item["contained_items"]:
                                            if _command["args"][0] in contained_item.get("name", "").split(" "):
                                                _item = contained_item
                                                _from_container = bodypart["slot1"]
                                                break
                        else:
                            self.callback_client_send(connection_object,
                                                    "Could not find item on ground or in open containers.\r\n")
                            return

                    # ## possible move types ##
                    # creature(held) to creature(held) (give to another character)
                    # creature(held) to position(ground) (drop)
                    # creature(held) to bodypart (equip)
                    # bodypart to creature(held) (unequip)
                    # bodypart to position (drop)

                    # position to creature(held) (pick up from ground)
                    # position to bodypart (equip from ground)
                    # position to position (move from here to there)

                    # creature to blueprint (fill blueprint)

                    # blueprint to position (empty blueprint on ground)
                    # blueprint to creature (grab from blueprint)

                if _command["command"] == "hotbar":  # basically user aliases that get saved per character. TODO
                    return

                if _command["command"] == "recipe":
                    # Check if character is selected
                    if not hasattr(connection_object, "character") or connection_object.character is None:
                        print(f"Warning: {connection_object.username} tried to access recipes without selecting character")
                        return
                    if len(_command["args"]) == 0:
                        # send the player their character's known recipes.
                        _character = self.characters[connection_object.character]
                        self.callback_client_send(connection_object, "--- Known Recipes ---\r\n")

                        for recipe in _character["known_recipes"]:
                            self.callback_client_send(connection_object, recipe + "\r\n")
                    else:  # send the specific recipe.
                        try:
                            _recipe = _command["args"][0]
                            self.callback_client_send(connection_object, "--- Recipe ---\r\n")
                            self.callback_client_send(connection_object,
                                                    self.RecipeManager.RECIPE_TYPES[_recipe]["result"] + "\r\n")
                            for component in self.RecipeManager.RECIPE_TYPES[_recipe]["components"]:
                                print(component)
                                self.callback_client_send(connection_object,
                                                        " " + str(component["amount"]) + "* " + component[
                                                            "ident"] + "\r\n")
                            return
                        except:
                            # recipe doesn't exist.
                            self.callback_client_send(connection_object, "No known recipe.\r\n")
                    return

                if _command["command"] == "help":
                    self.callback_client_send(connection_object,
                                            "Common commands are look, move, bash, attack, craft, take, transfer, recipe, character, spawn.\r\n")
                    self.callback_client_send(connection_object, "Furniture can be \'bash\'d for recipe components.\r\n")
                    self.callback_client_send(connection_object, "Press 'A' then a direction to attack adjacent creatures.\r\n")
                    self.callback_client_send(connection_object, "Use 'spawn' to create monsters for testing.\r\n")
                    self.callback_client_send(connection_object, "recipes can be \'craft\'ed and then \'work\'ed on.\r\n")
                    self.callback_client_send(connection_object,
                                            "\'dump direction\' to put components in a blueprint from inventory.\r\n")
                    return

                if _command["command"] == "spawn":
                    # Debug command to spawn monsters (for testing)
                    if not hasattr(connection_object, "character") or connection_object.character is None:
                        print(f"Warning: {connection_object.username} tried to spawn without selecting character")
                        return
                    
                    if len(_command["args"]) == 0:
                        # Spawn random monsters around player
                        player_pos = self.characters[connection_object.character]["position"]
                        self.spawn_random_monsters_near_position(player_pos, radius=3, count=2)
                        self.callback_client_send(connection_object, "Spawned random monsters nearby.\r\n")
                    else:
                        # Spawn specific monster type
                        monster_type = _command["args"][0]
                        player_pos = self.characters[connection_object.character]["position"]
                        # Spawn in random direction from player
                        import random
                        directions = [
                            Position(player_pos["x"] + 1, player_pos["y"], player_pos["z"]),
                            Position(player_pos["x"] - 1, player_pos["y"], player_pos["z"]),
                            Position(player_pos["x"], player_pos["y"] + 1, player_pos["z"]),
                            Position(player_pos["x"], player_pos["y"] - 1, player_pos["z"])
                        ]
                        spawn_pos = random.choice(directions)
                        if self.spawn_monster(monster_type, spawn_pos):
                            self.callback_client_send(connection_object, f"Spawned {monster_type} nearby.\r\n")
                        else:
                            self.callback_client_send(connection_object, f"Failed to spawn {monster_type}.\r\n")
                    return

                if _command["command"] == "work":  # (work direction) The command just sets up the action. Do checks in the action queue.
                    if len(_command["args"]) == 0:
                        self.callback_client_send(connection_object,
                                                "You must supply a direction. try north, south, east, or west.\r\n")
                        return
                    # Only allow one action to be queued at a time
                    if len(self.characters[connection_object.character]["command_queue"]) > 0:
                        return
                    # check blueprint exists in the direction.
                    position_to_create_at = self.characters[connection_object.character]["position"]
                    if _command["args"][0] == "south":
                        position_to_create_at = Position(
                            position_to_create_at["x"],
                            position_to_create_at["y"] + 1,
                            position_to_create_at["z"],
                        )
                    elif _command["args"][0] == "north":
                        position_to_create_at = Position(
                            position_to_create_at["x"],
                            position_to_create_at["y"] - 1,
                            position_to_create_at["z"],
                        )
                    elif _command["args"][0] == "east":
                        position_to_create_at = Position(
                            position_to_create_at["x"] + 1,
                            position_to_create_at["y"],
                            position_to_create_at["z"],
                        )
                    elif _command["args"][0] == "west":
                        position_to_create_at = Position(
                            position_to_create_at["x"] - 1,
                            position_to_create_at["y"],
                            position_to_create_at["z"],
                        )
                    else:
                        self.callback_client_send(connection_object,
                                                "That is not a valid direction. try north, south, east, or west.\r\n")
                        return

                    _tile = self.worldmap.get_tile_by_position(position_to_create_at)

                    _recipe = None
                    _blueprint = None
                    if _tile and _tile.get("items"):
                        for item in _tile["items"]:
                            if item["ident"] == "blueprint":  # one blueprint per tile.
                                _recipe = item["recipe"]
                                _blueprint = item
                                break
                    else:
                        self.callback_client_send(connection_object, "There is no Blueprint in that tile to work on.\r\n")
                        return

                    # TODO: Does character have this blueprint learned? give it to them. (learn by seeing)
                    # Queue the work action; do not send immediate result.
                    _action = Action(connection_object.character, None, 'work', _command["args"])
                    self.characters[connection_object.character]["command_queue"].append(_action)
                    self.callback_client_send(connection_object, "You start working on the blueprint.\r\n")
                    return

                if _command["command"] == "dump":  # (dump direction)
                    # check for items in a blueprint from the direction and drop the items in the blueprint that are needed.
                    # get the recipe from the blueprint. we need a reference.
                    if len(_command["args"]) == 0:
                        self.callback_client_send(connection_object,
                                                "You must supply a direction. try north, south, east, or west.\r\n")
                        return

                    position_to_create_at = self.characters[connection_object.character]["position"]
                    if _command["args"][0] == "south":
                        position_to_create_at = Position(
                            position_to_create_at["x"],
                            position_to_create_at["y"] + 1,
                            position_to_create_at["z"],
                        )
                    elif _command["args"][0] == "north":
                        position_to_create_at = Position(
                            position_to_create_at["x"],
                            position_to_create_at["y"] - 1,
                            position_to_create_at["z"],
                        )
                    elif _command["args"][0] == "east":
                        position_to_create_at = Position(
                            position_to_create_at["x"] + 1,
                            position_to_create_at["y"],
                            position_to_create_at["z"],
                        )
                    elif _command["args"][0] == "west":
                        position_to_create_at = Position(
                            position_to_create_at["x"] - 1,
                            position_to_create_at["y"],
                            position_to_create_at["z"],
                        )
                    else:
                        self.callback_client_send(connection_object,
                                                "That is not a valid direction. try north, south, east, or west.\r\n")
                        return

                    _tile = self.worldmap.get_tile_by_position(position_to_create_at)

                    _recipe = None
                    _blueprint = None
                    for item in _tile["items"]:
                        if item["ident"] == "blueprint":  # only one blueprint per tile.
                            _recipe = item["recipe"]
                            _blueprint = item
                            break
                    else:
                        self.callback_client_send(connection_object, "There is no Blueprint in that tile to dump.\r\n")
                        return
                    # check only items that belong to the recipe get dumped.
                    # loop through open containers on the creature

                    for component in self.RecipeManager.RECIPE_TYPES[_recipe["result"]]["components"]:
                        # the recipe is only stored by ident in the worldmap to save memory.
                        # get open containers.
                        # TODO: check for items already in it.
                        _character_requesting = self.characters[connection_object.character]
                        for bodypart in _character_requesting["body_parts"]:
                            if bodypart["slot0"] is not None:
                                body_item = bodypart["slot0"]
                                if "opened" in body_item.keys():  # is this a container?
                                    if body_item["opened"] == "yes":
                                        for contained_item in body_item["contained_items"][:]:
                                            if component["ident"] == contained_item["ident"]:
                                                # add item to blueprint["contained_items"]
                                                # remove item from container.
                                                _blueprint["contained_items"].append(contained_item)
                                                pprint(_blueprint)
                                                body_item["contained_items"].remove(contained_item)
                                                self.callback_client_send(connection_object,
                                                                        "You dumped " + component["ident"] + ".\r\n")
                            if bodypart["slot1"] is not None:
                                body_item = bodypart["slot1"]
                                if "opened" in body_item.keys():
                                    if body_item["opened"] == "yes":
                                        for contained_item in body_item["contained_items"][:]:
                                            if component["ident"] == contained_item["ident"]:
                                                _blueprint["contained_items"].append(contained_item)
                                                body_item["contained_items"].remove(contained_item)
                                                self.callback_client_send(connection_object,
                                                                        "You dumped " + component["ident"] + ".\r\n")
                    return
            
            return super(Server, self).callback_client_handle(connection_object, data)

    def callback_client_send(self, connection_object, data, compression=None):
        # Match base class signature: compression can be None or bool
        return super(Server, self).callback_client_send(connection_object, data, compression)

    def callback_connect_client(self, connection_object):
        print("Client {} connected.".format(connection_object.address))
        # send the user a login prompt
        # connection_object.state = "LOGIN"
        # return super(Server, self).callback_connect_client(connection_object)
        # TODO: for line in Message Of The Day send to client.
        # motd = open('motd.txt', 'r')
        # motd_lines = motd.readlines()

        # Strips the newline character 
        #for line in motd_lines:
        #    self.callback_client_send(connection_object, line)
        #self.callback_client_send(connection_object, " \r\n")
        #self.callback_client_send(connection_object, " \r\n")
        #self.callback_client_send(connection_object, "Please Login:\r\n")
        #self.callback_client_send(connection_object, "Username? >\r\n")
        #return

    def callback_disconnect_client(self, connection_object):
        print("Server: Client from {} disconnected.".format(connection_object.address))
        
        # Remove connection from list to prevent communicating with dead clients
        if connection_object.address in self._mm_connections:
            try:
                del self._mm_connections[connection_object.address]
            except KeyError:
                pass

        # Clean up character association
        if hasattr(connection_object, 'character'):
            print(f"Character {connection_object.character} is now offline")
            # Don't delete the character attribute here since it might still be referenced
        return super(Server, self).callback_disconnect_client(connection_object)

    def find_connection_object_by_character_name(self, character):
        # Use list() to copy keys, preventing RuntimeError if dictionary changes during iteration
        for con_object in list(self._mm_connections.keys()):
            if con_object not in self._mm_connections:
                continue
            connection = self._mm_connections[con_object]
            # Check if connection is active and has the character
            if (hasattr(connection, 'character') and 
                connection.character == character):
                return connection
        return None

    def clear_stale_character_connections(self, character_name, current_connection=None):
        """Remove character association from any other connections"""
        for con_object in list(self._mm_connections.keys()):
            try:
                connection = self._mm_connections[con_object]
                if hasattr(connection, 'character') and connection.character == character_name:
                    if connection != current_connection:
                        print(f"Clearing stale entry for character {character_name} from {connection.address}")
                        del connection.character
            except Exception:
                pass

    def process_creature_command_queue(self, creature):  # processes a single turn for as many action points as they get per turn.
        actions_to_take = creature["actions_per_turn"]
        actions_processed = 0
        i = 0
        max_actions = min(actions_to_take, len(creature["command_queue"]))
        while actions_processed < actions_to_take and i < len(creature["command_queue"]):
            if actions_processed >= actions_to_take:
                break
            action = creature["command_queue"][i]
            _pos = creature["position"]
            _target_pos = creature["position"] # default to the characters position if a direction is excluded

            # this creature can't act until x turns from now.
            if creature["next_action_available"] > 0:
                creature["next_action_available"] = creature["next_action_available"] - 1
                break

            # Directional argument parsing
            if action.get("args") and len(action["args"]) > 0:
                if action["args"][0] == "north":
                    _target_pos = Position(_pos["x"], _pos["y"] - 1, _pos["z"])
                elif action["args"][0] == "south":
                    _target_pos = Position(_pos["x"], _pos["y"] + 1, _pos["z"])
                elif action["args"][0] == "east":
                    _target_pos = Position(_pos["x"] + 1, _pos["y"], _pos["z"])
                elif action["args"][0] == "west":
                    _target_pos = Position(_pos["x"] - 1, _pos["y"], _pos["z"])
                elif action["args"][0] == "up":
                    _target_pos = Position(_pos["x"], _pos["y"], _pos["z"] + 1)
                elif action["args"][0] == "down":
                    _target_pos = Position(_pos["x"], _pos["y"], _pos["z"] - 1)

            # Process action types
            if action.get("type") == "work":
                for _ in range(actions_to_take - actions_processed):
                    self.work(action["owner"], _target_pos)
                actions_processed = actions_to_take
                creature["command_queue"].pop(i)
                break
            elif action.get("type") == "move":
                self.worldmap.move_creature_from_position_to_position(creature, _pos, _target_pos)
                actions_processed += 1
                creature["command_queue"].pop(i)
                continue
            elif action.get("type") == "bash":
                self.bash(action["owner"], action["target"])
                self.localmaps[creature["name"]] = self.worldmap.get_chunks_near_position(
                    self.characters[creature["name"]]["position"])
                actions_processed += 1
                creature["command_queue"].pop(i)
                continue
            elif action.get("type") == "attack":
                self.attack(creature, _target_pos)
                actions_processed += 1
                creature["command_queue"].pop(i)
                continue
            else:
                i += 1

        # After processing actions, send the updated localmap to the client if connected
        character_name = creature.get("name")
        if character_name:
            connection_object = self.find_connection_object_by_character_name(character_name)
            if connection_object:
                try:
                    chunks = self.worldmap.get_chunks_near_position(creature["position"])
                    update_command = Command('server', 'localmap_update', chunks)
                    self.callback_client_send(connection_object, json.dumps(update_command))
                    # print(f"Sent localmap update to {character_name}")
                except Exception as e:
                    print(f"Failed to send localmap update to {character_name}: {e}")
                    # Connection is stale, remove character association
                    if hasattr(connection_object, 'character'):
                        del connection_object.character
            # No need to log when connection not found - character can exist without being online

    def work(self, owner, target):
        connection_object = self.find_connection_object_by_character_name(owner)
        _tile = self.worldmap.get_tile_by_position(target)
        _recipe = None
        _blueprint = None
        if not _tile or not _tile.get("items") or not isinstance(_tile.get("items"), list):
            print("WARNING: Player tried to work on non-existant blueprint (no tile or items).")
            return
        for item in _tile["items"]:
            if item and isinstance(item, dict) and item.get("ident") == "blueprint":  # only one blueprint per tile.
                _recipe = item.get("recipe")
                _blueprint = item
                break
        else:
            print("WARNING: Player tried to work on non-existant blueprint.")
            return

        if not _recipe:
            print("WARNING: Blueprint missing recipe.")
            self.callback_client_send(connection_object, "Blueprint is missing a recipe.\r\n")
            return

        print("_recipe")
        pprint(_recipe)
        print()
        print("_blueprint")
        pprint(_blueprint)
        print()
        count = dict()
        for material in _blueprint.get("contained_items", []):  # these could be duplicates. get a count.
            print("material")
            pprint(material)
            if material["ident"] in count.keys():
                count[material["ident"]]["amount"] = count[material["ident"]]["amount"] + 1
            else:
                count[material["ident"]] = dict()
                count[material["ident"]]["amount"] = 1

        for component in _recipe.get("components", []):
            # get count of item by ident in blueprint.
            if not component["ident"] in count or count[component["ident"]]["amount"] < component["amount"]:
                # need all required components to start.
                self.callback_client_send(connection_object, "Blueprint does not contain the required components.\r\n")
                print("not enough components.")
                return

        # add time worked on to the blueprint.
        _blueprint["turns_worked_on"] = _blueprint["turns_worked_on"] + 1
        self.callback_client_send(connection_object, "Working on blueprint..\r\n")
        # if the "time worked on" is greater than the "time" is takes to craft then
        # create the object and remove the blueprint and all materials.
        if _blueprint["turns_worked_on"] >= _recipe["time"]:
            _newobject = None
            # create Item, Terrain, Furniture from recipe by result.
            if _blueprint["type_of"] == "Item":
                _newobject = Item(_recipe["result"])
                if isinstance(_tile.get("items"), list):
                    _tile["items"].append(_newobject)
            if _blueprint["type_of"] == "Furniture":
                _newobject = Furniture(_recipe["result"])
                _tile["furniture"] = _newobject
            if _blueprint["type_of"] == "Terrain":
                _newobject = Terrain(_recipe["result"])
                _tile["terrain"] = _newobject
            if isinstance(_tile.get("items"), list) and _blueprint in _tile["items"]:
                _tile["items"].remove(_blueprint)  # remove it from the world.
            self.callback_client_send(connection_object, "Finished working on blueprint!\r\n")
            print("Completed blueprint")
            return
        return

    def attack(self, attacker, target_pos):
        """Handle combat attack from attacker towards target_pos"""
        # Get the tile at target position
        target_tile = self.worldmap.get_tile_by_position(target_pos)
        if not target_tile:
            print(f"Attack failed: No tile at position {target_pos}")
            return
        
        # Check if there's a creature at the target position
        target_creature = target_tile.get('creature')
        if not target_creature:
            print(f"Attack failed: No creature at position {target_pos}")
            return
        
        # Don't allow attacking yourself
        if target_creature.get('name') == attacker.get('name'):
            print(f"Attack failed: Cannot attack yourself")
            return
        
        # Calculate damage based on attacker's strength
        base_damage = 10  # Base unarmed damage
        strength_bonus = max(0, attacker.get('strength', 8) - 8)  # Bonus damage from strength above 8
        damage = base_damage + strength_bonus
        
        # Apply damage to target
        target_health = target_creature.get('current_health', 100)
        new_health = max(0, target_health - damage)
        target_creature['current_health'] = new_health
        
        # Check if target died
        if new_health <= 0:
            target_creature['alive'] = False
            print(f"{attacker.get('name', 'Unknown')} killed {target_creature.get('name', 'Unknown')} with {damage} damage!")
            
            # Remove dead creature from the tile
            target_tile['creature'] = None
            
            # If it was a player character, handle death
            if target_creature.get('name') in self.characters:
                print(f"Player character {target_creature.get('name')} has died!")
        else:
            print(f"{attacker.get('name', 'Unknown')} attacks {target_creature.get('name', 'Unknown')} for {damage} damage! ({new_health}/{target_creature.get('max_health', 100)} HP remaining)")
        
        # Send updates to connected clients if they're players
        for char_name in [attacker.get('name'), target_creature.get('name')]:
            if char_name and char_name in self.characters:
                connection_object = self.find_connection_object_by_character_name(char_name)
                if connection_object:
                    try:
                        chunks = self.worldmap.get_chunks_near_position(self.characters[char_name]["position"])
                        update_command = Command('server', 'localmap_update', chunks)
                        self.callback_client_send(connection_object, json.dumps(update_command))
                    except Exception as e:
                        print(f"Failed to send combat update to {char_name}: {e}")

    def spawn_monster(self, monster_ident, position):
        """Spawn a specific monster at the given position"""
        if monster_ident not in self.MonsterManager.MONSTER_TYPES:
            print(f"Warning: Monster type '{monster_ident}' not found")
            return None
        
        # Check if position is valid and empty
        tile = self.worldmap.get_tile_by_position(position)
        if not tile:
            print(f"Cannot spawn monster: invalid position {position}")
            return None
        
        if tile.get('creature') is not None:
            print(f"Cannot spawn monster: position {position} already occupied")
            return None
        
        # Create monster from template
        from src.monster import Monster
        monster = Monster()
        monster_template = self.MonsterManager.MONSTER_TYPES[monster_ident]
        
        # Apply monster template stats
        monster['name'] = f"{monster_template['name']}_{len(self.monsters)}"
        monster['ident'] = monster_ident
        monster['position'] = position
        monster['tile_ident'] = monster_ident  # For rendering
        
        # Set health based on hitdie
        hitdie = int(monster_template.get('hitdie', 1))
        max_health = hitdie * 15  # 15 HP per hit die
        monster['max_health'] = max_health
        monster['current_health'] = max_health
        monster['alive'] = True
        
        # Set stats based on tier
        tier = int(monster_template.get('tier', 1))
        base_stat = 6 + tier * 2
        monster['strength'] = base_stat
        monster['dexterity'] = base_stat
        monster['constitution'] = base_stat
        monster['intelligence'] = max(1, base_stat - 4)  # Most monsters are not very smart
        monster['perception'] = base_stat
        
        # Set aggression and behavior
        monster['aggression'] = int(monster_template.get('aggression', 50))
        monster['morale'] = int(monster_template.get('morale', 50))
        monster['species'] = monster_template.get('species', 'unknown')
        monster['faction'] = monster_template.get('default_faction', 'hostile')
        
        # Place monster in world
        tile['creature'] = monster
        self.monsters[monster['name']] = monster
        
        print(f"Spawned {monster['name']} at {position}")
        return monster

    def spawn_random_monsters_near_position(self, center_position, radius=5, count=3):
        """Spawn random monsters in an area around a position"""
        import random
        
        # Get list of all available monster types
        monster_types = list(self.MonsterManager.MONSTER_TYPES.keys())
        if not monster_types:
            print("No monster types available for spawning")
            return
        
        spawned = 0
        attempts = 0
        max_attempts = count * 10  # Prevent infinite loops
        
        while spawned < count and attempts < max_attempts:
            attempts += 1
            
            # Pick random position within radius
            x_offset = random.randint(-radius, radius)
            y_offset = random.randint(-radius, radius)
            spawn_pos = Position(
                center_position["x"] + x_offset,
                center_position["y"] + y_offset,
                center_position["z"]
            )
            
            # Pick random monster type
            monster_type = random.choice(monster_types)
            
            # Try to spawn
            if self.spawn_monster(monster_type, spawn_pos):
                spawned += 1
        
        print(f"Spawned {spawned} monsters near {center_position}")

    def spawn_monsters_on_chunk_load(self, chunk):
        """Spawn monsters when a new chunk is loaded"""
        import random
        
        # Only spawn on outdoor chunks (z=0) for now
        if chunk.get('z', 0) != 0:
            return
        
        # 30% chance to spawn monsters on new chunk
        if random.random() > 0.3:
            return
        
        # Find suitable spawn positions in the chunk
        chunk_size = chunk.get('chunk_size', 24)
        chunk_x = chunk.get('x', 0) * chunk_size
        chunk_y = chunk.get('y', 0) * chunk_size
        
        spawn_count = random.randint(1, 3)
        for _ in range(spawn_count):
            # Pick random position in chunk
            x = chunk_x + random.randint(0, chunk_size - 1)
            y = chunk_y + random.randint(0, chunk_size - 1)
            position = Position(x, y, 0)
            
            # Check if position is suitable (not impassable terrain, no existing creature)
            tile = self.worldmap.get_tile_by_position(position)
            if tile and not tile.get('terrain', {}).get('impassable', False) and not tile.get('creature'):
                # Pick appropriate monster based on location
                monster_types = self.get_appropriate_monsters_for_terrain(tile.get('terrain', {}).get('ident', 'grass'))
                if monster_types:
                    monster_type = random.choice(monster_types)
                    self.spawn_monster(monster_type, position)

    def get_appropriate_monsters_for_terrain(self, terrain_ident):
        """Return list of monster types appropriate for the given terrain"""
        # Define monster spawn tables for different terrains
        spawn_tables = {
            'grass': ['rat_giant', 'dog_feral', 'zombie_walker'],
            'dirt': ['rat_giant', 'spider_giant', 'zombie_walker'],
            'forest': ['bear_black', 'dog_feral', 'spider_giant'],
            'road': ['zombie_walker', 'zombie_runner', 'dog_feral'],
            'concrete': ['zombie_walker', 'zombie_runner', 'rat_giant'],
            'floor': ['rat_giant', 'spider_giant', 'eye_bot'],
            'water': ['sewer_gator', 'blob_small'],
            'sewer': ['rat_giant', 'sewer_gator', 'blob_small'],
        }
        
        # Default to basic monsters if terrain not found
        return spawn_tables.get(terrain_ident, ['zombie_walker', 'rat_giant'])

    def generate_and_apply_city_layout(self, city_size):
        city_layout = self.worldmap.generate_city(city_size)
        # for every 1 city size it's 13 tiles across and high
        for j in range(city_size * 13 - 1):
            for i in range(city_size * 13 - 1):
                _chunk = server.worldmap.get_chunk_by_position(Position(i, j, 0))
                if _chunk["was_loaded"] is False:
                    json_file = None
                    if city_layout[i][j] == "r":
                        json_file = random.choice(os.listdir("./data/json/mapgen/residential/"))
                        server.worldmap.build_json_building_on_chunk("./data/json/mapgen/residential/" + json_file,
                                                                     Position(i * _chunk["chunk_size"],
                                                                              j * _chunk["chunk_size"], 0))
                    elif city_layout[i][j] == "c":
                        json_file = random.choice(os.listdir("./data/json/mapgen/commercial/"))
                        server.worldmap.build_json_building_on_chunk(
                            "./data/json/mapgen/commercial/" + json_file,
                            Position(
                                i * _chunk["chunk_size"],
                                j * _chunk["chunk_size"],
                                0,
                            ),
                        )
                    elif city_layout[i][j] == "i":
                        json_file = random.choice(
                            os.listdir("./data/json/mapgen/industrial/")
                        )
                        server.worldmap.build_json_building_on_chunk(
                            "./data/json/mapgen/industrial/" + json_file,
                            Position(
                                i * _chunk["chunk_size"],
                                j * _chunk["chunk_size"],
                                0,
                            ),
                        )
                    elif (
                            city_layout[i][j] == "R"
                    ):  # complex enough to choose the right rotation.
                        attached_roads = 0
                        try:
                            if city_layout[int(i - 1)][int(j)] == "R":
                                attached_roads = attached_roads + 1
                            if city_layout[int(i + 1)][int(j)] == "R":
                                attached_roads = attached_roads + 1
                            if city_layout[int(i)][int(j - 1)] == "R":
                                attached_roads = attached_roads + 1
                            if city_layout[int(i)][int(j + 1)] == "R":
                                attached_roads = attached_roads + 1
                            if attached_roads == 4:
                                json_file = (
                                    "./data/json/mapgen/road/city_road_4_way.json"
                                )
                            elif (
                                    attached_roads == 3
                            ):
                                json_file = "./data/json/mapgen/road/city_road_3_way.json"  # placeholder
                            elif attached_roads <= 2:
                                json_file = "./data/json/mapgen/road/city_road_straight.json"  # placeholder
                            if json_file:
                                server.worldmap.build_json_building_on_chunk(
                                    json_file,
                                    Position(
                                        i * _chunk["chunk_size"] + 1,
                                        j * _chunk["chunk_size"] + 1,
                                        0,
                                    ),
                                )
                        except Exception:
                            # TODO: fix this blatant hack to account for coordinates outside the city layout.
                            pass
def mainloop(server, configParser, time_per_turn):

    dont_break = True
    while dont_break:
        try:
            # a turn is normally one second.
            server.calendar.advance_time_by_x_seconds(time_per_turn)

            # where all queued creature actions get taken care of.
            server.compute_turn()

            # if the worldmap in memory changed update it on the hard drive.
            server.worldmap.handle_chunks()
            
            # Wait for the turn duration before processing next turn
            time.sleep(time_per_turn)
        except KeyboardInterrupt:
            dont_break = False
            print()
            print("Cleaning up before exiting.")
            server.accepting_disallow()
            server.disconnect_clients()
            server.disconnect()
            # if the worldmap in memory changed update it on the hard drive.
            server.worldmap.handle_chunks()
            server.calendar.save_calendar()
            dont_break = False
            print("Done cleaning up.")



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Cataclysm: Looming Darkness Server")
    parser.add_argument("--host", metavar="Host", help="Server host", default="0.0.0.0")
    parser.add_argument("--port", metavar="Port", type=int, help="Server port", default=6317)
    parser.add_argument("--config", metavar="Config", help="Configuration file", default="server.cfg")
    args = parser.parse_args()

    # Configuration Parser - configured values override command line
    configParser = configparser.ConfigParser()
    configParser.read(args.config)

    # Grab the values within the configuration file's DEFAULT scope and
    # make them available as configuration values
    defaultConfig = configParser["DEFAULT"]
    ip = defaultConfig.get("listen_address", args.host)
    port = int(defaultConfig.get("listen_port") or args.port)

    # Enable logging - It uses its own configparser for the same file
    # logging.config.fileConfig(args.config)
    # log = logging.getLogger("root")

    citySize = int(defaultConfig.get("city_size", 1))


    # make needed directories if they don't exist
    _needed_directories = ["./accounts/", "./world/"]
    for _path in _needed_directories:
        if not os.path.isdir(_path):
            try:
                os.mkdir(_path)
            except OSError:
                print("Creation of the directory %s failed" % _path)
            else:
                print("Successfully created %s " % _path)

    server = Server(logger=None, config=defaultConfig)
    server.connect(ip, port)


   

    # TODO: add variable to make it at world position for generating cities anywhere.
    server.generate_and_apply_city_layout(citySize)

    time_per_turn = int(defaultConfig.get("time_per_turn", 1))

    for character in server.worldmap.get_all_characters():
        server.characters[character["name"]] = character
    print("Found " + str(len(server.characters)) + " living characters in the world.")
    print("Handling any chunks that may need to move to stasis before players connect.")
    server.worldmap.handle_chunks()  # handle any chunks that may need to move to stasis before player's connect.
    print("\n")
    print("Server is listening at {}:{}".format(ip, port))
    print("Started Cataclysm: Looming Darkness. Clients may now connect!")
    print("Press Ctrl+C to shutdown the server.")

    server.accepting_allow()

    mainloop(server=server, configParser=configParser, time_per_turn=time_per_turn)
