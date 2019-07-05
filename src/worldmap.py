import json
import os
import pickle
import pprint
import random
import time
import logging
from collections import defaultdict

from src.blueprint import Blueprint
from src.creature import Creature
from src.furniture import Furniture, FurnitureManager
from src.item import Item, ItemManager
from src.lighting import Lighting
from src.monster import Monster
from src.character import Character
from src.position import Position
from src.terrain import Terrain

# weather = [WEATHER_CLEAR, WEATHER_RAIN, WEATHER_FOG, WEATHER_STORM, WEATHER_TORNADO]


class Chunk:
    def __init__(
        self, x, y, z, chunk_size
    ):  # x, y, z relate to it's position on the world map.
        self.tiles = []
        self.weather = "WEATHER_NONE"  # weather is per chunk.
        self.overmap_tile = "open_air"  # the tile represented on the over map
        self.is_dirty = (
            True
        )  # set this to true to have the changes updated on the disk, default is True so worldgen writes it to disk
        self.was_loaded = "no"
        # start = time.time()
        for i in range(chunk_size):  # 0-13
            for j in range(chunk_size):  # 0-13
                chunkdict = {}
                chunkdict["position"] = Position(
                    i + int(x * chunk_size), j + int(y * chunk_size), z
                )  # this position is on the worldmap. no position is ever repeated. each chunk tile gets its own position.
                if int(z) <= 0:
                    chunkdict["terrain"] = Terrain("t_dirt")  # make the earth
                else:
                    chunkdict["terrain"] = Terrain("t_open_air")  # make the air
                chunkdict["creature"] = None  # Creature() # one creature per tile
                chunkdict["items"] = []  # can be more then one item in a tile.
                chunkdict["furniture"] = None  # single furniture per tile
                chunkdict["vehicle"] = None  # one per tile
                chunkdict["trap"] = None  # one per tile
                chunkdict[
                    "bullet"
                ] = None  # one per tile (TODO: figure out a better way)
                chunkdict[
                    "lumens"
                ] = (
                    1
                )  # used in lightmap calculations, use 1 for base so we never have total darkness.
                self.tiles.append(chunkdict)
        # end = time.time()
        # duration = end - start
        # print('chunk generation took: ' + str(duration) + ' seconds.')


class Worldmap:
    # let's make the world map and fill it with chunks!

    def __init__(self, WORLD_SIZE):  # size in chunks along one axis.
        self._log = logging.getLogger("worldmap")
        self.WORLD_SIZE = WORLD_SIZE
        self.WORLDMAP = defaultdict(dict)  # dict of dicts for chunks
        self.chunk_size = 13  # size of the chunk, leave it hardcoded here. (0-12)
        self.FurnitureManager = FurnitureManager()
        self.ItemManager = ItemManager()
        start = time.time()
        # TODO: only need to load the chunks where there are actual Characters present in memory after generation.
        self._log.debug("creating/loading world chunks")
        count = 0
        for i in range(self.WORLD_SIZE):
            for j in range(self.WORLD_SIZE):
                for k in range(0, 1):  # just load z0 for now. load the rest as needed.
                    self.WORLDMAP[i][j] = dict()
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
                        with open(path, "rb") as fp:
                            self.WORLDMAP[i][j][k] = pickle.load(fp)
                            self.WORLDMAP[i][j][k].was_loaded = "yes"
                        if count < self.WORLD_SIZE - 1:
                            count = count + 1
                        else:
                            count = 0
                    else:
                        self.WORLDMAP[i][j][k] = Chunk(i, j, k, self.chunk_size)
                        with open(path, "wb") as fp:
                            pickle.dump(self.WORLDMAP[i][j][k], fp)

        end = time.time()
        duration = end - start
        self._log.debug("---------------------------------------------")
        self._log.debug("World generation took: {} seconds".format(duration))

    def update_chunks_on_disk(
        self
    ):  # after our map in memory changes we need to update the chunk file on disk.
        for i in range(self.WORLD_SIZE):
            for j in range(self.WORLD_SIZE):
                for k, chunk in self.WORLDMAP[i][j].items():
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
                        if chunk.is_dirty:
                            with open(path, "wb") as fp:
                                self._log.debug(
                                    "{}_{}_{}.chunk is dirty. Saving changes to disk.".format(
                                        i, j, k
                                    )
                                )
                                self.WORLDMAP[i][j][k].is_dirty = False
                                pickle.dump(self.WORLDMAP[i][j][k], fp)

    def get_chunk_by_position(self, position):
        tile = self.get_tile_by_position(
            position
        )  # check and see if it exists if not create it.
        x_count = 0  #
        x = position.x
        while x >= self.chunk_size:
            x = x - self.chunk_size
            x_count = x_count + 1

        y_count = 0  #
        y = position.y
        # worldmap[x][y].tiles
        while y >= self.chunk_size:
            y = y - self.chunk_size
            y_count = y_count + 1

        z = position.z

        # self._log.debug('getting chunk {} {}'.format(x_count, y_count))
        return self.WORLDMAP[x_count][y_count][z]

    def get_all_tiles(self):
        ret = []
        self._log.debug("getting all tiles")
        for i, dictionary_x in self.WORLDMAP.items():
            for j, dictionary_y in dictionary_x.items():
                for k, chunk in dictionary_y.items():
                    for tile in chunk.tiles:
                        ret.append(tile)
        self._log.debug("all tiles: {}".format(len(ret)))
        return ret  # expensive function. use sparingly.

    def get_tile_by_position(self, position):
        x_count = 0  # these two little loop gets us the right chunk FAST
        x = position.x
        while x >= self.chunk_size:
            x = x - self.chunk_size
            x_count = x_count + 1

        y_count = 0  #
        y = position.y
        while y >= self.chunk_size:
            y = y - self.chunk_size
            y_count = y_count + 1

        z = position.z

        try:
            for tile in self.WORLDMAP[x_count][y_count][z].tiles:
                if tile["position"] == position:
                    return tile
            #else:
            #    raise Exception("FATAL ERROR: couldn't find chunk for tile")
        except Exception:
            # if it doesn't exist yet (exception) we need to create it and return it.
            self.WORLDMAP[x_count][y_count][z] = Chunk(
                x_count, y_count, z, self.chunk_size
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
            with open(path, "wb") as fp:
                pickle.dump(self.WORLDMAP[x_count][y_count][z], fp)
                for tile in self.WORLDMAP[x_count][y_count][z].tiles:
                    if tile["position"] == position:
                        return tile
                else:
                    print('position we couldnt find', str(position))
                    raise Exception(
                        "ERROR: Could not find tile or create it. (this should never happen)"
                    )

    def get_chunks_near_position(self, position):  # a localmap
        chunks = []
        # we should only need the 9 chunks around the chunk position
        x = position.x
        y = position.y
        z = position.z

        north_east_chunk = self.get_chunk_by_position(
            Position(x + self.chunk_size, y + self.chunk_size, z)
        )
        chunks.append(north_east_chunk)
        north_chunk = self.get_chunk_by_position(Position(x + self.chunk_size, y, z))
        chunks.append(north_chunk)
        north_west_chunk = self.get_chunk_by_position(
            Position(x + self.chunk_size, y - self.chunk_size, z)
        )
        chunks.append(north_west_chunk)
        west_chunk = self.get_chunk_by_position(Position(x, y - self.chunk_size, z))
        chunks.append(west_chunk)
        mid_chunk = self.get_chunk_by_position(Position(x, y, z))
        chunks.append(mid_chunk)
        east_chunk = self.get_chunk_by_position(Position(x, y + self.chunk_size, z))
        chunks.append(east_chunk)
        south_west_chunk = self.get_chunk_by_position(
            Position(x - self.chunk_size, y - self.chunk_size, z)
        )
        chunks.append(south_west_chunk)
        south_chunk = self.get_chunk_by_position(Position(x - self.chunk_size, y, z))
        chunks.append(south_chunk)
        south_east_chunk = self.get_chunk_by_position(
            Position(x - self.chunk_size, y + self.chunk_size, z)
        )
        chunks.append(south_east_chunk)

        # up_chunk = self.get_chunk_by_position(Position(x, y, z+1))
        # chunks.append(up_chunk)

        # down_chunk = self.get_chunk_by_position(Position(x, y, z-1))
        # chunks.append(down_chunk)

        return chunks

    def get_character(self, ident):
        for tile in self.get_all_tiles():
            if tile["creature"] is not None and tile["creature"].name == ident:
                print("found player:" + tile["creature"].name)
                return tile["creature"]
        else:
            return None
    
    # used in server restarts to populate Server.characters
    def get_all_characters(self):
        _ret_list = []
        for tile in self.get_all_tiles():
            if tile["creature"] is not None and isinstance(tile["creature"], Character):
                print("found player:" + tile["creature"].name)
                _ret_list.append(tile["creature"])
        
        return _ret_list

    def put_object_at_position(
        self, obj, position
    ):  # attempts to take any object (creature, item, furniture) and put it in the right spot in the WORLDMAP
        # TODO: check if something is already there. right now it just replaces it
        tile = self.get_tile_by_position(position)
        self.get_chunk_by_position(position).is_dirty = True
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
        elif isinstance(
            obj, Blueprint
        ):  # a blueprint takes up the slot that the final object is. e.g Terrain blueprint takes up the Terrain slot in the world map.
            if obj.type_of == "Terrain":
                tile["terrain"] = obj
                return
            elif obj.type_of == "Item":
                items = tile["items"]  # which is []
                items.append(obj)
                self._log.debug("added blueprint for an Item.")
                return
            elif obj.type_of == "Furniture":
                tile["furniture"] = obj
                return

        # TODO: the rest of the types.

    def build_json_building_at_position(
        self, filename, position
    ):  # applys the json file to world coordinates. can be done over multiple chunks.
        self._log.debug("building: {} at {}".format(filename, position))
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
                    t_position = Position(position.x + i, position.y + j, k)
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
        self._log.debug("Building {} took: {} seconds.".format(filename, duration))

    def move_object_from_position_to_position(self, obj, from_position, to_position):
        from_tile = self.get_tile_by_position(from_position)
        to_tile = self.get_tile_by_position(to_position)
        if to_tile is None or from_tile is None:
            self._log.error(
                "tile doesn't exist. This should NEVER get called. get_tile_by_position creates a new chunk and tiles if we need it."
            )
            return False
        if from_position.z != to_position.z:  # check for stairs.
            if from_position.z < to_position.z:
                if from_tile["terrain"].ident != "t_stairs_up":
                    print("no up stairs there")
                    return False
            elif from_position.z > to_position.z:
                if from_tile["terrain"].ident != "t_stairs_down":
                    print("no down stairs there")
                    return False
        self.get_chunk_by_position(from_position).is_dirty = True
        self.get_chunk_by_position(to_position).is_dirty = True
        if isinstance(obj, (Creature, Character, Monster)):
            self._log.debug(
                "moving {} from {} to {}.".format(obj, from_position, to_position)
            )
            if to_tile["terrain"].impassable:
                self._log.debug("tile is impassable")
                return False
            if (
                to_tile["creature"] is not None
            ):  # don't replace creatures in the tile if we move over them.
                self._log.debug("creature is impassable")
                return False
            to_tile["creature"] = obj
            from_tile["creature"] = None
            return True
        if isinstance(obj, Terrain):
            to_tile["terrain"] = obj
            return True
        if obj is Item:
            print(
                "Moving "
                + str(obj)
                + " from "
                + str(from_tile["position"])
                + " to "
                + str(to_tile["position"])
            )
            if obj in from_tile["items"][:]:  # iterate a copy to remove properly.
                # items = tile['item'] # which is []
                from_tile["items"].remove(obj)
                to_tile["items"].append(obj)
            else:
                pass
            return True
        if obj is Furniture:
            if to_tile["furniture"] is not None:
                self._log.debug("already furniture there.")
                return False
            to_tile["furniture"] = obj
            from_tile["furniture"] = None
            return True
        # TODO: the rest of the types.

    def bash(
        self, object, position
    ):  # catch-all for bash/smash (can probably use this for vehicle collisions aswell) object is object that is doing the bashing
        # since we bash in a direction we need to check what's in the tile and go from there.
        # both furniture and terrain can be bashed but we should assume that the player wants to bash the furniture first then terrain we will go in that order.
        tile = self.get_tile_by_position(position)
        terrain = tile["terrain"]
        # strength = creature strength.
        if tile["furniture"] is not None:
            furniture_type = self.FurnitureManager.FURNITURE_TYPES[
                tile["furniture"].ident
            ]
            for item in furniture_type["bash"]["items"]:
                self.put_object_at_position(
                    Item(
                        self.ItemManager.ITEM_TYPES[str(item["item"])]["ident"],
                        self.ItemManager.ITEM_TYPES[str(item["item"])],
                    ),
                    position,
                )  # need to pass the reference to load the item with data.
            tile["furniture"] = None
            # get the 'bash' dict for this object from furniture.json
            # get 'str_min'
            # if player can break it then delete the furniture and add the bash items from it to the tile.
            return
        if terrain is not None:
            # get the 'bash' dict for this object from terrain.json if any
            # if dict is not None:
            # get 'str_min'
            # if player can break it then delete the terrain and add the bash terrain from it to the tile.
            return
        return

    def furniture_open(self, object, position):  # the object doing the opening.
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

    def furniture_close(self, object, position):  # the object doing the opening.
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
        for i in range(position.x - radius, position.x + radius + 1):
            for j in range(position.y - radius, position.y + radius + 1):
                dx = position.x - i
                dy = position.y - j
                distance = max(abs(dx), abs(dy))
                ret_tiles.append(
                    (self.get_tile_by_position(Position(i, j, position.z)), distance)
                )
        return ret_tiles

    def generate_city(self, size):
        size = int(size * 12)  # multiplier
        # this function creates a overmap that can be translated to build json buildings.
        # size is 1-10
        city_layout = defaultdict(dict)
        for j in range(size):
            for i in range(size):
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

        self._log.debug("num_residential: " + str(num_residential))
        self._log.debug("num_commercial: " + str(num_commercial))
        self._log.debug("num_industrial: " + str(num_industrial))
        self._log.debug("num_hospitals: " + str(num_hospitals))
        self._log.debug("num_police: " + str(num_police))
        self._log.debug("num_firedept: " + str(num_firedept))
        self._log.debug("num_jail: " + str(num_jail))

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
                        city_layout[i][j] = "R"  # rarely build a road between roads.
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
                #print(str(city_layout[i][j]), end = '') # the visual feedback on the console.
                pass

        return city_layout

    def get_adjacent_positions_non_impassable(
        self, position
    ):  # we use this in pathfinding.
        ret_tiles = []
        tile0 = self.get_tile_by_position(
            Position(position.x + 1, position.y, position.z)
        )
        tile1 = self.get_tile_by_position(
            Position(position.x - 1, position.y, position.z)
        )
        tile2 = self.get_tile_by_position(
            Position(position.x, position.y + 1, position.z)
        )
        tile3 = self.get_tile_by_position(
            Position(position.x, position.y - 1, position.z)
        )

        if not tile0["terrain"].impassable:
            ret_tiles.append(tile0["position"])
        if not tile1["terrain"].impassable:
            ret_tiles.append(tile1["position"])
        if not tile2["terrain"].impassable:
            ret_tiles.append(tile2["position"])
        if not tile3["terrain"].impassable:
            ret_tiles.append(tile3["position"])

        return ret_tiles
