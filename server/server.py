#!/usr/bin/env python3

import argparse
import os
import random
import time
import configparser
import logging.config

from src.mastermind._mm_server import MastermindServerTCP
from src.blueprint import Blueprint
from src.calendar import Calendar
from src.model.command import Command
from src.model.manager.item import Item
from src.model.manager.managers import Managers
from src.model.world_state import WorldState
from src.position import Position
from src.request_handler.request_handler import RequestHandler


class OverMap:  # when the character pulls up the OverMap. a OverMap for each character will have to be stored for undiscovered areas and when they use maps.
    def __init__(self):  # the ident of the character who owns this overmap.
        # over map size is the worldmap size
        # build the overmap from seen tiles, roadmaps, maps.
        # if a character sees a chunk loaded it"s safe to say they "saw" that overmap tile.
        return


class Server(MastermindServerTCP):
    def __init__(self, config, logger=None):
        MastermindServerTCP.__init__(self, 0.5, 0.5, 300.0)
        self._config = config
        self.logger = logger
        if self.logger is None:
            logging.basicConfig()
            self.logger = logging.getLogger("root")
            self.logger.warning("Basic logging configuration fallback used because no logger defined.")

        self.calendar = Calendar(0, 0, 0, 0, 0, 0)  # all zeros is the epoch

        self.world_state = WorldState()
        self.managers = Managers()

        self.request_handler = RequestHandler(self.logger, self.managers, self.callback_client_send)

    def get_connections(self):
        return self._mm_connections

    # where most data is handled from the client.
    def callback_client_handle(self, connection_object, data):
        print(f"Server: Received data {data} from client {connection_object.address}.")

        if data == "disconnect":
            self.callback_disconnect_client(connection_object)
            return

        try:
            command = Command(data["ident"], data["command"], connection_object.address, data["args"])
        except:
            print(f"Server: invalid data {data} from client {connection_object.address}.")
            return

        self.request_handler.handle_request(command, self.world_state, connection_object)

        return super(Server, self).callback_client_handle(connection_object, data)

    def callback_client_send(self, connection_object, data, compression=False):
        return super(Server, self).callback_client_send(
            connection_object, data, compression
        )

    def callback_connect_client(self, connection_object):
        print("Server: Client from {} connected.".format(connection_object.address))

    def callback_disconnect_client(self, connection_object):
        print("Server: Client from {} disconnected.".format(connection_object.address))
        connection_object.terminate()

    def process_creature_command_queue(self, creature):
        actions_to_take = creature["actions_per_turn"]
        worldmap = self.world_state.worldmap
        characters = self.world_state.characters
        # iterate a copy so we can remove on the fly.
        for action in creature["command_queue"][:]:
            if actions_to_take == 0:
                return  # this creature is out of action points.

            # this creature can't act until x turns from now.
            if creature["next_action_available"] > 0:
                creature["next_action_available"] = creature["next_action_available"] - 1
                return

            # if we get here we can process a single action
            if action["action_type"] == "move":
                print("moving character " + str(creature["name"]))
                actions_to_take = actions_to_take - 1  # moving costs 1 ap.
                if action["args"][0] == "south":
                    if worldmap.move_creature_from_position_to_position(
                        characters[creature["name"]],
                        characters[creature["name"]]["position"],
                        Position(
                            characters[creature["name"]]["position"]["x"],
                            characters[creature["name"]]["position"]["y"] + 1,
                            characters[creature["name"]]["position"]["z"],
                        ),
                    ):
                        characters[creature["name"]]["position"] = Position(
                            characters[creature["name"]]["position"]["x"],
                            characters[creature["name"]]["position"]["y"] + 1,
                            characters[creature["name"]]["position"]["z"],
                        )
                    creature["command_queue"].remove(action) 
                if action["args"][0] == "north":
                    if worldmap.move_creature_from_position_to_position(
                        characters[creature["name"]],
                        characters[creature["name"]]["position"],
                        Position(
                            characters[creature["name"]]["position"]["x"],
                            characters[creature["name"]]["position"]["y"] - 1,
                            characters[creature["name"]]["position"]["z"],
                        ),
                    ):
                        characters[creature["name"]]["position"] = Position(
                            characters[creature["name"]]["position"]["x"],
                            characters[creature["name"]]["position"]["y"] - 1,
                            characters[creature["name"]]["position"]["z"],
                        )
                    creature["command_queue"].remove(action) 
                if action["args"][0] == "east":
                    if worldmap.move_creature_from_position_to_position(
                        characters[creature["name"]],
                        characters[creature["name"]]["position"],
                        Position(
                            characters[creature["name"]]["position"]["x"] + 1,
                            characters[creature["name"]]["position"]["y"],
                            characters[creature["name"]]["position"]["z"],
                        ),
                    ):
                        characters[creature["name"]]["position"] = Position(
                            characters[creature["name"]]["position"]["x"] + 1,
                            characters[creature["name"]]["position"]["y"],
                            characters[creature["name"]]["position"]["z"],
                        )
                    creature["command_queue"].remove(action) 
                if action["args"][0] == "west":
                    if worldmap.move_creature_from_position_to_position(
                        characters[creature["name"]],
                        characters[creature["name"]]["position"],
                        Position(
                            characters[creature["name"]]["position"]["x"] - 1,
                            characters[creature["name"]]["position"]["y"],
                            characters[creature["name"]]["position"]["z"],
                        ),
                    ):
                        characters[creature["name"]]["position"] = Position(
                            characters[creature["name"]]["position"]["x"] - 1,
                            characters[creature["name"]]["position"]["y"],
                            characters[creature["name"]]["position"]["z"],
                        )
                    creature["command_queue"].remove(action) 
                if action["args"][0] == "up":
                    if worldmap.move_creature_from_position_to_position(
                        characters[creature["name"]],
                        characters[creature["name"]]["position"],
                        Position(
                            characters[creature["name"]]["position"]["x"],
                            characters[creature["name"]]["position"]["y"],
                            characters[creature["name"]]["position"]["z"] + 1,
                        ),
                    ):
                        characters[creature["name"]]["position"] = Position(
                            characters[creature["name"]]["position"]["x"],
                            characters[creature["name"]]["position"]["y"],
                            characters[creature["name"]]["position"]["z"] + 1,
                        )
                    creature["command_queue"].remove(action)
                if action["args"][0] == "down":
                    if worldmap.move_creature_from_position_to_position(
                        characters[creature["name"]],
                        characters[creature["name"]]["position"],
                        Position(
                            characters[creature["name"]]["position"]["x"],
                            characters[creature["name"]]["position"]["y"],
                            characters[creature["name"]]["position"]["z"] - 1,
                        ),
                    ):
                        characters[creature["name"]]["position"] = Position(
                            characters[creature["name"]]["position"]["x"],
                            characters[creature["name"]]["position"]["y"],
                            characters[creature["name"]]["position"]["z"] - 1,
                        )
                    creature["command_queue"].remove(action)
            elif action["action_type"] == "bash":
                actions_to_take = actions_to_take - 1  # bashing costs 1 ap.
                self.bash(
                    self.world_state.characters[creature["name"]],
                    Position(
                        action["args"]['x'],
                        action["args"]['y'],
                        action["args"]['z']
                    ),
                )
                self.world_state.localmaps[creature["name"]] = self.world_state.worldmap.get_chunks_near_position(
                    self.world_state.characters[creature["name"]]["position"]
                )
                creature["command_queue"].remove(action)

    def bash(self, creature, position):
        """Catch-all for bash/smash since we bash in a direction we need to check what's in the tile."""
        tile = self.world_state.worldmap.get_tile_by_position(position)
        # strength = creature strength.
        if tile["furniture"] is not None:
            furniture_type = self.managers.furniture_manager.FURNITURE_TYPES[tile["furniture"]["ident"]]
            for item in furniture_type["bash"]["items"]:
                self.world_state.worldmap.put_object_at_position(
                    Item(
                        self.managers.item_manager.ITEM_TYPES[str(item["item"])]["ident"],
                        self.managers.item_manager.ITEM_TYPES[str(item["item"])],
                    ),
                    position,
                )  # need to pass the reference to load the item with data.
            tile["furniture"] = None
        return

    def compute_turn(self):
        # this function handles overseeing all creature movement, attacks, and interactions
        localmaps = self.world_state.localmaps
        worldmap = self.world_state.worldmap

        # init a list for all our found lights around characters.
        for _, chunks in localmaps.items():
            for chunk in chunks:  # characters typically get 9 chunks
                for tile in chunk["tiles"]:
                    tile["lumens"] = 0  # reset light levels.

        for _, chunks in localmaps.items():
            for chunk in chunks:  # characters typically get 9 chunks
                for tile in chunk["tiles"]:
                    for item in tile["items"]:
                        if isinstance(item, Blueprint):
                            continue
                        if "flags" in self.managers.item_manager.ITEM_TYPES[item["ident"]]:
                            for flag in self.managers.item_manager.ITEM_TYPES[item["ident"]]["flags"]:
                                if flag.split("_")[0] == "LIGHT":  # this item produces light.
                                    for (tile, distance) in worldmap.get_tiles_near_position(tile["position"], int(flag.split("_")[1])):
                                        tile["lumens"] = tile["lumens"] + int(
                                            int(flag.split("_")[1]) - distance
                                        )
                    if tile["furniture"] is not None:
                        for key in self.managers.furniture_manager.FURNITURE_TYPES[tile["furniture"]["ident"]]:
                            if key == "flags":
                                for flag in self.managers.furniture_manager.FURNITURE_TYPES[tile["furniture"]["ident"]]["flags"]:
                                    if flag.split("_")[0] == "LIGHT":  # this furniture produces light.
                                        for (tile, distance) in worldmap.get_tiles_near_position(tile["position"], int(flag.split("_")[1])):
                                            tile["lumens"] = tile["lumens"] + int(
                                                int(flag.split("_")[1]) - distance
                                            )
                                        break
        # we want a list that contains all the non-duplicate creatures on all localmaps around characters.
        creatures_to_process = list()
        for _, chunks in localmaps.items():
            for chunk in chunks:  # characters typically get 9 chunks
                for tile in chunk["tiles"]:
                    if tile["creature"] is not None and tile["creature"] not in creatures_to_process:
                        creatures_to_process.append(tile["creature"])

        for creature in creatures_to_process:
            # as long as there at least one we'll pass it on and let the function handle how many actions they can take.
            if len(creature["command_queue"]) > 0:
                self.process_creature_command_queue(creature)

        # now that we've processed what everything wants to do we can return.

    def generate_and_apply_city_layout(self, city_size):
        # city_size = 1
        worldmap = self.world_state.worldmap
        city_layout = worldmap.generate_city(city_size)
        # for every 1 city size it's 12 tiles across and high
        for j in range(city_size * 12):
            for i in range(city_size * 12):
                if (
                    worldmap.get_chunk_by_position(
                        Position(
                            i * worldmap["chunk_size"] + 1,
                            j * worldmap["chunk_size"] + 1,
                            0,
                        )
                    )["was_loaded"]
                    is False
                ):
                    if city_layout[i][j] == "r":
                        json_file = random.choice(
                            os.listdir("./data/json/mapgen/residential/")
                        )

                        worldmap.build_json_building_at_position(
                            "./data/json/mapgen/residential/" + json_file,
                            Position(
                                i * worldmap["chunk_size"] + 1,
                                j * worldmap["chunk_size"] + 1,
                                0,
                            ),
                        )
                    elif city_layout[i][j] == "c":
                        json_file = random.choice(
                            os.listdir("./data/json/mapgen/commercial/")
                        )
                        worldmap.build_json_building_at_position(
                            "./data/json/mapgen/commercial/" + json_file,
                            Position(
                                i * worldmap["chunk_size"] + 1,
                                j * worldmap["chunk_size"] + 1,
                                0,
                            ),
                        )
                    elif city_layout[i][j] == "i":
                        json_file = random.choice(
                            os.listdir("./data/json/mapgen/industrial/")
                        )
                        worldmap.build_json_building_at_position(
                            "./data/json/mapgen/industrial/" + json_file,
                            Position(
                                i * worldmap["chunk_size"] + 1,
                                j * worldmap["chunk_size"] + 1,
                                0,
                            ),
                        )
                    elif city_layout[i][j] == "R":  # complex enough to choose the right rotation.
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
                                json_file = "./data/json/mapgen/road/city_road_4_way.json"
                            elif attached_roads == 3:
                                # TODO: make sure the roads line up right.
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
                                    json_file = "./data/json/mapgen/road/city_road_h.json"
                                elif city_layout[int(i - 1)][int(j)] == "R":
                                    json_file = "./data/json/mapgen/road/city_road_h.json"
                                elif city_layout[int(i)][int(j + 1)] == "R":
                                    json_file = "./data/json/mapgen/road/city_road_v.json"
                                elif city_layout[int(i)][int(j - 1)] == "R":
                                    json_file = "./data/json/mapgen/road/city_road_v.json"
                            worldmap.build_json_building_at_position(
                                json_file,
                                Position(
                                    i * worldmap["chunk_size"] + 1,
                                    j * worldmap["chunk_size"] + 1,
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
    print("Server is listening at {}:{}".format(ip, port))

    server = Server(logger=log, config=defaultConfig)
    server.connect(ip, port)
    server.accepting_allow()

    dont_break = True
    time_offset = float(
        defaultConfig.get("time_offset", 1.0)
    )  # 0.5 is twice as fast, 2.0 is twice as slow
    last_turn_time = time.time()
    citySize = int(defaultConfig.get("city_size", 1))
    # print("City size: {}'.format(citySize))
    server.generate_and_apply_city_layout(citySize)

    time_per_turn = int(defaultConfig.get("time_per_turn", 1))
    # print("time_per_turn: {}".format(time_per_turn))
    spin_delay_ms = float(defaultConfig.get("time_per_turn", 0.001))
    # print("spin_delay_ms: {}".format(spin_delay_ms))

    worldmap = server.world_state.worldmap
    characters = server.world_state.characters

    for character in worldmap.get_all_characters():
        characters[character["name"]] = character

    print("Started Cataclysm: Looming Darkness. Clients may now connect.")
    while dont_break:
        try:
            # try to keep up with the time offset but never go faster than it.
            if time.time() - last_turn_time < time_offset:
                continue

            # a turn is one second.
            server.calendar.advance_time_by_x_seconds(time_per_turn)

            # where all queued creature actions get taken care of, as well as physics engine stuff.
            server.compute_turn()

            # if the worldmap in memory changed update it on the hard drive.
            worldmap.update_chunks_on_disk()

            # TODO: unload from memory chunks that have no updates required. (such as no monsters, Characters, or fires)
            last_turn_time = time.time()  # based off of system clock.
        except KeyboardInterrupt:
            print("Cleaning up before exiting.")
            server.accepting_disallow()
            server.disconnect_clients()
            server.disconnect()
            # if the worldmap in memory changed update it on the hard drive.
            worldmap.update_chunks_on_disk()
            dont_break = False
            print("Done cleaning up.")
