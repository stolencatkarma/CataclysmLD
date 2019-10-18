import json
import os
import random
import time

from src.blueprint import Blueprint
from src.creature import Creature
from src.model.manager.furniture import Furniture
from src.model.manager.item import Item
from src.model.manager.monster import Monster
from src.character import Character
from src.position import Position
from src.terrain import Terrain

# weather = [WEATHER_CLEAR, WEATHER_RAIN, WEATHER_FOG, WEATHER_STORM, WEATHER_TORNADO]


class Chunk(dict):
    def __init__(
        self, x, y, z, chunk_size
    ):  # x, y, z relate to it's position on the world map.
        self["tiles"] = list()
        self["weather"] = "WEATHER_NONE"  # weather is per chunk.
        # the tile represented on the over map
        self["overmap_tile"] = "open_air"
        # set this to true to have the changes updated on the disk, default is True so worldgen writes it to disk
        self["is_dirty"] = True
        self["was_loaded"] = False
        # start = time.time()
        for i in range(chunk_size):  # 0-13
            for j in range(chunk_size):  # 0-13
                chunkdict = {}
                # this position is on the worldmap. no position is ever repeated. each chunk tile gets its own position.
                chunkdict["position"] = Position(
                    i + int(x * chunk_size), j + int(y * chunk_size), z)
                if int(z) <= 0:
                    chunkdict["terrain"] = Terrain("t_dirt")  # make the earth
                else:
                    chunkdict["terrain"] = Terrain(
                        "t_open_air")  # make the air
                # Creature() # one creature per tile
                chunkdict["creature"] = None
                chunkdict["items"] = []  # can be zero to many items in a tile.
                chunkdict["furniture"] = None  # single furniture per tile
                chunkdict["vehicle"] = None  # one per tile
                # used in lightmap calculations, use 1 for base so we never have total darkness.
                chunkdict["lumens"] = 1
                self["tiles"].append(chunkdict)
        # end = time.time()
        # duration = end - start
        # print('chunk generation took: ' + str(duration) + ' seconds.')


class Worldmap(dict):
    # let's make the world map and fill it with chunks!

    def __init__(self, size):  # size in chunks along one axis.
        self["WORLD_SIZE"] = size
        self["WORLDMAP"] = dict()  # dict of dicts for chunks
        # size of the chunk, leave it hardcoded here. (0-12)
        self["chunk_size"] = 13
        start = time.time()
        # TODO: only need to load the chunks where there are actual Characters present in memory after generation.
        print("creating/loading world chunks")
        count = 0
        for i in range(self["WORLD_SIZE"]):
            self["WORLDMAP"][i] = dict()
            for j in range(self["WORLD_SIZE"]):
                # just load z0 for now. load the rest as needed.
                for k in range(0, 1):
                    self["WORLDMAP"][i][j] = dict()
                    path = str(
                        "./worlds/default/"
                        + str(i)
                        + "_"
                        + str(j)
                        + "_"
                        + str(k)
                        + ".chunk"
                    )

                    if os.path.isfile(
                        path
                    ):  # if the chunk already exists on disk just load it.
                        with open(path, "r") as fp:
                            self["WORLDMAP"][i][j][k] = json.loads(fp.read())
                            self["WORLDMAP"][i][j][k]["was_loaded"] = "yes"
                        if count < self["WORLD_SIZE"] - 1:
                            count = count + 1
                        else:
                            count = 0
                    else:
                        self["WORLDMAP"][i][j][k] = Chunk(
                            i, j, k, self["chunk_size"])
                        with open(path, "w") as fp:
                            json.dump(self["WORLDMAP"][i][j][k], fp)

        end = time.time()
        duration = end - start
        print("---------------------------------------------")
        print("World generation took: {} seconds".format(duration))

    def update_chunks_on_disk(
        self
    ):  # after our map in memory changes we need to update the chunk file on disk.
        for i in range(self["WORLD_SIZE"]):
            for j in range(self["WORLD_SIZE"]):
                for k, chunk in self["WORLDMAP"][i][j].items():
                    path = str(
                        "./worlds/default/"
                        + str(i)
                        + "_"
                        + str(j)
                        + "_"
                        + str(k)
                        + ".chunk"
                    )
                    if os.path.isfile(path):
                        if chunk["is_dirty"]:
                            with open(path, "w") as fp:
                                self["WORLDMAP"][i][j][k]["is_dirty"] = False
                                json.dump(chunk, fp)

    def get_chunk_by_position(self, position):
        # check and see if it exists if not create it.
        tile = self.get_tile_by_position(position)
        x_count = 0
        x = position["x"]
        while x >= self["chunk_size"]:
            x = x - self["chunk_size"]
            x_count = x_count + 1

        y_count = 0  #
        y = position["y"]
        # worldmap[x][y]['tiles']
        while y >= self["chunk_size"]:
            y = y - self["chunk_size"]
            y_count = y_count + 1

        z = position["z"]

        # print('getting chunk {} {}'.format(x_count, y_count))
        return self["WORLDMAP"][x_count][y_count][z]

    def get_all_tiles(self):
        ret = []
        # print("getting all tiles")
        for i, dictionary_x in self["WORLDMAP"].items():
            for j, dictionary_y in dictionary_x.items():
                for k, chunk in dictionary_y.items():
                    for tile in chunk["tiles"]:
                        ret.append(tile)
        # print("all tiles: {}".format(len(ret)))
        return ret  # expensive function. use sparingly.

    def get_tile_by_position(self, position):
        x_count = 0  # these two little loop gets us the right chunk FAST
        x = position["x"]
        while x >= self["chunk_size"]:
            x = x - self["chunk_size"]
            x_count = x_count + 1

        y_count = 0  #
        y = position["y"]
        while y >= self["chunk_size"]:
            y = y - self["chunk_size"]
            y_count = y_count + 1

        z = position["z"]

        try:
            for tile in self["WORLDMAP"][x_count][y_count][z]["tiles"]:
                if tile["position"] == position:
                    return tile
            # else:
            #    raise Exception("FATAL ERROR: couldn't find chunk for tile")
        except Exception:
            # if it doesn't exist yet (exception) we need to create it and return it.
            self["WORLDMAP"][x_count][y_count][z] = Chunk(
                x_count, y_count, z, self["chunk_size"]
            )
            path = str(
                "./worlds/default/"
                + str(x_count)
                + "_"
                + str(y_count)
                + "_"
                + str(z)
                + ".chunk"
            )
            with open(path, "w") as fp:
                fp = json.dumps(self["WORLDMAP"][x_count][y_count][z])
                for tile in self["WORLDMAP"][x_count][y_count][z]["tiles"]:
                    if tile["position"] == position:
                        return tile
                else:
                    print("position we couldnt find", str(position))
                    raise Exception(
                        "ERROR: Could not find tile or create it. (this should never happen)"
                    )

    def get_chunks_near_position(self, position):  # a localmap
        chunks = []
        # we should only need the 9 chunks around the chunk position
        x = position["x"]
        y = position["y"]
        z = position["z"]

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

        # up_chunk = self.get_chunk_by_position(Position(x, y, z+1))
        # chunks.append(up_chunk)

        # down_chunk = self.get_chunk_by_position(Position(x, y, z-1))
        # chunks.append(down_chunk)

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
                print("found player:" + tile["creature"]["name"])
                _ret_list.append(tile["creature"])

        return _ret_list

    def put_object_at_position(
        self, obj, position
    ):  # attempts to take any object (creature, item, furniture) and put it in the right spot in the WORLDMAP
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

    def build_json_building_at_position(
        self, filename, position
    ):  # applys the json file to world coordinates. can be done over multiple chunks.
        # print("building: {} at {}".format(filename, position))
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
                    t_position = Position(
                        position["x"] + i, position["y"] + j, k)
                    self.put_object_at_position(
                        Terrain(fill_terrain, impassable), t_position
                    )  # use fill_terrain if unrecognized.
                    if char in terrain:
                        if terrain[char] in impassable_tiles:
                            impassable = True
                        self.put_object_at_position(
                            Terrain(terrain[char], impassable), t_position
                        )
                    elif char in furniture:
                        self.put_object_at_position(
                            Furniture(furniture[char]), t_position
                        )
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

    def furniture_open(self, object, position):  # the object doing the opening
        tile = self.get_tile_by_position(position)
        furniture = tile["furniture"]
        if furniture is not None:
            if "open" in furniture:  #
                # replace this furniture with the open version.
                # make sure to copy any items in it to the new one.
                pass
        else:
            return False
        return

    # the object doing the opening.
    def furniture_close(self, object, position):
        tile = self.get_tile_by_position(position)
        furniture = tile["furniture"]
        if furniture is not None:
            if "close" in furniture:  #
                # replace this furniture with the closed version.
                # make sure to copy any items in it to the new one.
                pass
        else:
            return False
        return

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
                # print(str(city_layout[i][j]), end = '') # the visual feedback on the console.
                pass

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
