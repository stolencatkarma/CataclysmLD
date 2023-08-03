import json
import os
import random
import time
import pprint

from src.creature import Creature
from src.furniture import Furniture
from src.item import Item, Container, Blueprint
from src.monster import Monster
from src.character import Character
from src.position import Position
from src.terrain import Terrain

# weather = [WEATHER_CLEAR, WEATHER_RAIN, WEATHER_FOG, WEATHER_STORM, WEATHER_TORNADO]


class Worldmap(dict):
    # let's make the world map and fill it with chunks!

    def __init__(self):
        print("Initializing Worldmap..")
        self["CHUNKS"] = dict()  # dict of dicts for chunks. chunks are x, y
        #self["CHUNKS"]["x:y"]
        # search for chunks in the world folder to load.
        for root, _, files in os.walk("./world/"):
            for file_data in files:
                if file_data.endswith(".chunk"):
                    x = file_data.split(".")[0].split("_")[0]
                    y = file_data.split(".")[0].split("_")[1]
                    with open(root+file_data) as json_file:
                        data = json.load(json_file)
                        self["CHUNKS"][str(x) + "_" + str(y)] = data
                        self["CHUNKS"][str(x) + "_" + str(y)]["was_loaded"] = True
                        self["CHUNKS"][str(x) + "_" + str(y)]["is_dirty"] = False


    # save the chunk to disk.
    def save_chunk(self, chunk):
        path = str("./world/" + str(chunk["x"]) + "_" + str(chunk["y"]) + ".chunk")
        print("Saving", path, "to disk")
        with open(path, "w") as fp:
            json.dump(chunk, fp)

    def handle_chunks(self):
        # save as needed. check for dirty, stasis
        _chunks_to_save = []
        for _, chunk in self["CHUNKS"].items():
            if chunk["stasis"]:
                continue

            if chunk["time_to_stasis"] > 1:
               chunk["time_to_stasis"] = chunk["time_to_stasis"] - 1
            else:
                chunk["should_stasis"] = True

            if chunk["is_dirty"]:
                self.save_chunk(chunk)
                chunk["is_dirty"] = False

            if chunk["should_stasis"]:
                _dict = {}
                _dict["stasis"] = True
                _dict["x"] = chunk["x"]
                _dict["y"] = chunk["y"]
                self["CHUNKS"][str(chunk["x"]) + "_" + str(chunk["y"])] = _dict # use a small placeholder instead of completely removing it.

        return True

    # if you write a function that deals with chunk manipulation of any kind use this.
    # returns a chunk from a global position 
    # handles chunks that need to be created or manipulated.
    def get_chunk_by_position(self, position):
        x_count = 0
        x = position["x"]
        while x >= 13:
            x = x - 13
            x_count = x_count + 1

        y_count = 0
        y = position["y"]
        while y >= 13:
            y = y - 13
            y_count = y_count + 1

        _dict = str(x_count) + "_" + str(y_count)

        path = str("./world/" + str(_dict) + ".chunk")
        


        # chunks will either be loaded, stasis'd,  or non-existant. handle all three cases.
        # check if chunk exists on disk first. if not create it and load it into memory.
        if(os.path.isfile(path)):
            pass
        else:
            print("creating new chunk!", _dict)
            self["CHUNKS"][_dict] = Chunk(x_count, y_count)
            with open(path, "w") as fp:
                json.dump(self["CHUNKS"][_dict], fp)
            return self["CHUNKS"][_dict]
        
        # un-stasis (thaw) the chunk
        if self["CHUNKS"][_dict]["stasis"]:  # need to load it from disk and back into memory.
            print("thawing chunk ", _dict)
            with open(path) as json_file:
                self["CHUNKS"][_dict] = json.load(json_file)
                self["CHUNKS"][_dict]["stasis"] = False
                self["CHUNKS"][_dict]["should_stasis"] = False
                self["CHUNKS"][_dict]["time_to_stasis"] = 100
        
        return self["CHUNKS"][_dict]

       

    def get_tile_by_position(self, position):
        _chunk = self.get_chunk_by_position(position)
        # if chunk exists but a tile doesn't (usually a z-level) just make one.
        for tile in _chunk["tiles"]:
            if tile["position"] == position:
                return tile
        else:
            # print('creating new tile', position)
            newtile = {}
            newtile["position"] = position
            newtile["terrain"] = Terrain("t_dirt")  # make the earth
            newtile["creature"] = None  # one per tile.
            newtile["items"] = []  # can be zero to many items in a tile.
            newtile["furniture"] = None  # one furniture per tile
            # chunkdict["vehicle"] = None  # one per tile, but may be part of a bigger whole.
            newtile["lumens"] = 0 # lighting engine

            _chunk["tiles"].append(newtile)
            for tile in _chunk["tiles"]:
                if tile["position"] == position:
                    return tile


    def get_chunks_near_position(self, position):  # a localmap
        chunks = []
        # we should only need the 9 chunks around the chunk position
        x = position["x"]
        y = position["y"]
        z = position["z"]
        self["chunk_size"] = 13

        north_east_chunk = self.get_chunk_by_position(Position(x + self["chunk_size"], y + self["chunk_size"], z))
        chunks.append(north_east_chunk)

        north_chunk = self.get_chunk_by_position(Position(x + self["chunk_size"], y, z))
        chunks.append(north_chunk)

        north_west_chunk = self.get_chunk_by_position(Position(x + self["chunk_size"], y - self["chunk_size"], z))
        chunks.append(north_west_chunk)

        west_chunk = self.get_chunk_by_position(Position(x, y - self["chunk_size"], z))
        chunks.append(west_chunk)

        mid_chunk = self.get_chunk_by_position(Position(x, y, z))
        chunks.append(mid_chunk)

        east_chunk = self.get_chunk_by_position(Position(x, y + self["chunk_size"], z))
        chunks.append(east_chunk)

        south_west_chunk = self.get_chunk_by_position(Position(x - self["chunk_size"], y - self["chunk_size"], z))
        chunks.append(south_west_chunk)

        south_chunk = self.get_chunk_by_position(Position(x - self["chunk_size"], y, z))
        chunks.append(south_chunk)

        south_east_chunk = self.get_chunk_by_position(Position(x - self["chunk_size"], y + self["chunk_size"], z))
        chunks.append(south_east_chunk)

        # print("num chunks in localmap: " + str(len(chunks)))
        for chunk in chunks:
            chunk["time_to_stasis"] = 100  # keep used chunks from going to stasis

        return chunks

    def get_all_characters(self):
        ret_list = list()
        for _, chunk in self["CHUNKS"].items():
            for tile in chunk["tiles"]:
                if tile["creature"] is not None: # and isinstance(tile["creature"], Character):
                    # print("found player:" + tile["creature"]["name"])
                    ret_list.append(tile["creature"])
        return ret_list

    # attempts to take any object (creature, item, furniture) and put it in the right spot in the WORLDMAP
    def put_object_at_position(self, obj, position):
        # TODO: check if something is already there. right now it just replaces it
        tile = self.get_tile_by_position(position)
        #pprint.pprint(tile)
        self.get_chunk_by_position(position)["is_dirty"] = True
        if isinstance(obj, (Creature, Character, Monster)):
            tile["creature"] = obj
            tile["creature"]["position"] = position  # for the action queue.
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
            print("tile doesn't exist.")
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

        # Can't move into impassable terrain.
        if to_tile["terrain"]["impassable"]:
            print("tile is impassable")
            return False

        # Don't move over creatures. 1 per tile.
        if to_tile["creature"] is not None:
            print("creature is impassable")
            return False

        # cut from one and paste it to another.
        to_tile["creature"] = obj
        to_tile["creature"]["position"] = to_position  # update it for the action queue. makes life easier there.
        from_tile["creature"] = None

        self.get_chunk_by_position(from_position)["is_dirty"] = True
        self.get_chunk_by_position(to_position)["is_dirty"] = True
        return True

    def get_tiles_near_position(self, position, radius):
        # figure out a way to get all tile positions near a position, so we can get_tile_by_position on them.
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
        size = int(size * 13)  # multiplier
        # this function creates an overmap that can be translated to build json buildings.
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

        num_hospitals = int(size / 13)
        num_police = int(size / 13)
        num_firedept = int(size / 13)
        num_jail = int(size / 13)

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

        #for j in range(size):
            #for i in range(size):
                #print(str(city_layout[i][j]), end = '') # the visual feedback on the console.
            #print()

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



class Chunk(dict):
    def __init__(self, x, y):  # x, y relate to its position on the world map.
        self["chunk_size"] = 13  # 0-12 tiles in x and y, z-level 1 tile only (0).
        self["x"] = x
        self["y"] = y
        self["tiles"] = list()
        self["weather"] = "WEATHER_NONE"  # weather is per chunk.
        # the tile represented on the over map
        self["overmap_tile"] = "open_air"
        # set this to true to have the changes updated on the disk, default is True so worldgen writes it to disk
        self["is_dirty"] = False
        self["was_loaded"] = False
        self["should_stasis"] = False  # TODO: when we unload from memory we need a flag not to loop through it during compute turn
        self["stasis"] = False  # when a chunk is put into stasis.
        self["time_to_stasis"] = 100  # reduce by 1 every turn a player is not near it. set should_stasis when gets to zero

        # when a chunk is created for the first time fill with dirt and nothing else.
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
                # chunkdict["vehicle"] = None  # one per tile, but may be part of a bigger whole.
                chunkdict["lumens"] = 0 # lighting engine

                self["tiles"].append(chunkdict)

        end = time.time()
        duration = end - start
        print('chunk generation took: ' + str(duration) + ' seconds.')



