#!/usr/bin/env python3

import argparse
import json
import os
import random
import sys
import time
import pprint
import configparser
import logging.config
import pickle
import jsonpickle
from collections import defaultdict

from Mastermind._mm_server import MastermindServerTCP
from src.action import Action
from src.blueprint import Blueprint
from src.calendar import Calendar
from src.command import Command
from src.furniture import Furniture, FurnitureManager
from src.item import Container, Item
from src.options import Options
from src.character import Character
from src.position import Position
from src.recipe import Recipe, RecipeManager
from src.terrain import Terrain
from src.profession import ProfessionManager, Profession
from src.monster import MonsterManager
from src.worldmap import Worldmap
from src.passhash import makeSalt, hashPassword


class OverMap:  # when the character pulls up the OverMap. a OverMap for each character will have to be stored for undiscovered areas and when they use maps.
    def __init__(self):  # the ident of the character who owns this overmap.
        # over map size is the worldmap size
        # build the overmap from seen tiles, roadmaps, maps.
        # if a character sees a chunk loaded it's safe to say they 'saw' that overmap tile.
        return


class Server(MastermindServerTCP):
    def __init__(self, config, logger=None):
        MastermindServerTCP.__init__(self, 0.5, 0.5, 300.0)
        self._config = config
        if logger == None:
            logging.basicConfig()
            self._log = logging.getLogger("root")
            self._log.warn(
                "Basic logging configuration fallback used because no logger defined."
            )

        else:
            self._log = logger

        # all the Character()s that exist in the world whether connected or not.
        self.characters = dict()

        self.localmaps = dict()  # the localmaps for each character.
        self.overmaps = dict()  # the dict of all overmaps by character.name
        # self.options = Options()
        self.calendar = Calendar(0, 0, 0, 0, 0, 0)  # all zeros is the epoch
        # self.options.save()
        # create this many chunks in x and y (z is always 1 (level 0) for genning the world. we will build off that for caverns and ant stuff and z level buildings.
        self.worldmap = Worldmap(26)
        self.RecipeManager = RecipeManager()
        self.ProfessionManager = ProfessionManager()
        self.MonsterManager = MonsterManager()
        self.ItemManager = self.worldmap.ItemManager
        self.FurnitureManager = self.worldmap.FurnitureManager

    def get_connections(self):
        return self._mm_connections

    def calculate_route(self, pos0, pos1, consider_impassable=True):
        # normally we will want to consider impassable terrain in movement calculations. Creatures that can walk or break through walls don't need to though.
        reachable = [pos0]
        explored = []

        while len(reachable) > 0:
            position = random.choice(
                reachable
            )  # get a random reachable position #TODO: be a little more intelligent about picking the best reachable position.

            # If we just got to the goal node. return the path.
            if position == pos1:
                path = []
                while position != pos0:
                    path.append(position)
                    position = position.previous
                ret_path = []
                for step in path:
                    ret_path.insert(0, step)
                return ret_path

            # Don't repeat ourselves.
            reachable.remove(position)
            explored.append(position)

            new_reachable = self.worldmap.get_adjacent_positions_non_impassable(
                position
            )
            for adjacent in new_reachable:
                if abs(adjacent.x - pos0.x) > 10 or abs(adjacent.y - pos0.y) > 10:
                    continue
                if adjacent not in reachable and adjacent not in explored:
                    adjacent.previous = position  # Remember how we got there.
                    reachable.append(adjacent)

        return None

    def find_spawn_point_for_new_character(self):
        _tiles = self.worldmap.get_all_tiles()
        random.shuffle(_tiles)  # so we all don't spawn in one corner.
        for tile in _tiles:
            if (
                tile["position"].x < 13
                or tile["position"].y < 13
                or tile["position"].z != 0
            ):
                continue
            if tile["terrain"].impassable:
                continue
            if tile["creature"] is not None:
                continue
            if tile["terrain"].ident == "t_open_air":
                continue

            return tile["position"]

    def handle_new_character(self, ident, character):
        # ident is the account, character is the Character()
        self.characters[character.name] = character

        self.characters[
            character.name
        ].position = self.find_spawn_point_for_new_character()
        self.worldmap.put_object_at_position(
            self.characters[character.name], self.characters[character.name].position
        )
        self.localmaps[character.name] = self.worldmap.get_chunks_near_position(
            self.characters[character.name].position
        )

        # give the character their starting items by referencing the ProfessionManager.
        for key, value in self.ProfessionManager.PROFESSIONS[
            str(self.characters[character.name].profession)
        ].items():
            # TODO: load the items into the character equipment slots as well as future things like CBMs and flags
            if key == "equipped_items":
                for equip_location, item_ident in value.items():
                    for bodypart in self.characters[character.name].body_parts:
                        if bodypart.ident.split("_")[0] == equip_location:
                            if bodypart.slot0 is None:
                                if (
                                    "container_type"
                                    in self.ItemManager.ITEM_TYPES[item_ident]
                                ):
                                    bodypart.slot0 = Container(
                                        item_ident,
                                        self.ItemManager.ITEM_TYPES[item_ident],
                                    )  # need to pass the reference to load the item with data.
                                else:
                                    bodypart.slot0 = Item(
                                        item_ident,
                                        self.ItemManager.ITEM_TYPES[item_ident],
                                    )  # need to pass the reference to load the item with data.
                                break
                            elif bodypart.slot1 is None:
                                if (
                                    "container_type"
                                    in self.ItemManager.ITEM_TYPES[item_ident]
                                ):
                                    bodypart.slot1 = Container(
                                        item_ident,
                                        self.ItemManager.ITEM_TYPES[item_ident],
                                    )  # need to pass the reference to load the item with data.
                                else:
                                    bodypart.slot1 = Item(
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
                    for bodypart in self.characters[character.name].body_parts:
                        if bodypart.slot0 is not None:
                            if (
                                isinstance(bodypart.slot0, Container)
                                and bodypart.slot0.ident == location_ident
                            ):  # uses the first one it finds, maybe check if it's full?
                                bodypart.slot0.add_item(
                                    Item(
                                        item_ident,
                                        self.ItemManager.ITEM_TYPES[item_ident],
                                    )
                                )
                            if (
                                isinstance(bodypart.slot1, Container)
                                and bodypart.slot1.ident == location_ident
                            ):  # uses the first one it finds, maybe check if it's full?
                                bodypart.slot1.add_item(
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
            + str(character.name)
            + ".character"
        )
        import jsonpickle

        with open(path, "w") as fp:
            _pickled = jsonpickle.encode(character)
            pprint.pprint(_pickled)
            fp.write(_pickled)

        self._log.info("New character added to world: {}".format(character.name))

    # where most data is handled from the client.
    def callback_client_handle(self, connection_object, data):
        self._log.debug(
            "Server: Recieved data {} from client {}.".format(
                data, connection_object.address
            )
        )

        try:
            _command = Command(data["ident"], data["command"], data["args"])
        except:
            self._log.debug(
                "Server: invalid data {} from client {}.".format(
                    data, connection_object.address
                )
            )
            return

        # we recieved a valid command. process it.
        if isinstance(_command, Command):
            if _command["command"] == "login":
                # check whether this username has an account.
                _path = "./accounts/" + _command["ident"] + "/"
                if os.path.isdir("./accounts/" + _command["ident"]):
                    # account exists. check the sent password against the saved one.
                    with open(str(_path + "SALT"), "r") as _salt:
                        with open(
                            str(_path + "HASHED_PASSWORD"), "r"
                        ) as _hashed_password:
                            # read the password hashed
                            _check = hashPassword(_command["args"], _salt.read())
                            _check2 = _hashed_password.read()
                            if _check == _check2:
                                print("password accepted for " + str(_command["ident"]))
                                _message = {"login": "Accepted"}
                                self.callback_client_send(
                                    connection_object, json.dumps(_message)
                                )

                            else:
                                print(
                                    "password not accepted for "
                                    + str(_command["ident"])
                                )
                                connection_object.terminate()
                                # this player can recieve a list of characters they own.
                                pass

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
                        f.write(str(hashPassword(_command["args"], _salt)))

                    _path = "./accounts/" + _command["ident"] + "/characters/"
                    try:
                        os.mkdir(_path)
                    except OSError:
                        print("Creation of the directory %s failed" % _path)
                    else:
                        print("Successfully created the directory %s " % _path)

                    _message = {"login": "Accepted"}
                    self.callback_client_send(connection_object, json.dumps(_message))

            if _command["command"] == "choose_character":
                # send the current localmap to the player choosing the character
                self.characters[data["args"][0]] = self.worldmap.get_character(
                    data["args"][0]
                )
                self.localmaps[
                    data["args"][0]
                ] = self.worldmap.get_chunks_near_position(
                    self.characters[data["args"][0]].position
                )
                self.callback_client_send(
                    connection_object, self.localmaps[data["args"][0]]
                )

            if _command["command"] == "completed_character":
                if not data["ident"] in self.characters:
                    _character = Character(data["args"])
                    # this character doesn't exist in the world yet.
                    self.handle_new_character(data["ident"], _character)
                    self._log.debug(
                        "Server: character created: {} From client {}.".format(
                            _character.name, connection_object.address
                        )
                    )
                else:
                    self._log.debug(
                        "Server: character NOT created. Already Exists.: {} From client {}.".format(
                            data["ident"], connection_object.address
                        )
                    )

            if _command["command"] == "request_character_list":
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

                # put that list into a json container with header
                _container = {"character_list": _tmp_list}
                # pprint.pprint(_container)
                self.callback_client_send(connection_object, json.dumps(_container))

            if _command["command"] == "request_localmap_update":
                self.localmaps[data["args"]] = self.worldmap.get_chunks_near_position(
                    self.characters[data["args"]].position
                )
                _container = {"localmap_update": self.localmaps[data["args"]]}
                self.callback_client_send(connection_object, jsonpickle.encode(_container))

            # all the commands that are actions need to be put into the command_queue then we will loop through the queue each turn and process the actions.
            if _command["command"] == "ping":
                self.callback_client_send(connection_object, "pong")

            if _command["command"] == "move":
                self.characters[data["ident"]].command_queue.append(
                    Action(self.characters[data["ident"]], "move", [data.args[0]])
                )

            if _command["command"] == "bash":
                self.characters[data["ident"]].command_queue.append(
                    Action(self.characters[data["ident"]], "bash", [data.args[0]])
                )

            if _command["command"] == "create_blueprint":  # [result, direction])
                # args 0 is ident args 1 is direction.
                print(
                    "creating blueprint "
                    + str(data.args[0])
                    + " for character "
                    + str(self.characters[data["ident"]])
                )
                self._log.info(
                    "creating blueprint {} for character {}".format(
                        str(data.args[0]), str(self.characters[data["ident"]])
                    )
                )
                # blueprint rules
                # * there should be blueprints for terrain, furniture, items, and anything else that takes a slot up in the Worldmap.
                # * they act as placeholders and then 'transform' into the type they are once completed.
                # Blueprint(type, recipe)
                position_to_create_at = None
                if data.args[1] == "south":
                    position_to_create_at = Position(
                        self.characters[data["ident"]].position.x,
                        self.characters[data["ident"]].position.y + 1,
                        self.characters[data["ident"]].position.z,
                    )
                elif data.args[1] == "north":
                    position_to_create_at = Position(
                        self.characters[data["ident"]].position.x,
                        self.characters[data["ident"]].position.y - 1,
                        self.characters[data["ident"]].position.z,
                    )
                elif data.args[1] == "east":
                    position_to_create_at = Position(
                        self.characters[data["ident"]].position.x + 1,
                        self.characters[data["ident"]].position.y,
                        self.characters[data["ident"]].position.z,
                    )
                elif data.args[1] == "west":
                    position_to_create_at = Position(
                        self.characters[data["ident"]].position.x - 1,
                        self.characters[data["ident"]].position.y,
                        self.characters[data["ident"]].position.z,
                    )

                _recipe = server.RecipeManager.RECIPE_TYPES[data.args[0]]
                type_of = _recipe["type_of"]
                bp_to_create = Blueprint(type_of, _recipe)

                self.worldmap.put_object_at_position(
                    bp_to_create, position_to_create_at
                )

            if _command["command"] == "calculated_move":
                self._log.debug(
                    "Recieved calculated_move action. Building a path for {}".format(
                        str(data["ident"])
                    )
                )
                pprint.pprint(data['args'])
                _position = Position(data['args'][0], data['args'][1], data['args'][2])
                _route = self.calculate_route(
                    self.characters[data["ident"]].position, _position
                )  # returns a route from point 0 to point 1 as a series of Position(s)
                self._log.debug(
                    "Calculated route for Character {}: {}".format(
                        self.characters[data["ident"]], _route
                    )
                )

                # fill the queue with move commands to reach the tile.
                _x = self.characters[data["ident"]].position.x
                _y = self.characters[data["ident"]].position.y
                _z = self.characters[data["ident"]].position.z
                action = None
                if _route is None:
                    self._log.debug("No _route possible.")
                    return
                for step in _route:
                    _next_x = step.x
                    _next_y = step.y
                    _next_z = step.z
                    if _x > _next_x:
                        action = Action(
                            self.characters[data["ident"]], "move", ["west"]
                        )
                    elif _x < _next_x:
                        action = Action(
                            self.characters[data["ident"]], "move", ["east"]
                        )
                    elif _y > _next_y:
                        action = Action(
                            self.characters[data["ident"]], "move", ["north"]
                        )
                    elif _y < _next_y:
                        action = Action(
                            self.characters[data["ident"]], "move", ["south"]
                        )
                    elif _z < _next_z:
                        action = Action(self.characters[data["ident"]], "move", ["up"])
                    elif _z > _next_z:
                        action = Action(
                            self.characters[data["ident"]], "move", ["down"]
                        )
                    self.characters[data["ident"]].command_queue.append(action)
                    # pretend as if we are in the next position.
                    _x = _next_x
                    _y = _next_y
                    _z = _next_z

            if _command["command"] == "move_item_to_character_storage":
                _character = self.characters[data["ident"]]
                _from_pos = Position(data.args[0], data.args[1], data.args[2])
                _item_ident = data.args[3]
                _from_item = None
                _open_containers = []
                # find the item that the character is requesting.
                for item in self.worldmap.get_tile_by_position(_from_pos)["items"]:
                    if item.ident == _item_ident:
                        # this is the item or at least the first one that matches the same ident.
                        _from_item = item  # save a reference to it to use.
                        break

                # we didn't find one, character sent bad information (possible hack?)
                if _from_item == None:
                    return

                # make a list of open_containers the character has to see if they can pick it up.
                for bodyPart in _character.body_parts:
                    if (
                        bodyPart.slot0 is not None
                        and isinstance(bodyPart.slot0, Container)
                        and bodyPart.slot0.opened == "yes"
                    ):
                        _open_containers.append(bodyPart.slot0)
                    if (
                        bodyPart.slot1 is not None
                        and isinstance(bodyPart.slot1, Container)
                        and bodyPart.slot1.opened == "yes"
                    ):
                        _open_containers.append(bodyPart.slot1)

                if len(_open_containers) <= 0:
                    return  # no open containers.

                # check if the character can carry that item.
                for container in _open_containers:
                    # then find a spot for it to go (open_containers)
                    if container.add_item(item):  # if it added it sucessfully.
                        # remove it from the world.
                        for item in self.worldmap.get_tile_by_position(_from_pos)[
                            "items"
                        ][
                            :
                        ]:  # iterate a copy to remove properly.
                            if item.ident == _item_ident:
                                self.worldmap.get_tile_by_position(_from_pos)[
                                    "items"
                                ].remove(item)
                                break
                        return
                    else:
                        print("could not add item to character inventory.")
                    # then send the character the updated version of themselves so they can refresh.

            if _command["command"] == "move_item":
                # client sends 'hey server. can you move this item from this to that?'
                _character_requesting = self.characters[data["ident"]]
                _item = data.args[0]  # the item we are moving.
                _from_type = data.args[
                    1
                ]  # creature.held_item, creature.held_item.container, bodypart.equipped, bodypart.equipped.container, position, blueprint
                _from_list = (
                    []
                )  # the object list that contains the item. parse the type and fill this properly.
                _to_list = data.args[
                    2
                ]  # the list the item will end up. passed from command.
                _position = Position(
                    data.args[3], data.args[4], data.args[5]
                )  # pass the position even if we may not need it.

                # need to parse where it's coming from and where it's going.
                if _from_type == "bodypart.equipped":
                    for bodypart in _character_requesting.body_parts[
                        :
                    ]:  # iterate a copy to remove properly.
                        if _item in bodypart.equipped:
                            _from_list = bodypart.equipped
                            _from_list.remove(_item)
                            _to_list.append(_item)
                            return
                elif _from_type == "bodypart.equipped.container":
                    for bodypart in _character_requesting.body_parts[
                        :
                    ]:  # iterate a copy to remove properly.
                        for item in bodypart.equipped:  # could be a container or not.
                            # if it's a container.
                            if isinstance(item, Container):
                                for item2 in item.contained_items[
                                    :
                                ]:  # check every item in the container.
                                    if item2 is _item:
                                        _from_list = item.contained_items
                                        _from_list.remove(_item)
                                        _to_list.append(_item)
                                        return
                elif _from_type == "position":
                    _from_list = self.worldmap.get_tile_by_position(_position)["items"]
                    if _item in _from_list:
                        _from_list.remove(_item)
                        _to_list.append(_item)
                        return
                elif (
                    _from_type == "blueprint"
                ):  # a blueprint is a type of container but can't be moved from it's world position.
                    for item in self.worldmap.get_tile_by_position(_position)["items"]:
                        if (
                            isinstance(item) == Blueprint
                        ):  # only one blueprint allowed per space.
                            _from_list = item.contained_items
                            _from_list.remove(_item)
                            _to_list.append(_item)
                            return

                ### possible move types ###
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

        return super(Server, self).callback_client_handle(connection_object, data)

    def callback_client_send(self, connection_object, data, compression=False):
        return super(Server, self).callback_client_send(
            connection_object, data, compression
        )

    def callback_connect_client(self, connection_object):
        self._log.info(
            "Server: Client from {} connected.".format(connection_object.address)
        )
        return super(Server, self).callback_connect_client(connection_object)

    def callback_disconnect_client(self, connection_object):
        self._log.info(
            "Server: Client from {} disconnected.".format(connection_object.address)
        )
        return super(Server, self).callback_disconnect_client(connection_object)

    def process_creature_command_queue(self, creature):
        actions_to_take = creature.actions_per_turn
        for action in creature.command_queue[
            :
        ]:  # iterate a copy so we can remove on the fly.
            if actions_to_take == 0:
                return  # this creature is out of action points.

            if (
                creature.next_action_available > 0
            ):  # this creature can't act until x turns from now.
                creature.next_action_available = creature.next_action_available - 1
                return

            # if we get here we can process a single action
            if action.action_type == "move":
                actions_to_take = actions_to_take - 1  # moving costs 1 ap.
                if action.args[0] == "south":
                    if self.worldmap.move_object_from_position_to_position(
                        self.characters[creature.name],
                        self.characters[creature.name].position,
                        Position(
                            self.characters[creature.name].position.x,
                            self.characters[creature.name].position.y + 1,
                            self.characters[creature.name].position.z,
                        ),
                    ):
                        self.characters[creature.name].position = Position(
                            self.characters[creature.name].position.x,
                            self.characters[creature.name].position.y + 1,
                            self.characters[creature.name].position.z,
                        )
                    creature.command_queue.remove(
                        action
                    )  # remove the action after we process it.
                if action.args[0] == "north":
                    if self.worldmap.move_object_from_position_to_position(
                        self.characters[creature.name],
                        self.characters[creature.name].position,
                        Position(
                            self.characters[creature.name].position.x,
                            self.characters[creature.name].position.y - 1,
                            self.characters[creature.name].position.z,
                        ),
                    ):
                        self.characters[creature.name].position = Position(
                            self.characters[creature.name].position.x,
                            self.characters[creature.name].position.y - 1,
                            self.characters[creature.name].position.z,
                        )
                    creature.command_queue.remove(
                        action
                    )  # remove the action after we process it.
                if action.args[0] == "east":
                    if self.worldmap.move_object_from_position_to_position(
                        self.characters[creature.name],
                        self.characters[creature.name].position,
                        Position(
                            self.characters[creature.name].position.x + 1,
                            self.characters[creature.name].position.y,
                            self.characters[creature.name].position.z,
                        ),
                    ):
                        self.characters[creature.name].position = Position(
                            self.characters[creature.name].position.x + 1,
                            self.characters[creature.name].position.y,
                            self.characters[creature.name].position.z,
                        )
                    creature.command_queue.remove(
                        action
                    )  # remove the action after we process it.
                if action.args[0] == "west":
                    if self.worldmap.move_object_from_position_to_position(
                        self.characters[creature.name],
                        self.characters[creature.name].position,
                        Position(
                            self.characters[creature.name].position.x - 1,
                            self.characters[creature.name].position.y,
                            self.characters[creature.name].position.z,
                        ),
                    ):
                        self.characters[creature.name].position = Position(
                            self.characters[creature.name].position.x - 1,
                            self.characters[creature.name].position.y,
                            self.characters[creature.name].position.z,
                        )
                    creature.command_queue.remove(
                        action
                    )  # remove the action after we process it.
                if action.args[0] == "up":
                    if self.worldmap.move_object_from_position_to_position(
                        self.characters[creature.name],
                        self.characters[creature.name].position,
                        Position(
                            self.characters[creature.name].position.x,
                            self.characters[creature.name].position.y,
                            self.characters[creature.name].position.z + 1,
                        ),
                    ):
                        self.characters[creature.name].position = Position(
                            self.characters[creature.name].position.x,
                            self.characters[creature.name].position.y,
                            self.characters[creature.name].position.z + 1,
                        )
                    creature.command_queue.remove(
                        action
                    )  # remove the action after we process it.
                if action.args[0] == "down":
                    if self.worldmap.move_object_from_position_to_position(
                        self.characters[creature.name],
                        self.characters[creature.name].position,
                        Position(
                            self.characters[creature.name].position.x,
                            self.characters[creature.name].position.y,
                            self.characters[creature.name].position.z - 1,
                        ),
                    ):
                        self.characters[creature.name].position = Position(
                            self.characters[creature.name].position.x,
                            self.characters[creature.name].position.y,
                            self.characters[creature.name].position.z - 1,
                        )
                    creature.command_queue.remove(
                        action
                    )  # remove the action after we process it.
            elif action.action_type == "bash":
                actions_to_take = actions_to_take - 1  # bashing costs 1 ap.
                if action.args[0] == "south":
                    self.worldmap.bash(
                        self.characters[creature.name],
                        Position(
                            self.characters[creature.name].position.x,
                            self.characters[creature.name].position.y + 1,
                            self.characters[creature.name].position.z,
                        ),
                    )
                    self.localmaps[
                        creature.name
                    ] = self.worldmap.get_chunks_near_position(
                        self.characters[creature.name].position
                    )
                    creature.command_queue.remove(
                        action
                    )  # remove the action after we process it.
                if action.args[0] == "north":
                    self.worldmap.bash(
                        self.characters[creature.name],
                        Position(
                            self.characters[creature.name].position.x,
                            self.characters[creature.name].position.y - 1,
                            self.characters[creature.name].position.z,
                        ),
                    )
                    self.localmaps[
                        creature.name
                    ] = self.worldmap.get_chunks_near_position(
                        self.characters[creature.name].position
                    )
                    creature.command_queue.remove(
                        action
                    )  # remove the action after we process it.
                if action.args[0] == "east":
                    self.worldmap.bash(
                        self.characters[creature.name],
                        Position(
                            self.characters[creature.name].position.x + 1,
                            self.characters[creature.name].position.y,
                            self.characters[creature.name].position.z,
                        ),
                    )
                    self.localmaps[
                        creature.name
                    ] = self.worldmap.get_chunks_near_position(
                        self.characters[creature.name].position
                    )
                    creature.command_queue.remove(
                        action
                    )  # remove the action after we process it.
                if action.args[0] == "west":
                    self.worldmap.bash(
                        self.characters[creature.name],
                        Position(
                            self.characters[creature.name].position.x - 1,
                            self.characters[creature.name].position.y,
                            self.characters[creature.name].position.z,
                        ),
                    )
                    self.localmaps[
                        creature.name
                    ] = self.worldmap.get_chunks_near_position(
                        self.characters[creature.name].position
                    )
                    creature.command_queue.remove(
                        action
                    )  # remove the action after we process it.

    def compute_turn(self):
        # this function handles overseeing all creature movement, attacks, and interactions

        # init a list for all our found lights around characters.
        for _, chunks in self.localmaps.items():
            for chunk in chunks:  # characters typically get 9 chunks
                for tile in chunk.tiles:
                    tile["lumens"] = 0  # reset light levels.

        for _, chunks in self.localmaps.items():
            for chunk in chunks:  # characters typically get 9 chunks
                for tile in chunk.tiles:
                    for item in tile["items"]:
                        if isinstance(item, Blueprint):
                            continue
                        for flag in self.ItemManager.ITEM_TYPES[item.ident]["flags"]:
                            if (
                                flag.split("_")[0] == "LIGHT"
                            ):  # this item produces light.
                                for (
                                    tile,
                                    distance,
                                ) in self.worldmap.get_tiles_near_position(
                                    tile["position"], int(flag.split("_")[1])
                                ):
                                    tile["lumens"] = tile["lumens"] + int(
                                        int(flag.split("_")[1]) - distance
                                    )
                    if tile["furniture"] is not None:
                        for key in self.FurnitureManager.FURNITURE_TYPES[
                            tile["furniture"].ident
                        ]:
                            if key == "flags":
                                for flag in self.FurnitureManager.FURNITURE_TYPES[
                                    tile["furniture"].ident
                                ]["flags"]:
                                    if (
                                        flag.split("_")[0] == "LIGHT"
                                    ):  # this furniture produces light.
                                        for (
                                            tile,
                                            distance,
                                        ) in self.worldmap.get_tiles_near_position(
                                            tile["position"], int(flag.split("_")[1])
                                        ):
                                            tile["lumens"] = tile["lumens"] + int(
                                                int(flag.split("_")[1]) - distance
                                            )
                                        break
        # we want a list that contains all the non-duplicate creatures on all localmaps around characters.
        creatures_to_process = list()
        for _, chunks in self.localmaps.items():
            for chunk in chunks:  # characters typically get 9 chunks
                for tile in chunk.tiles:
                    if (
                        tile["creature"] is not None
                        and tile["creature"] not in creatures_to_process
                    ):
                        creatures_to_process.append(tile["creature"])

        for creature in creatures_to_process:
            # as long as there at least one we'll pass it on and let the function handle how many actions they can take.
            if len(creature.command_queue) > 0:
                self.process_creature_command_queue(creature)

        # now that we've processed what everything wants to do we can return.

    def generate_and_apply_city_layout(self, city_size):
        # city_size = 1
        city_layout = self.worldmap.generate_city(city_size)
        # for every 1 city size it's 12 tiles across and high
        for j in range(city_size * 12):
            for i in range(city_size * 12):
                if (
                    server.worldmap.get_chunk_by_position(
                        Position(
                            i * server.worldmap.chunk_size + 1,
                            j * server.worldmap.chunk_size + 1,
                            0,
                        )
                    ).was_loaded
                    == "no"
                ):
                    if city_layout[i][j] == "r":
                        json_file = random.choice(
                            os.listdir("./data/json/mapgen/residential/")
                        )

                        server.worldmap.build_json_building_at_position(
                            "./data/json/mapgen/residential/" + json_file,
                            Position(
                                i * server.worldmap.chunk_size + 1,
                                j * server.worldmap.chunk_size + 1,
                                0,
                            ),
                        )
                    elif city_layout[i][j] == "c":
                        json_file = random.choice(
                            os.listdir("./data/json/mapgen/commercial/")
                        )
                        server.worldmap.build_json_building_at_position(
                            "./data/json/mapgen/commercial/" + json_file,
                            Position(
                                i * server.worldmap.chunk_size + 1,
                                j * server.worldmap.chunk_size + 1,
                                0,
                            ),
                        )
                    elif city_layout[i][j] == "i":
                        json_file = random.choice(
                            os.listdir("./data/json/mapgen/industrial/")
                        )
                        server.worldmap.build_json_building_at_position(
                            "./data/json/mapgen/industrial/" + json_file,
                            Position(
                                i * server.worldmap.chunk_size + 1,
                                j * server.worldmap.chunk_size + 1,
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
                            server.worldmap.build_json_building_at_position(
                                json_file,
                                Position(
                                    i * server.worldmap.chunk_size + 1,
                                    j * server.worldmap.chunk_size + 1,
                                    0,
                                ),
                            )
                        except:
                            # TODO: fix this blatant hack to account for coordinates outside the city layout.
                            pass


# do this if the server was started up directly.
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Cataclysm LD Server")
    parser.add_argument("--host", metavar="Host", help="Server host", default="0.0.0.0")
    parser.add_argument(
        "--port", metavar="Port", type=int, help="Server port", default=6317
    )
    parser.add_argument(
        "--config", metavar="Config", help="Configuration file", default="server.cfg"
    )
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
    logging.config.fileConfig(args.config)
    log = logging.getLogger("root")
    log.info("Server is start at {}:{}".format(ip, port))

    server = Server(logger=log, config=defaultConfig)
    server.connect(ip, port)
    server.accepting_allow()

    dont_break = True
    time_offset = float(
        defaultConfig.get("time_offset", 1.0)
    )  # 0.5 is twice as fast, 2.0 is twice as slow
    last_turn_time = time.time()
    citySize = int(defaultConfig.get("city_size", 1))
    log.info("City size: {}".format(citySize))
    server.generate_and_apply_city_layout(citySize)

    time_per_turn = int(defaultConfig.get("time_per_turn", 1))
    log.info("time_per_turn: {}".format(time_per_turn))
    spin_delay_ms = float(defaultConfig.get("time_per_turn", 0.001))
    log.info("spin_delay_ms: {}".format(spin_delay_ms))
    
    for _character in server.worldmap.get_all_characters():
        server.characters[_character.name] = _character

    log.info("Started up Cataclysm: Looming Darkness Server.")
    while dont_break:
        try:
            while (
                time.time() - last_turn_time < time_offset
            ):  # try to keep up with the time offset but never go faster than it.
                time.sleep(spin_delay_ms)
            server.calendar.advance_time_by_x_seconds(
                time_per_turn
            )  # a turn is one second.
            # where all queued creature actions get taken care of, as well as physics engine stuff.
            server.compute_turn()
            # if the worldmap in memory changed update it on the hard drive.
            server.worldmap.update_chunks_on_disk()
            # TODO: unload from memory chunks that have no updates required. (such as no monsters, Characters, or fires)
            last_turn_time = time.time()  # based off of system clock.
        except KeyboardInterrupt:
            log.info("cleaning up before exiting.")
            server.accepting_disallow()
            server.disconnect_clients()
            server.disconnect()
            # if the worldmap in memory changed update it on the hard drive.
            server.worldmap.update_chunks_on_disk()
            dont_break = False
            log.info("done cleaning up.")
        """except Exception as e:
            server.accepting_disallow()
            server.disconnect_clients()
            server.disconnect()
            server.worldmap.update_chunks_on_disk() # if the worldmap in memory changed update it on the hard drive.
            dont_break = False
            sys.exit()"""
