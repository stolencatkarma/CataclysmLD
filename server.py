#/usr/bin/env python3

import argparse
import json
import os
import random
import time
import pprint
import configparser
# import logging.config

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


# when the character pulls up the OverMap.
class OverMap:
    def __init__(self):  # the ident of the character who owns this overmap.
        # over map size is the worldmap size
        # build the overmap from seen tiles, roadmaps, maps.
        # if a character sees a chunk loaded it's safe to say they 'saw' that overmap tile.
        return


class Server(MastermindServerTCP):
    def __init__(self, config, logger=None):
        MastermindServerTCP.__init__(self, 0.5, 0.5, 300.0)
        self._config = config
        if logger is None:
            pass
        else:
            self._log = logger

        # all the Character()s that exist in the world whether connected or not.
        self.characters = dict()

        self.localmaps = dict()  # the localmaps for each character.
        self.overmaps = dict()  # the dict of all overmaps by character
        # self.options = Options()
        self.calendar = Calendar(0, 0, 0, 0, 0, 0)  # all zeros is the epoch
        # self.options.save()
        # create this many chunks in x and y (z is always 1 (level 0)
        # for genning the world. we will build off that for caverns and ant stuff and z level buildings.
        self.worldmap = Worldmap()
        self.RecipeManager = RecipeManager()
        self.ProfessionManager = ProfessionManager()
        self.MonsterManager = MonsterManager()
        self.ItemManager = ItemManager()
        self.FurnitureManager = FurnitureManager()
        self.TileManager = TileManager()

    def get_connections(self):
        return self._mm_connections

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
            print(path[len(path) - 1])
            path.append(next_pos)

            if len(path) > 9:
                break

        return path

    def find_spawn_point_for_new_character(self):
        _possible = list()
        for _, chunk in self.worldmap["CHUNKS"].items():
            for tile in chunk["tiles"]:
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
        #else:
        #    print("ERROR: Couldn't find spawn point for new character!")
        #    return None

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
                                if (
                                    "container_type"
                                    in self.ItemManager.ITEM_TYPES[item_ident]
                                ):
                                    bodypart["slot0"] = Container(
                                        item_ident,
                                        self.ItemManager.ITEM_TYPES[item_ident],
                                    )  # need to pass the reference to load the item with data.
                                else:
                                    bodypart["slot0"] = Item(
                                        item_ident,
                                        self.ItemManager.ITEM_TYPES[item_ident],
                                    )  # need to pass the reference to load the item with data.
                                break
                            elif bodypart["slot1"] is None:
                                if (
                                    "container_type"
                                    in self.ItemManager.ITEM_TYPES[item_ident]
                                ):
                                    bodypart["slot1"] = Container(
                                        item_ident,
                                        self.ItemManager.ITEM_TYPES[item_ident],
                                    )  # need to pass the reference to load the item with data.
                                else:
                                    bodypart["slot1"] = Item(
                                        item_ident,
                                        self.ItemManager.ITEM_TYPES[item_ident],
                                    )  # need to pass the reference to load the item with data.
                                break
                    else:
                        self._log.warn(
                            "character needed an item but no free slots found"
                        )
            elif (
                key == "items_in_containers"
            ):  # load the items_in_containers into their containers we just created.
                for location_ident, item_ident in value.items():
                    # first find the location_ident so we can load a new item into it.
                    for bodypart in self.characters[character]["body_parts"]:
                        if bodypart["slot0"] is not None:
                            if (
                                isinstance(bodypart["slot0"], Container)
                                and bodypart["slot0"]["ident"] == location_ident
                            ):  # uses the first one it finds, maybe check if it's full?
                                bodypart["slot0"].add_item(
                                    Item(
                                        item_ident,
                                        self.ItemManager.ITEM_TYPES[item_ident],
                                    )
                                )
                            if (
                                isinstance(bodypart["slot1"], Container)
                                and bodypart["slot1"]["ident"] == location_ident
                            ):  # uses the first one it finds, maybe check if it's full?
                                bodypart["slot1"].add_item(
                                    Item(
                                        item_ident,
                                        self.ItemManager.ITEM_TYPES[item_ident],
                                    )
                                )
        path = str(
            "./accounts/"
            + str(ident)
            + "/"
            + str("characters")
            + "/"
            + str(character)
            + ".character"
        )

        with open(path, "w") as fp:
            json.dump(self.characters[character]["name"], fp)
            # pprint.pprint(_pickled)

            print("New character added to world: {}".format(character))

    # where most data is handled from the client.
    def callback_client_handle(self, connection_object, data):
        # print("Server: Recieved data {} from client {}.".format(data, connection_object.address))

        # quit on disconnect signal.
        if data == "disconnect":
            # print('got disconnect signal')
            connection_object.terminate()
            return

        # LOGIN is the default state when a new connection is established.
        if connection_object.state == "LOGIN":
            # this will be the client's username.
            connection_object.state = "LOGIN2"
            connection_object.username = data
            self.callback_client_send(connection_object, "Password? >\r\n")
            return

        if connection_object.state == "LOGIN2":
            # print(connection_object.username + " entered LOGIN2")
            # this is the client's password.
            connection_object.password = data

            # check whether this username has an account.
            _path = "./accounts/" + connection_object.username + "/"
            if os.path.isdir("./accounts/" + connection_object.username):
                # account exists. check the sent password against the saved one.
                with open(str(_path + "SALT"), "r") as _salt:
                    with open(str(_path + "HASHED_PASSWORD"), "r") as _hashed_password:
                        # read the password hashed
                        _check = hashPassword(connection_object.password, _salt.read())
                        _check2 = _hashed_password.read()
                        if _check == _check2:
                            print("password accepted for " + connection_object.username)

                        else:
                            self.callback_client_send(connection_object, "Password NOT accepted for " + connection_object.username)
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

                _salt = makeSalt()
                with open(str(_path + "SALT"), "w") as f:
                    # write the password salt
                    f.write(str(_salt))

                with open(str(_path + "HASHED_PASSWORD"), "w") as f:
                    # write the password hashed
                    f.write(str(hashPassword(connection_object.password, _salt)))

                _path = "./accounts/" + connection_object.username + "/characters/"
                try:
                    os.mkdir(_path)
                except OSError:
                    print("Creation of the directory %s failed" % _path)
                else:
                    print("Successfully created the directory %s " % _path)

            _message = "Login Accepted! Moving us to Character Select.\r\n"
            connection_object.state = "CHOOSE_CHARACTER"
            self.callback_client_send(connection_object, _message)

        if connection_object.state == "CHOOSE_CHARACTER":
            # first option is always create new character
            idx = 2
            self.callback_client_send(connection_object, '1.) Create New >\r\n')
            for root, _, files in os.walk("./accounts/" + connection_object.username + "/characters/"):
                for file_data in files:
                    if file_data.endswith(".character"):
                        self.callback_client_send(connection_object, str(idx) + '.) ' + file_data.split(".")[0] + '\r\n')
                        idx = idx + 1

            self.callback_client_send(connection_object, "Choice? >\r\n")
            connection_object.state = "CHOOSING_CHARACTER"
            return

        if connection_object.state == "CHOOSING_CHARACTER":
            # the client has been shown the list of characters. they now select to make a new one or choose a existing one.
            if data == "1":
                # client has chosen to create a new character.
                connection_object.state = "CREATE_CHARACTER1"
                self.callback_client_send(connection_object, "Name? >\r\n")
                return
            else:
                idx = 2
                # send the current localmap to the player choosing the character
                for root, _, files in os.walk("./accounts/" + connection_object.username + "/characters/"):
                    for file_data in files:
                        if file_data.endswith(".character"):
                            if int(data) == idx:
                                connection_object.character = file_data.split(".")[0]
                                connection_object.state = "CONNECTED"
                                self.callback_client_send(connection_object, "Entering the Darkness as " + connection_object.character + "\r\n")
                                self.callback_client_send(connection_object, "try help for a list of commands." + "\r\n")
                                # TODO: send the first map update.
                                return
                            else:
                                idx = idx + 1
            # player sent an incorrect option
            return

        if connection_object.state == "CREATE_CHARACTER1":
            if not data in self.characters:
                # this character doesn't exist in the world yet.
                self.handle_new_character(connection_object.username, data)
                print("Server: character created: {} From client {}.".format( data, connection_object.address))
            else:
                print("Server: character NOT created. Already Exists")
            connection_object.state = "CHOOSE_CHARACTER"


        ########################################################
        ## Main Loop After a Client connects with a Character. #
        ########################################################
        # Once players have chosen a character they are CONNECTED and can start sending character commands.
        if connection_object.state == "CONNECTED":
            # player sent an empty command.
            if len(data) < 1:
                self.localmaps[connection_object.character] = self.worldmap.get_chunks_near_position(self.characters[connection_object.character]['position'])
                cx = self.characters[connection_object.character]['position']['x']
                cy = self.characters[connection_object.character]['position']['y']
                cz = self.characters[connection_object.character]['position']['z']
                send_map = dict()
                for i in range(39):
                    send_map[i] = dict()
                    for j in range(39):
                        send_map[i][j] = '.'  # null by default then gets filled.

                min_x = None
                min_y = None
                for chunk in self.localmaps[connection_object.character]:
                    for tile in chunk['tiles']:
                        x = tile['position']['x']
                        y = tile['position']['y']
                        z = tile['position']['z']
                        if min_x is None:
                            min_x = x
                            min_y = y
                            continue
                        if x < min_x:
                            min_x = x
                        if y < min_y:
                            min_y = y

                # print("min_x: " + str(min_x))
                # print("min_y: " + str(min_y))
                pre_color = "\u001b[38;5;"
                post_color = "\u001b[0m"
                for chunk in self.localmaps[connection_object.character]:
                    for tile in chunk['tiles']:
                        # translate localmap to a terminal friendly map and send it to the client.
                        # order the tiles by x, y, ignore z levels not on current level.
                        # send map to client line by line centered on the player.
                        x = tile['position']['x']
                        y = tile['position']['y']
                        z = tile['position']['z']
                        if cz != z:
                            continue
                        # print("trying " + str(x - min_x) + ", " + str(y - min_y))
                        t_id = self.TileManager.TILE_TYPES[tile['terrain']['ident']]
                        send_map[x - min_x][y - min_y] = pre_color + t_id['color'] + "m" + t_id['symbol'] + post_color  # concat color and symbol

                        if tile['furniture'] is not None:
                            f_id = self.FurnitureManager.FURNITURE_TYPES[tile['furniture']['ident']]
                            send_map[x - min_x][y - min_y] = pre_color + f_id['color'] + "m" + f_id['symbol'] + post_color.lower()
                        if tile['creature'] is not None:
                            send_map[x - min_x][y - min_y] = tile['creature']['tile_ident'][:1].upper()

                next_line = ""
                for i in range(39):
                    for j in range(39):
                        next_line = next_line + send_map[j][i]
                    self.callback_client_send(connection_object, next_line + '\r\n')
                    next_line = ''

                self.send_prompt(connection_object)
                return

            # try to parse the data sent for arguments.
            data_list = data.split(" ")
            _command = dict()
            _command["args"] = list()
            _command["command"] = data_list.pop(0)
            for item in data_list:
                _command["args"].append(item)

            # all the commands that are actions need to be put into the command_queue
            # then we will loop through the queue each turn and process the actions.
            if _command["command"] == "move":
                self.characters[connection_object.character]["command_queue"].append(Action(connection_object.character, connection_object.character, "move", _command["args"]))
                self.callback_client_send(connection_object, "You head " + _command['args'][0] + ".\r\n")
                self.send_prompt(connection_object)
                return

            if _command["command"] == "bash":
                _target = _command["args"][0]
                _action = Action(connection_object.character, _target, 'bash', _command["args"])
                self.characters[connection_object.character]["command_queue"].append(_action)
                self.callback_client_send(connection_object, "You break down " + _target + " for its components.")
                self.send_prompt(connection_object)
                return

            if _command["command"] == "look":
                _tile = self.worldmap.get_tile_by_position(self.characters[connection_object.character]["position"])
                # pprint.pprint(_tile)
                self.callback_client_send(connection_object, "---- Items ----\r\n")
                for item in _tile["items"]:
                    _item = self.ItemManager.ITEM_TYPES[item["ident"]]
                    self.callback_client_send(connection_object, _item["name"] + "\r\n")
                self.callback_client_send(connection_object, "-- Furniture --\r\n")
                if _tile["furniture"] is not None:
                    _furniture = self.FurnitureManager.FURNITURE_TYPES[_tile["furniture"]["ident"]]
                    self.callback_client_send(connection_object, _furniture["name"] + ": " + _furniture["description"] + "\r\n")

                # send_prompt sends the client's character's stats after each request
                self.send_prompt(connection_object)
                return

            if _command["command"] == "character": # character sheet
                _character = self.characters[connection_object.character]
                self.callback_client_send(connection_object, "### Character Sheet\r\n")
                self.callback_client_send(connection_object, "# Name: " + _character["name"] + "\r\n")
                self.callback_client_send(connection_object, "#\r\n")
                self.callback_client_send(connection_object, "# Strength: " + str(_character["strength"]) + "\r\n")
                self.callback_client_send(connection_object, "# Dexterity: " + str(_character["dexterity"]) + "\r\n")
                self.callback_client_send(connection_object, "# Intelligence: " + str(_character["intelligence"]) + "\r\n")
                self.callback_client_send(connection_object, "# Perception: " + str(_character["perception"]) + "\r\n")
                self.callback_client_send(connection_object, "# Constitution: " + str(_character["constitution"]) + "\r\n")
                for body_part in _character["body_parts"]:
                    # pprint.pprint(body_part)
                    self.callback_client_send(connection_object, "# " + body_part["ident"] + "\r\n")
                    if body_part["slot0"] is not None:
                        self.callback_client_send(connection_object, "#  " + body_part["slot0"]["ident"] + "\r\n")
                    if body_part["slot1"] is not None:
                        self.callback_client_send(connection_object, "#  " + body_part["slot1"]["ident"] + "\r\n")
                    if "slot_equipped" in _character:
                        if body_part["slot_equipped"] is not None:
                            self.callback_client_send(connection_object, "#  " + body_part["slot_equipped"]["ident"] + "\r\n")

                self.send_prompt(connection_object)
                return

            if _command["command"] == "craft":  # 2-3 args (craft, <recipe>, direction)
                # args 0 is ident args 1 is direction.
                print("creating blueprint " + _command["args"][0] + " for character " + connection_object.character)
                # blueprint rules
                # * there should be blueprints for terrain, furniture, items, and anything else that takes a slot up in a tile.
                # * they act as placeholders and then 'transform' into the type they are once completed.
                # Blueprint(type, recipe)
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

                _recipe = server.RecipeManager.RECIPE_TYPES[_command["args"][0]]
                type_of = _recipe["type_of"]
                bp_to_create = Blueprint(type_of, _recipe)

                self.worldmap.put_object_at_position(
                    bp_to_create, position_to_create_at
                )

            if _command["command"] == "take": # take an item from current tile and put it in players open inventory. (take, <item>)
                _from_pos = self.characters(connection_object.character)["position"]
                _item_ident = _command["args"][0]
                _from_item = None
                _open_containers = []
                # find the item that the character is requesting.
                for item in self.worldmap.get_tile_by_position(_from_pos)["items"]:
                    if item["ident"] == _item_ident:
                        # this is the item or at least the first one that matches the same ident.
                        _from_item = item  # save a reference to it to use.
                        break

                # we didn't find one, character sent bad information (possible hack?)
                if _from_item is None:
                    return

                # make a list of open_containers the character has to see if they can pick it up.
                for bodyPart in self.characters(connection_object.character)["body_parts"]:
                    if (
                        bodyPart["slot0"] is not None
                        and isinstance(bodyPart["slot0"], Container)
                        and bodyPart["slot0"].opened == "yes"
                    ):
                        _open_containers.append(bodyPart["slot0"])
                    if (
                        bodyPart["slot1"] is not None
                        and isinstance(bodyPart["slot1"], Container)
                        and bodyPart["slot1"].opened == "yes"
                    ):
                        _open_containers.append(bodyPart["slot1"])

                if len(_open_containers) <= 0:
                    return  # no open containers.

                # check if the character can carry that item.
                for container in _open_containers:
                    # then find a spot for it to go (open_containers)
                    if container.add_item(item):  # if it added it sucessfully.
                        # remove it from the world.
                        for item in self.worldmap.get_tile_by_position(_from_pos)[
                            "items"
                        ][:]:
                            if item["ident"] == _item_ident:
                                self.worldmap.get_tile_by_position(_from_pos)[
                                    "items"
                                ].remove(item)
                                break
                        return
                    else:
                        print("could not add item to character inventory.")

            if _command["command"] == "transfer": # (transfer, <item_ident>, <container_ident>) *Requires two open containers or taking from tile['items'].
                # client sends 'hey server. can you move item from this to that?'
                _character_requesting = self.characters[connection_object.character]

                _item = None  # the item we are moving. parse this

                # the container the item is coming from. parse this
                # either the player's character inventory or the player occupied tile["items"]
                _from_container = None

                # the container the item will end up. parse this as well.
                _to_container = None

                # find _from_container and _item, either equipped containers or items on the ground.
                for ground_item in self.worldmap.get_tile_by_position(_character_requesting["position"])["items"][:]: # parse copy
                    # check if ground item is a container or blueprint
                    #
                    # check if item is laying on the ground. tile["items"]
                    if _command["args"][0] in ground_item["name"].split(" "): # found the item on the ground by parsing it's ["name"]
                        _item = ground_item
                        _from_container = self.worldmap.get_tile_by_position(_character_requesting["position"])["items"]
                        break
                # if we didn't find it there let's check the player's own inventory.
                if _item is None:
                    for bodypart in _character_requesting["body_parts"][:]:
                        for body_item in bodypart["slot0"]:
                            if isinstance(body_item, Container): # could be a container or armor. only move to a container.
                                for containted_item in body_item["contained_items"]:
                                    if _command["args"][0] in contained_item["name"].split(" "):
                                        _item = body_item
                                        _from_container = bodypart["slot0"]
                                        break
                        for body_item in bodypart["slot1"]:
                            if isinstance(body_item, Container): # could be a container or armor. only move to a container.

                                for containted_item in body_item["contained_items"]:
                                    if _command["args"][0] in contained_item["name"].split(" "):
                                        _item = body_item
                                        _from_container = bodypart["slot1"]
                                        break
                    else:
                        self.callback_client_send(connection_object, "Couldn't find item on ground or in open containers.\r\n")
                        return

                # a blueprint is a type of container but can't be moved from it's world position.
                # TODO: Move to "dump" command blueprints are containers.
                #    for item in self.worldmap.get_tile_by_position(_position)["items"]:
                #        # only one blueprint allowed per space.
                #        if isinstance(item) == Blueprint:
                #            _from_list = item.contained_items
                #            _from_list.remove(_item)
                #            _to_list.append(_item)
                #            return

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
            if _command["command"] == "hotbar":
                return

            if _command["command"] == "recipes":
                if len(_command["args"]) == 0:
                    # send the player their character's known recipes.
                    _character = self.characters[connection_object.character]
                    self.callback_client_send(connection_object, "--- Known Recipes ---\r\n")

                    for recipe in _character["known_recipes"]:
                        self.callback_client_send(connection_object, recipe + "\r\n")
                else: # send the specific recipe.
                    try:
                        _recipe = _command["args"][0]
                        self.callback_client_send(connection_object, "--- Recipe ---\r\n")
                        self.callback_client_send(connection_object, self.RecipeManager.RECIPE_TYPES[_recipe]["result"] + "\r\n")
                        for component in self.RecipeManager.RECIPE_TYPES[_recipe]["components"]:
                            self.callback_client_send(connection_object, " " + str(component["amount"]) + ": " + component["ident"] + "\r\n")
                        return
                    except:
                        # recipe doesn't exist.
                        self.callback_client_send(connection_object, "No known recipe.\r\n")
                self.send_prompt(connection_object)
                return

            if _command["command"] == "help":
                self.callback_client_send(connection_object, "Common commands are look, move, bash, craft, take, transfer, recipes.\r\n")
                self.callback_client_send(connection_object, "Furniture can be bashed for recipe components.\r\n")
                self.callback_client_send(connection_object, "recipes can be \'craft\'ed and then \'work\'ed on.\r\n")
                self.send_prompt(connection_object)
                return

            if _command["command"] == "work":
                # TODO: work on a blueprint checking for materials in a direction.
                pass

            if _command["command"] == "dump":
                # TODO: check for items in a blueprint from the direction and drop the items in the blueprint that are needed.
                pass

            # fallback to not knowing wtf the player is talking about.
            self.callback_client_send(connection_object, "I am not sure what you are trying to do.\r\n")
            self.send_prompt(connection_object)

        return super(Server, self).callback_client_handle(connection_object, data)

    def send_prompt(self, connection_object):
        _character = self.characters[connection_object.character]
        # send body health as [*******] of varying colors of wounds.
        pre_color = "\u001b[38;5;150m"
        post_color = "\u001b[0m"

        self.callback_client_send(connection_object, pre_color + "(" + str(_character["position"]) + ")" + "(" + _character["name"] + ") > " + post_color + "\r\n")

    def callback_client_send(self, connection_object, data, compression=False):
        return super(Server, self).callback_client_send(connection_object, data, compression)

    def callback_connect_client(self, connection_object):
        # we need to have a login system to handle raw telnet and MUD clients.
        print("Server: Client from {} connected.".format(connection_object.address))
        # send the user a login prompt
        connection_object.state = "LOGIN"
        # return super(Server, self).callback_connect_client(connection_object)
        self.callback_client_send(connection_object, "Username? >\r\n")
        return

    def callback_disconnect_client(self, connection_object):
        print("Server: Client from {} disconnected.".format(
            connection_object.address))
        return super(Server, self).callback_disconnect_client(connection_object)

    def process_creature_command_queue(self, creature):
        actions_to_take = creature["actions_per_turn"]
        print("processing " + str(creature["position"]))
        # iterate a copy so we can remove on the fly.
        for action in creature["command_queue"][:]:
            if actions_to_take == 0:
                return  # this creature is out of action points.

            # this creature can't act until x turns from now.
            if creature["next_action_available"] > 0:
                creature["next_action_available"] = (
                    creature["next_action_available"] - 1
                )
                return
            # if we get here we can process a single action
            if action["type"] == "move":
                # pprint.pprint(action["args"])
                actions_to_take = actions_to_take - 1  # moving costs 1 ap.
                if action["args"][0] == "south":
                    if self.worldmap.move_creature_from_position_to_position(
                        self.characters[creature["name"]],
                        self.characters[creature["name"]]["position"],
                        Position(
                            self.characters[creature["name"]]["position"]["x"],
                            self.characters[creature["name"]]["position"]["y"] + 1,
                            self.characters[creature["name"]]["position"]["z"],
                        ),
                    ):
                        self.characters[creature["name"]]["position"] = Position(
                            self.characters[creature["name"]]["position"]["x"],
                            self.characters[creature["name"]]["position"]["y"] + 1,
                            self.characters[creature["name"]]["position"]["z"],
                        )
                    creature["command_queue"].remove(action)
                if action["args"][0] == "north":
                    if self.worldmap.move_creature_from_position_to_position(
                        self.characters[creature["name"]],
                        self.characters[creature["name"]]["position"],
                        Position(
                            self.characters[creature["name"]]["position"]["x"],
                            self.characters[creature["name"]]["position"]["y"] - 1,
                            self.characters[creature["name"]]["position"]["z"],
                        ),
                    ):
                        self.characters[creature["name"]]["position"] = Position(
                            self.characters[creature["name"]]["position"]["x"],
                            self.characters[creature["name"]]["position"]["y"] - 1,
                            self.characters[creature["name"]]["position"]["z"],
                        )
                    creature["command_queue"].remove(action)
                if action["args"][0] == "east":
                    if self.worldmap.move_creature_from_position_to_position(
                        self.characters[creature["name"]],
                        self.characters[creature["name"]]["position"],
                        Position(
                            self.characters[creature["name"]]["position"]["x"] + 1,
                            self.characters[creature["name"]]["position"]["y"],
                            self.characters[creature["name"]]["position"]["z"],
                        ),
                    ):
                        self.characters[creature["name"]]["position"] = Position(
                            self.characters[creature["name"]]["position"]["x"] + 1,
                            self.characters[creature["name"]]["position"]["y"],
                            self.characters[creature["name"]]["position"]["z"],
                        )
                    creature["command_queue"].remove(action)
                if action["args"][0] == "west":
                    if self.worldmap.move_creature_from_position_to_position(
                        self.characters[creature["name"]],
                        self.characters[creature["name"]]["position"],
                        Position(
                            self.characters[creature["name"]]["position"]["x"] - 1,
                            self.characters[creature["name"]]["position"]["y"],
                            self.characters[creature["name"]]["position"]["z"],
                        ),
                    ):
                        self.characters[creature["name"]]["position"] = Position(
                            self.characters[creature["name"]]["position"]["x"] - 1,
                            self.characters[creature["name"]]["position"]["y"],
                            self.characters[creature["name"]]["position"]["z"],
                        )
                    creature["command_queue"].remove(action)
                if action["args"][0] == "up":
                    if self.worldmap.move_creature_from_position_to_position(
                        self.characters[creature["name"]],
                        self.characters[creature["name"]]["position"],
                        Position(
                            self.characters[creature["name"]]["position"]["x"],
                            self.characters[creature["name"]]["position"]["y"],
                            self.characters[creature["name"]]["position"]["z"] + 1,
                        ),
                    ):
                        self.characters[creature["name"]]["position"] = Position(
                            self.characters[creature["name"]]["position"]["x"],
                            self.characters[creature["name"]]["position"]["y"],
                            self.characters[creature["name"]]["position"]["z"] + 1,
                        )
                    creature["command_queue"].remove(action)
                if action["args"][0] == "down":
                    if self.worldmap.move_creature_from_position_to_position(
                        self.characters[creature["name"]],
                        self.characters[creature["name"]]["position"],
                        Position(
                            self.characters[creature["name"]]["position"]["x"],
                            self.characters[creature["name"]]["position"]["y"],
                            self.characters[creature["name"]]["position"]["z"] - 1,
                        ),
                    ):
                        self.characters[creature["name"]]["position"] = Position(
                            self.characters[creature["name"]]["position"]["x"],
                            self.characters[creature["name"]]["position"]["y"],
                            self.characters[creature["name"]]["position"]["z"] - 1,
                        )
                    creature["command_queue"].remove(action)
            elif action["type"] == "bash":
                # pprint.pprint(action)
                actions_to_take = actions_to_take - 1  # bashing costs 1 ap.
                self.bash(action["owner"], action["target"])
                self.localmaps[creature["name"]] = self.worldmap.get_chunks_near_position(self.characters[creature["name"]]["position"])
                creature["command_queue"].remove(action)

    # catch-all for bash/smash/break
    # since we bash in a direction we need to check what's in the tile.
    def bash(self, owner, target):
        _tile = self.worldmap.get_tile_by_position(self.characters[owner]["position"])
        # strength = creature strength.
        if _tile["furniture"] is not None:
            _furniture = self.FurnitureManager.FURNITURE_TYPES[_tile["furniture"]["ident"]]
            if target in _furniture["name"].split(" "):
                for item in _furniture["bash"]["items"]:
                    self.worldmap.put_object_at_position(Item(self.ItemManager.ITEM_TYPES[item["item"]]["ident"], self.ItemManager.ITEM_TYPES[item["item"]]), self.characters[owner]["position"])
                _tile["furniture"] = None
                # TODO: check 4 directions for target
        return

    def compute_turn(self):
        # this function handles overseeing all creature movement, attacks, and interactions

        # init a list for all our found lights around characters.
        for _, chunks in self.localmaps.items():
            for chunk in chunks:  # characters typically see 9 chunks
                for tile in chunk["tiles"]:
                    tile["lumens"] = 0  # reset light levels.

        for _, chunks in self.localmaps.items():
            for chunk in chunks:  # characters typically see 9 chunks and 1 z level
                for tile in chunk["tiles"]:
                    for item in tile["items"]:
                        if isinstance(item, Blueprint):
                            continue
                        # this item produces light.
                        if("flags" in self.ItemManager.ITEM_TYPES[item["ident"]]):
                            for flag in self.ItemManager.ITEM_TYPES[item["ident"]]["flags"]:
                                if flag.split("_")[0] == "LIGHT":
                                    for (
                                        tile,
                                        distance,
                                    ) in self.worldmap.get_tiles_near_position(
                                        tile["position"], int(
                                            flag.split("_")[1])
                                    ):
                                        tile["lumens"] = tile["lumens"] + int(
                                            int(flag.split("_")[1]) - distance
                                        )
                    if tile["furniture"] is not None:
                        for key in self.FurnitureManager.FURNITURE_TYPES[tile["furniture"]["ident"]]:
                            if key == "flags":
                                for flag in self.FurnitureManager.FURNITURE_TYPES[
                                    tile["furniture"]["ident"]]["flags"]:
                                    # this furniture produces light.
                                    if flag.split("_")[0] == "LIGHT":
                                        for (
                                            tile,
                                            distance,
                                        ) in self.worldmap.get_tiles_near_position(
                                            tile["position"], int(
                                                flag.split("_")[1])
                                        ):
                                            tile["lumens"] = tile["lumens"] + int(
                                                int(flag.split("_")
                                                    [1]) - distance
                                            )
                                        break
        # we want a list that contains all the non-duplicate creatures on all localmaps around characters.
        creatures_to_process = list()
        for _, chunks in self.localmaps.items():
            for chunk in chunks:  # characters typically get 9 chunks
                for tile in chunk["tiles"]:
                    if (
                        tile["creature"] is not None
                        and tile["creature"] not in creatures_to_process
                    ):
                        creatures_to_process.append(tile["creature"])

        for creature in creatures_to_process:
            # as long as there at least one we'll pass it on and let the function handle how many actions they can take.
            if len(creature["command_queue"]) > 0:
                self.process_creature_command_queue(creature)

        # now that we've processed what everything wants to do we can return.

    def generate_and_apply_city_layout(self, city_size):
        city_layout = self.worldmap.generate_city(city_size)
        # for every 1 city size it's 13 tiles across and high
        for j in range(city_size * 13):
            for i in range(city_size * 13):
                _chunk = server.worldmap.get_chunk_by_position(Position(i, j, 0))
                if _chunk["was_loaded"] is False:
                    if city_layout[i][j] == "r":
                        json_file = random.choice(os.listdir("./data/json/mapgen/residential/"))
                        server.worldmap.build_json_building_on_chunk("./data/json/mapgen/residential/" + json_file,
                            Position(i * _chunk["chunk_size"], j * _chunk["chunk_size"], 0))
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


# do this if the server was started up directly.
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
    #logging.config.fileConfig(args.config)
    #log = logging.getLogger("root")

    server = Server(logger=None, config=defaultConfig)
    server.connect(ip, port)
    server.accepting_allow()
    print("Server is listening at {}:{}".format(ip, port))

    dont_break = True
    # 0.5 is twice as fast, 2.0 is twice as slow
    time_offset = float(defaultConfig.get("time_offset", 1.0))
    last_turn_time = time.time()
    citySize = int(defaultConfig.get("city_size", 1))
    # print('City size: {}'.format(citySize))

    # TODO: add variable to make it at world position.
    server.generate_and_apply_city_layout(citySize)

    time_per_turn = int(defaultConfig.get("time_per_turn", 1))
    # print('time_per_turn: {}'.format(time_per_turn))
    spin_delay_ms = float(defaultConfig.get("time_per_turn", 0.001))
    # print('spin_delay_ms: {}'.format(spin_delay_ms))

    for character in server.worldmap.get_all_characters():
       server.characters[character["name"]] = character
    print("found " + str(len(server.characters)) + " characters in the world.")

    print("Started Cataclysm: Looming Darkness. Clients may now connect.")
    try:
        while dont_break:
            # keep up with the time offset but never go faster than it.
            if (time.time() - last_turn_time < time_offset):
                pass
            else:
                # a turn is normally one second.
                server.calendar.advance_time_by_x_seconds(time_per_turn)

                # where all queued creature actions get taken care of, as well as physics engine stuff.
                server.compute_turn()

                # if the worldmap in memory changed update it on the hard drive.
                server.worldmap.handle_chunks()

                # TODO: unload from memory chunks that have no updates required.
                # (such as no monsters, Characters, or fires)
                last_turn_time = time.time()  # based off of system clock.

    except (KeyboardInterrupt):
        print("Cleaning up before exiting.")
        server.accepting_disallow()
        server.disconnect_clients()
        server.disconnect()
        # if the worldmap in memory changed update it on the hard drive.
        server.worldmap.handle_chunks()
        dont_break = False
        print("Done cleaning up.")
