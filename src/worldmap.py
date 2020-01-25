import json
import os
import random
import time

from src.creature import Creature
from src.furniture import Furniture
from src.item import Item, Container, Blueprint
from src.monster import Monster
from src.character import Character
from src.position import Position
from src.terrain import Terrain

# weather = [WEATHER_CLEAR, WEATHER_RAIN, WEATHER_FOG, WEATHER_STORM, WEATHER_TORNADO]


class Chunk(dict):
    def __init__(self, x, y):  # x, y relate to it's position on the world map.
        self["chunk_size"] = 13  # 0-12 tiles in x and y, z-level 1 tile only (0).
        self["tiles"] = list()
        self["weather"] = "WEATHER_NONE"  # weather is per chunk.
        # the tile represented on the over map
        self["overmap_tile"] = "open_air"
        # set this to true to have the changes updated on the disk, default is True so worldgen writes it to disk
        self["is_dirty"] = True
        self["was_loaded"] = False
        self["should_stasis"] = True  # TODO: when we unload from memory we need a flag not to loop through it during compute turn
        self["stasis"] = False  # when a chunk is put into stasis.
        self["time_to_stasis"] = 100  # reduce by 1 every turn a player is not near it. set should_stasis when gets to zero
        
        # when a chunk is created for the first time fill with dirt and nothing else. rest is handled in world generation.
        start = time.time()
        for i in range(self["chunk_size"]):  # 0-12
            for j in range(self["chunk_size"]):  # 0-12
                chunkdict = {}
                # this position is on the worldmap. no position is ever repeated. each chunk tile gets its own position.
                chunkdict["position"] = Position(i + int(x * self["chunk_size"]), j + int(y * self["chunk_size"]), 0)
                chunkdict["terrain"] = Terrain("t_dirt")  # make the earth
                chunkdict["creature"] = None  # one per tile.
                chunkdict["items"] = []  # can be zero to many items in a tile.
                chunkdict["furniture"] = None  # one furniture per tile
                chunkdict["vehicle"] = None  # one per tile, but may be part of a bigger whole.
                chunkdict["lumens"] = 0 # lighting engine
                self["tiles"].append(chunkdict)
        end = time.time()
        duration = end - start
        print('chunk generation took: ' + str(duration) + ' seconds.')


class Worldmap(dict):
    # let's make the world map and fill it with chunks!

    def __init__(self, size):  # size in chunks along one axis.
        self["WORLD_SIZE"] = size
        self["WORLDMAP"] = dict()  # dict of dicts for chunks
        # size of the chunk, leave it hardcoded here. (0-12)
        start = time.time()
        print("creating/loading world chunks")
        for i in range(self["WORLD_SIZE"]):
            self["WORLDMAP"][i] = dict()
            for j in range(self["WORLD_SIZE"]):
                self["WORLDMAP"][i][j] = dict()
                path = str(
                    "./world/"
                    + str(i)
                    + "_"
                    + str(j)
                    + ".chunk"
                )

                if os.path.isfile(path):  # if the chunk already exists on disk load it. Otherwise create it and save it.
                    with open(path, "r") as fp:
                        self["WORLDMAP"][i][j] = json.loads(fp.read())
                        self["WORLDMAP"][i][j]["was_loaded"] = "yes"
                else:
                    self["WORLDMAP"][i][j] = Chunk(i, j)
                    with open(path, "w") as fp:
                        json.dump(self["WORLDMAP"][i][j], fp)

        end = time.time()
        duration = end - start
        print("First pass world generation took: {} seconds".format(duration))

    def update_chunks_on_disk(self):  # after our map in memory changes we need to update the chunk file on disk.
        for i in range(self["WORLD_SIZE"]):
            for j in range(self["WORLD_SIZE"]):
                path = str(
                    "./world/"
                    + str(i)
                    + "_"
                    + str(j)
                    + ".chunk"
                )
                if os.path.isfile(path):
                    if self["WORLDMAP"][i][j]["is_dirty"]:
                        with open(path, "w") as fp:
                            self["WORLDMAP"][i][j]["is_dirty"] = False
                            json.dump(self["WORLDMAP"][i][j], fp)

    def get_chunk_by_position(self, position):
        x_count = 0
        x = position["x"]
        while x >= 13:
            x = x - 13
            x_count = x_count + 1

        y_count = 0
        y = position["y"]
        # worldmap[x][y]['tiles']
        while y >= 13:
            y = y - 13
            y_count = y_count + 1

        # print('getting chunk {} {}'.format(x_count, y_count))
        return self["WORLDMAP"][x_count][y_count]

    def get_all_tiles(self):
        ret = []
        # print("getting all tiles")
        for i, dictionary_x in self["WORLDMAP"].items():
            for j, chunk in dictionary_x.items():
                for tile in chunk["tiles"]:
                    ret.append(tile)
        print("all tiles: {}".format(len(ret)))
        return ret  # expensive function. use sparingly.

    def get_tile_by_position(self, position):
        # print(position)
        x_count = 0  # these two little loop gets us the right chunk FAST
        x = position["x"]
        while x >= 12:
            x = x - 12
            x_count = x_count + 1

        y_count = 0
        y = position["y"]
        while y >= 12:
            y = y - 12
            y_count = y_count + 1

        # z = position["z"]

        for tile in self["WORLDMAP"][x_count][y_count]["tiles"]:
            if tile["position"] == position:
                return tile
        else:
            # need a position that doesn't exit yet. (likely z-level generation) Let's create it.
            # print("creating NEW tile for position")
            _tile = {}
            # this position is on the worldmap. no position is ever repeated. each chunk tile gets its own position.
            _tile["position"] = position
            _tile["terrain"] = Terrain("t_dirt")  # make the earth
            _tile["creature"] = None  # one per tile.
            _tile["items"] = []  # can be zero to many items in a tile.
            _tile["furniture"] = None  # one furniture per tile
            _tile["vehicle"] = None  # one per tile, but may be part of a bigger whole.
            _tile["lumens"] = 0  # lighting engine
            self["WORLDMAP"][x_count][y_count]["tiles"].append(_tile)
            return _tile

    def get_chunks_near_position(self, position):  # a localmap
        chunks = []
        # we should only need the 9 chunks around the chunk position
        x = position["x"]
        y = position["y"]
        z = position["z"]
        self["chunk_size"] = 13
        north_east_chunk = self.get_chunk_by_position(
            Position(x + self["chunk_size"], y + self["chunk_size"], z)
        )
        chunks.append(north_east_chunk)
        north_chunk = self.get_chunk_by_position(
            Position(x + self["chunk_size"], y, z))
        chunks.append(north_chunk)
        north_west_chunk = self.get_chunk_by_position(
            Position(x + self["chunk_size"], y - self["chunk_size"], z)
        )
        chunks.append(north_west_chunk)
        west_chunk = self.get_chunk_by_position(
            Position(x, y - self["chunk_size"], z))
        chunks.append(west_chunk)
        mid_chunk = self.get_chunk_by_position(Position(x, y, z))
        chunks.append(mid_chunk)
        east_chunk = self.get_chunk_by_position(
            Position(x, y + self["chunk_size"], z))
        chunks.append(east_chunk)
        south_west_chunk = self.get_chunk_by_position(
            Position(x - self["chunk_size"], y - self["chunk_size"], z)
        )
        chunks.append(south_west_chunk)
        south_chunk = self.get_chunk_by_position(
            Position(x - self["chunk_size"], y, z))
        chunks.append(south_chunk)
        south_east_chunk = self.get_chunk_by_position(
            Position(x - self["chunk_size"], y + self["chunk_size"], z)
        )
        chunks.append(south_east_chunk)

        return chunks

    def get_character(self, ident):
        for tile in self.get_all_tiles():
            if tile["creature"] is not None and tile["creature"]["name"] == ident:
                print("found player:" + tile["creature"]["name"])
                return tile["creature"]
        else:
            return None

    # used in server restarts to populate Server.characters
    def get_all_characters(self):
        _ret_list = []
        for tile in self.get_all_tiles():
            if tile["creature"] is not None and tile["creature"]["name"] is not None:
                # print("found player:" + tile["creature"]["name"])
                _ret_list.append(tile["creature"])

        return _ret_list

    # attempts to take any object (creature, item, furniture) and put it in the right spot in the WORLDMAP
    def put_object_at_position(self, obj, position):
        # TODO: check if something is already there. right now it just replaces it
        tile = self.get_tile_by_position(position)
        self.get_chunk_by_position(position)["is_dirty"] = True
        if isinstance(obj, (Creature, Character, Monster)):
            tile["creature"] = obj
            return
        elif isinstance(obj, Terrain):
            tile["terrain"] = obj
            return
        elif isinstance(obj, Item):
            items = tile["items"]  # which is []
            items.append(obj)
            return
        elif isinstance(obj, Furniture):
            tile["furniture"] = obj
            return
        # a blueprint takes up the slot that the final object is.
        # e.g Terrain blueprint takes up the Terrain slot in the world map.
        elif isinstance(obj, Blueprint):
            if obj.type_of == "Terrain":
                tile["terrain"] = obj
                return
            elif obj.type_of == "Item":
                items = tile["items"]  # which is []
                items.append(obj)
                print("added blueprint for an Item.")
                return
            elif obj.type_of == "Furniture":
                tile["furniture"] = obj
                return

        # TODO: the rest of the types.

    # applys the json file to a chunk.
    def build_json_building_on_chunk(self, filename, position):
        start = time.time()
        # TODO: fill the chunk overmap tile with this om_terrain
        with open(filename) as json_file:
            data = json.load(json_file)
        # group = data['group']
        # overmap_terrain = data['overmap_terrain']
        floors = data["floors"]
        terrain = data["terrain"]  # list
        furniture = data["furniture"]  # list
        fill_terrain = data["fill_terrain"]  # string

        impassable_tiles = ["t_wall"]  # TODO: make this global
        for k, floor in floors.items():
            i, j = 0, 0
            for row in floor:
                i = 0
                for char in row:
                    impassable = False
                    t_position = Position(position["x"] + i, position["y"] + j, k)
                    self.put_object_at_position(Terrain(fill_terrain, impassable), t_position)  # use fill_terrain if unrecognized.
                    if char in terrain:
                        if terrain[char] in impassable_tiles:
                            impassable = True
                        self.put_object_at_position(Terrain(terrain[char], impassable), t_position)
                    elif char in furniture:
                        self.put_object_at_position(Furniture(furniture[char]), t_position)
                    else:
                        pass
                    i = i + 1
                j = j + 1
        end = time.time()
        duration = end - start
        print("Building {} took: {} seconds.".format(filename, duration))

    def move_creature_from_position_to_position(self, obj, from_position, to_position):
        from_tile = self.get_tile_by_position(from_position)
        to_tile = self.get_tile_by_position(to_position)
        if to_tile is None or from_tile is None:
            print("tile doesn't exist. This should NEVER get called. ")
            return False
        if from_position["z"] != to_position["z"]:  # check for stairs.
            if from_position["z"] < to_position["z"]:
                if from_tile["terrain"]["ident"] != "t_stairs_up":
                    print("no up stairs there")
                    return False
            elif from_position["z"] > to_position["z"]:
                if from_tile["terrain"]["ident"] != "t_stairs_down":
                    print("no down stairs there")
                    return False
        self.get_chunk_by_position(from_position)["is_dirty"] = True
        self.get_chunk_by_position(to_position)["is_dirty"] = True

        if to_tile["terrain"]["impassable"]:
            print("tile is impassable")
            return False
        # don't replace creatures in the tile if we move over them.
        if to_tile["creature"] is not None:
            print("creature is impassable")
            return False
        # print("moving checks passed")
        to_tile["creature"] = obj
        from_tile["creature"] = None
        return True

    def get_tiles_near_position(self, position, radius):
        # figure out a way to get all tile positions near a position so we can get_tile_by_position on them.
        ret_tiles = []
        for i in range(position["x"] - radius, position["x"] + radius + 1):
            for j in range(position["y"] - radius, position["y"] + radius + 1):
                dx = position["x"] - i
                dy = position["y"] - j
                distance = max(abs(dx), abs(dy))
                ret_tiles.append(
                    (self.get_tile_by_position(
                        Position(i, j, position["z"])), distance)
                )
        return ret_tiles

    def generate_city(self, size):
        size = int(size * 12)  # multiplier
        # this function creates a overmap that can be translated to build json buildings.
        # size is 1-10
        city_layout = dict()
        for i in range(size):
            city_layout[i] = dict()
            for j in range(size):
                city_layout[i][j] = "."  # . is grass or nothing

        # first place roads along the center lines of the city
        for tile in range(size):
            city_layout[int(size / 2)][tile] = "R"
            city_layout[tile][int(size / 2)] = "R"

        # figure out how many buildings of each we need to build
        num_buildings = size * size  # size squared.
        num_residential = int(
            num_buildings / 2 * 0.34
        )  # 34% percent of the total tiles are residential.
        num_commercial = int(num_buildings / 2 * 0.22)
        num_industrial = int(num_buildings / 2 * 0.22)

        num_hospitals = int(size / 12)
        num_police = int(size / 12)
        num_firedept = int(size / 12)
        num_jail = int(size / 12)

        # print("num_residential: " + str(num_residential))
        # print("num_commercial: " + str(num_commercial))
        # print("num_industrial: " + str(num_industrial))
        # print("num_hospitals: " + str(num_hospitals))
        # print("num_police: " + str(num_police))
        # print("num_firedept: " + str(num_firedept))
        # print("num_jail: " + str(num_jail))

        # put road every 4th tile with houses on either side.
        for j in range(1, size - 1):
            for i in range(
                random.randrange(0, 2), size - int(random.randrange(0, 2))
            ):  # draw horizontal lines.
                if i == int(size / 2):
                    continue  # don't overwrite the middle road.

                if j % 2 == 0:
                    city_layout[i][j] = "R"
                else:
                    if random.randrange(0, 10) == 0:
                        # rarely build a road between roads.
                        city_layout[i][j] = "R"
                        continue
                    city_layout[i][j] = "B"  # else build a building.

                # if we have a building to build
                if city_layout[i][j] == "B":
                    if num_residential > 0:
                        city_layout[i][j] = "r"
                        num_residential = num_residential - 1
                    elif num_commercial > 0:
                        city_layout[i][j] = "c"
                        num_commercial = num_commercial - 1
                    elif num_industrial > 0:
                        city_layout[i][j] = "i"
                        num_industrial = num_industrial - 1
                    elif num_hospitals > 0:
                        city_layout[i][j] = "H"
                        num_hospitals = num_hospitals - 1
                    elif num_jail > 0:
                        city_layout[i][j] = "J"
                        num_jail = num_jail - 1
                    elif num_police > 0:
                        city_layout[i][j] = "P"
                        num_police = num_police - 1
                    elif num_firedept > 0:
                        city_layout[i][j] = "F"
                        num_firedept = num_firedept - 1

        # if we haven't placed our city services we need to go back and add them.
        while num_police > 0 or num_firedept > 0 or num_jail > 0 or num_hospitals > 0:
            i = random.randrange(1, size - 1)
            j = random.randrange(1, size - 1)

            if city_layout[i][j] != "R":
                if num_police > 0:
                    city_layout[i][j] = "P"
                    num_police = num_police - 1
                elif num_firedept > 0:
                    city_layout[i][j] = "F"
                    num_firedept = num_firedept - 1
                elif num_jail > 0:
                    city_layout[i][j] = "J"
                    num_jail = num_jail - 1
                elif num_hospitals > 0:
                    city_layout[i][j] = "H"
                    num_hospitals = num_hospitals - 1

        for j in range(size):
            for i in range(size):
                print(str(city_layout[i][j]), end = '') # the visual feedback on the console.
            print()

        return city_layout

    # we use this in pathfinding.
    def get_adjacent_positions_non_impassable(self, position):
        ret_tiles = []
        tile0 = self.get_tile_by_position(
            Position(position["x"] + 1, position["y"], position["z"])
        )
        tile1 = self.get_tile_by_position(
            Position(position["x"] - 1, position["y"], position["z"])
        )
        tile2 = self.get_tile_by_position(
            Position(position["x"], position["y"] + 1, position["z"])
        )
        tile3 = self.get_tile_by_position(
            Position(position["x"], position["y"] - 1, position["z"])
        )

        if tile0 is not None and not tile0["terrain"]["impassable"]:
            ret_tiles.append(tile0["position"])
        if tile1 is not None and not tile1["terrain"]["impassable"]:
            ret_tiles.append(tile1["position"])
        if tile2 is not None and not tile2["terrain"]["impassable"]:
            ret_tiles.append(tile2["position"])
        if tile3 is not None and not tile3["terrain"]["impassable"]:
            ret_tiles.append(tile3["position"])

        return ret_tiles
