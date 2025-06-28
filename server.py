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
from src.calendar import Calendar
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

        self.localmaps = dict()  # the localmaps for each character.
        self.overmaps = dict()  # the dict of all overmaps by character

        self.worldmap = Worldmap()
        self.RecipeManager = RecipeManager()
        self.ProfessionManager = ProfessionManager()
        self.MonsterManager = MonsterManager()
        self.ItemManager = ItemManager()
        self.FurnitureManager = FurnitureManager()
        self.TileManager = TileManager()

        self.calendar = Calendar(0,0,0,0,0,0)
        self.calendar.load_calendar()

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

        path = str("./accounts/" + str(ident) + "/" + str("characters") + "/" + str(character) + ".character")

        with open(path, "w") as fp:
            json.dump(self.characters[character], fp)
            print("New character added to world: {}".format(character))
            return

    # where most data is handled from the client.
    def callback_client_handle(self, connection_object, data):
        for i in (re.findall("\{(.*?)\}", data)):
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
                    for root, _, files in os.walk(
                        "./accounts/" + _command["ident"] + "/characters/"
                    ):
                        for file_data in files:
                            if file_data.endswith(".character"):
                                with open(root + file_data, "r") as data_file:
                                    _raw = data_file.read()
                                    # client will need to decode these
                                    _tmp_list.append(_raw)

                    _command = Command('server', 'character_list', _tmp_list)
                    self.callback_client_send(connection_object, json.dumps(_command))
                    return

                if _command["command"] == "choose_character":
                    print(connection_object.username + " entered choose_character")
                    connection_object.character = _command['args']
                    _command = Command('server', 'enter_game', [])
                    self.callback_client_send(connection_object, json.dumps(_command))
                    return

                if _command["command"] == "completed_character":
                    print(connection_object.username + " entered completed_character")
                    # _command["args"] should be the character name or data
                    if not _command["args"] in self.characters:
                        # this character doesn't exist in the world yet.
                        self.handle_new_character(connection_object.username, _command["args"])
                        _command = Command('server', 'enter_game', [])
                        self.callback_client_send(connection_object, json.dumps(_command))
                        print(f"Server: character created for {connection_object.username}.")
                    else:
                        print(f"Server: character NOT created. Already Exists: {_command['args']}")
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
                    # Only allow one move/action to be queued at a time to prevent spamming.
                    if len(self.characters[connection_object.character]["command_queue"]) > 0:
                        # Optionally, you can send a message to the client here.
                        return
                    self.characters[connection_object.character]["command_queue"].append(
                        Action(connection_object.character, connection_object.character, "move", _command["args"])
                    )
                    return
            # The commands above this line should all be working. please open an issue if you find a problem.
                
                if _command["command"] == "bash":
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

                if _command["command"] == "look":
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
                                            "Common commands are look, move, bash, craft, take, transfer, recipe, character.\r\n")
                    self.callback_client_send(connection_object, "Furniture can be \'bash\'d for recipe components.\r\n")
                    self.callback_client_send(connection_object, "recipes can be \'craft\'ed and then \'work\'ed on.\r\n")
                    self.callback_client_send(connection_object,
                                            "\'dump direction\' to put components in a blueprint from inventory.\r\n")
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
        return super(Server, self).callback_disconnect_client(connection_object)

    def find_connection_object_by_character_name(self, character):
        print("looking for " + character)
        for con_object in self._mm_connections.keys():
            pprint(self._mm_connections[con_object])
            if self._mm_connections[con_object].character == character:
                return self._mm_connections[con_object]
        else:
            print("could not find character " + character)

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
            else:
                i += 1

        # After processing actions, send the updated localmap to the client if possible
        character_name = creature.get("name")
        if character_name:
            connection_object = self.find_connection_object_by_character_name(character_name)
            if connection_object:
                chunks = self.worldmap.get_chunks_near_position(creature["position"])
                update_command = Command('server', 'localmap_update', chunks)
                self.callback_client_send(connection_object, json.dumps(update_command))

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
def mainloop(server, configParser):

    dont_break = True
    while dont_break:
        try:
            # a turn is normally one second.
            server.calendar.advance_time_by_x_seconds(time_per_turn)

            # where all queued creature actions get taken care of.
            server.compute_turn()

            # if the worldmap in memory changed update it on the hard drive.
            server.worldmap.handle_chunks()
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

    mainloop(server=server, configParser=configParser)
