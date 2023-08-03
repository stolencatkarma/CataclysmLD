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
from src.passhash import makeSalt, hashPassword
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
                    connection_object.password = data['args'] # plaintext password until salting and hashing is back

                    # check whether this username has an account.
                    _path = "./accounts/" + connection_object.username + "/"
                    if os.path.isdir("./accounts/" + connection_object.username):
                        # account exists. check the recieved password against the saved one.
                        with open(str(_path + "PASSWORD"), "r") as _password:
                            # read the password 
                            _check = connection_object.password
                            _check2 = _password.read()
                            if _check == _check2:
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

                        with open(str(_path + "PASSWORD"), "w") as f:
                            # write the password
                            f.write(str(connection_object.password))

                        _path = "./accounts/" + connection_object.username + "/characters/"
                        try:
                            os.mkdir(_path)
                        except OSError:
                            print("Creation of the directory %s failed" % _path)
                        else:
                            print("Successfully created the directory %s " % _path)
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
                    if not _command["args"] in self.characters:
                        # this character doesn't exist in the world yet.
                        self.handle_new_character(connection_object.username, _command["args"])
                        _command = Command('server', 'enter_game', [])
                        self.callback_client_send(connection_object, json.dumps(_command))
                        print("Server: character created for {}.".format(connection_object.username))
                    else:
                        print("Server: character NOT created. Already Exists")
                    return

                if _command["command"] == "request_localmap": # player wants their local map
                    chunks = self.worldmap.get_chunks_near_position(self.characters[connection_object.character]["position"])
                    _command = Command('server', 'localmap_update', chunks)
                    #print(_command)
                    self.callback_client_send(connection_object, json.dumps(_command))
                    print('sent ' + connection_object.username + " their localmap")
                    return


                ### all the commands below are Action() and need to be put into the creature's command_queue
                ### compute_turn() will loop through each queue each turn and process the Action()
                if _command["command"] == "move":
                    self.characters[connection_object.character]["command_queue"].append(Action(connection_object.character, connection_object.character, "move", _command["args"]))
                    chunks = self.worldmap.get_chunks_near_position(self.characters[connection_object.character]["position"])
                    _command = Command('server', 'localmap_update', chunks)
                    #print(_command)
                    self.callback_client_send(connection_object, json.dumps(_command))
                    print('sent ' + connection_object.username + " their localmap")
                    return
            # The commands above this line should all be working. please open an issue if you find a problem.
                
                if _command["command"] == "bash":
                    if len(_command["args"]) == 0:
                        self.callback_client_send(connection_object, "What do you want to bash?\r\n")
                        return
                    _target = _command["args"][0]
                    _action = Action(connection_object.character, _target, 'bash', _command["args"])
                    self.characters[connection_object.character]["command_queue"].append(_action)
                    self.callback_client_send(connection_object, "You break down " + _target + " for its components.\r\n")
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
                    self.callback_client_send(connection_object, "You are standing on " +
                                            self.TileManager.TILE_TYPES[_tile['terrain']['ident']]['name'] + "\r\n")

                    if len(_tile["items"]) > 0:
                        self.callback_client_send(connection_object, "---- Items ----\r\n")
                        for item in _tile["items"]:
                            if item["ident"] == "blueprint":
                                self.callback_client_send(connection_object,
                                                        item["ident"] + ": " + item["recipe"]["result"] + "\r\n")
                            else:
                                self.callback_client_send(connection_object,
                                                        self.ItemManager.ITEM_TYPES[item["ident"]]["name"] + "\r\n")

                    if _tile["furniture"] is not None:
                        self.callback_client_send(connection_object, "-- Furniture --\r\n")
                        _furniture = self.FurnitureManager.FURNITURE_TYPES[_tile["furniture"]["ident"]]
                        self.callback_client_send(connection_object,
                                                _furniture["name"] + ": " + _furniture["description"] + "\r\n")

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
                    if _tile["terrain"]["impassable"]:
                        self.callback_client_send(connection_object,
                                                "You cannot create a blueprint on impassable terrain.\r\n")
                        return

                    for item in _tile["items"]:
                        if item["ident"] == "blueprint":
                            self.callback_client_send(connection_object,
                                                    "You cannot create two blueprints on one tile.\r\n")
                            return

                    _recipe = server.RecipeManager.RECIPE_TYPES[_command["args"][0]]
                    type_of = _recipe["type_of"]

                    bp_to_create = Blueprint(type_of, _recipe)

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
                    for item in self.worldmap.get_tile_by_position(_from_pos)["items"]:
                        if _item_ident in self.ItemManager.ITEM_TYPES[item["ident"]]["name"].split(" "):
                            # this is the item or at least the first one that matches the same ident.
                            _from_item = item  # save the reference to our local variable.
                            break

                    # we didn't find the item they wanted.
                    if _from_item is None:
                        self.callback_client_send(connection_object, "I could not find what you are looking for.\r\n")
                        return

                    # make a list of open_containers the character has to see if they can pick it up.
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

                    # add it to the container and remove it from the world.
                    # TODO: check if the character can carry that item.
                    for container in _open_containers:
                        container["contained_items"].append(item)  # add it.
                        break
                    # then find a spot for it to go (open_containers)
                    # remove it from the world.
                    self.worldmap.get_tile_by_position(_from_pos)["items"].remove(_from_item)  # remove it from the world.
                    self.worldmap.get_chunk_by_position(_from_pos)["is_dirty"] = True

                    self.callback_client_send(connection_object,
                                            str("You take the " + self.ItemManager.ITEM_TYPES[item["ident"]][
                                                "name"] + " and put it in your " +
                                                self.ItemManager.ITEM_TYPES[container["ident"]]["name"] + "\r\n"))
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
                    for ground_item in self.worldmap.get_tile_by_position(_character_requesting["position"])["items"][
                                    :]:  # parse copy
                        # check if item is laying on the ground. tile["items"]
                        if _command["args"][0] in ground_item["name"].split(
                                " "):  # found the item on the ground by parsing its ["name"]
                            _item = ground_item
                            _from_container = self.worldmap.get_tile_by_position(_character_requesting["position"])["items"]
                            break
                    # if we didn't find it there let's check the player's own inventory.
                    else:
                        for bodypart in _character_requesting["body_parts"][:]:
                            for body_item in bodypart["slot0"]:
                                if isinstance(body_item,
                                            Container):  # could be a container or armor. only move to a container.
                                    for containted_item in body_item["contained_items"]:
                                        if _command["args"][0] in contained_item["name"].split(" "):
                                            _item = body_item
                                            _from_container = bodypart["slot0"]
                                            break
                            for body_item in bodypart["slot1"]:
                                if isinstance(body_item,
                                            Container):  # could be a container or armor. only move to a container.

                                    for containted_item in body_item["contained_items"]:
                                        if _command["args"][0] in contained_item["name"].split(" "):
                                            _item = body_item
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
                    for item in _tile["items"]:
                        if item["ident"] == "blueprint":  # one blueprint per tile.
                            _recipe = item["recipe"]
                            _blueprint = item
                            break
                    else:
                        self.callback_client_send(connection_object, "There is no Blueprint in that tile to work on.\r\n")
                        return

                    # TODO: Does character have this blueprint learned? give it to them. (learn by seeing)
                    # send an action to the action queue that repeats every turn. Client sends once, server repeats until done or interrupted.
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

    def callback_client_send(self, connection_object, data, compression=False):
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
        # iterate a copy so we can remove properly.
        for action in creature["command_queue"][:]:
            print(action)
            _pos = creature["position"]
            _target_pos = creature["position"] # default to the characters position if a direction is excluded
            if actions_to_take == 0:
                return  # this creature is out of action points.

            # this creature can't act until x turns from now.
            if creature["next_action_available"] > 0:
                creature["next_action_available"] = creature["next_action_available"] - 1
                return
            print(str(action["args"][0]))
            if action["args"][0] == "north":
                _target_pos = Position(_pos["x"], _pos["y"] - 1, _pos["z"])
            if action["args"][0] == "south":
                _target_pos = Position(_pos["x"], _pos["y"] + 1, _pos["z"])
            if action["args"][0] == "east":
                _target_pos = Position(_pos["x"] + 1, _pos["y"], _pos["z"])
            if action["args"][0] == "west":
                _target_pos = Position(_pos["x"] - 1, _pos["y"], _pos["z"])
            if action["args"][0] == "up":
                _target_pos = Position(_pos["x"], _pos["y"], _pos["z"] + 1)
            if action["args"][0] == "down":
                _target_pos = Position(_pos["x"], _pos["y"], _pos["z"] - 1)
            # even if we don't have a _target_pos we can still continue on. We may not need it.
            # print("POS, TARGETPOS", _pos, _target_pos)

            if action["type"] == "work":  # "args" is the direction. For working on blueprints.
                for i in range(actions_to_take):  # working uses up all your action points per turn.
                    self.work(action["owner"], _target_pos)
                creature["command_queue"].remove(action)
            elif action["type"] == "move":
                actions_to_take = actions_to_take - 1  # moving costs 1 ap.
                self.worldmap.move_creature_from_position_to_position(creature, _pos, _target_pos)
                creature["command_queue"].remove(action)
            elif action["type"] == "bash":
                actions_to_take = actions_to_take - 1  # bashing costs 1 ap.
                self.bash(action["owner"], action["target"])
                self.localmaps[creature["name"]] = self.worldmap.get_chunks_near_position(
                    self.characters[creature["name"]]["position"])
                creature["command_queue"].remove(action)

    def work(self, owner, target):
        connection_object = self.find_connection_object_by_character_name(owner)
        _tile = self.worldmap.get_tile_by_position(target)
        _recipe = None
        _blueprint = None
        for item in _tile["items"]:
            if item["ident"] == "blueprint":  # only one blueprint per tile.
                _recipe = item["recipe"]
                _blueprint = item
                break
        else:
            print("WARNING: Player tried to work on non-existant blueprint.")
            return

        # check if blueprint has all the materials.
        print("_recipe")
        pprint(_recipe)
        print()
        print("_blueprint")
        pprint(_blueprint)
        print()
        count = dict()
        for material in _blueprint["contained_items"]:  # these could be duplicates. get a count.
            print("material")
            pprint(material)
            if material["ident"] in count.keys():
                count["ident"]["amount"] = count["ident"]["amount"] + 1
            else:
                count[material["ident"]] = dict()
                count[material["ident"]]["amount"] = 1

        for component in _recipe["components"]:
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
                _tile["items"].append(_newobject)
            if _blueprint["type_of"] == "Furniture":
                _newobject = Furniture(_recipe["result"])
                _tile["furniture"] = _newobject
            if _blueprint["type_of"] == "Terrain":
                _newobject = Terrain(_recipe["result"])
                _tile["terrain"] = _newobject
            _tile["items"].remove(_blueprint)  # remove it from the world.
            self.callback_client_send(connection_object, "Finished working on blueprint!\r\n")
            print("Completed blueprint")
            return
        return

    # catch-all for bash/smash/break
    # since we bash in a direction we need to check what's in the tile.
    def bash(self, owner, target):
        _tile = self.worldmap.get_tile_by_position(self.characters[owner]["position"])
        # strength = creature strength.
        if _tile["furniture"] is not None:
            _furniture = self.FurnitureManager.FURNITURE_TYPES[_tile["furniture"]["ident"]]
            if target in _furniture["name"].split(" "):
                if "bash" in _furniture.keys():
                    for item in _furniture["bash"]["items"]:
                        self.worldmap.put_object_at_position(Item(item["item"]), self.characters[owner]["position"])
                    _tile["furniture"] = None

        return

    def compute_turn(self):
        # this function handles overseeing all character and creature movement, attacks, and interactions

        for _, character in self.characters.items():  # Player's characters
            if len(character["command_queue"]) > 0:
                self.process_creature_command_queue(character)

        for _, monster in self.monsters.items():  # Computer controlled Creatures
            if len(monster["command_queue"]) > 0:
                self.process_creature_command_queue(monster)

        # Now that characters and monsters have moved and done their actions let's check
        # for any possible combat that may have occurred.
        for _, character in self.characters.items():
            # get all 4 directions and check for enemies.
            #pprint(character)
            # if enemy found do an attack with wielded weapon or bare hands.
            pass
            # continue to next character or monster

        for _, monster in self.monsters.items():
            # get all 4 directions and check for enemies.
            #pprint(monster)
            pass
            # if enemy found do an attack with wielded weapon or bare hands.

            # continue to next character or monster

        # for fire in self.fires: #TODO

        # now that we've processed what everything wants to do we can return.
        return

    def generate_and_apply_city_layout(self, city_size):
        city_layout = self.worldmap.generate_city(city_size)
        # for every 1 city size it's 13 tiles across and high
        for j in range(city_size * 13 - 1):
            for i in range(city_size * 13 - 1):
                _chunk = server.worldmap.get_chunk_by_position(Position(i, j, 0))
                if _chunk["was_loaded"] is False:
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
                            ):  # TODO: make sure the roads line up right.
                                if city_layout[int(i + 1)][int(j)] != "R":
                                    json_file = "./data/json/mapgen/road/city_road_3_way_s0.json"
                                elif city_layout[int(i - 1)][int(j)] != "R":
                                    json_file = "./data/json/mapgen/road/city_road_3_way_p0.json"
                                elif city_layout[int(i)][int(j + 1)] != "R":
                                    json_file = "./data/json/mapgen/road/city_road_3_way_d0.json"
                                elif city_layout[int(i)][int(j - 1)] != "R":
                                    json_file = "./data/json/mapgen/road/city_road_3_way_u0.json"
                            elif attached_roads <= 2:
                                if city_layout[int(i + 1)][int(j)] == "R":
                                    json_file = (
                                        "./data/json/mapgen/road/city_road_h.json"
                                    )
                                elif city_layout[int(i - 1)][int(j)] == "R":
                                    json_file = (
                                        "./data/json/mapgen/road/city_road_h.json"
                                    )
                                elif city_layout[int(i)][int(j + 1)] == "R":
                                    json_file = (
                                        "./data/json/mapgen/road/city_road_v.json"
                                    )
                                elif city_layout[int(i)][int(j - 1)] == "R":
                                    json_file = (
                                        "./data/json/mapgen/road/city_road_v.json"
                                    )
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
    port = int(defaultConfig.get("listen_port", args.port))

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

    sys.exit(mainloop(server=server, configParser=configParser))
