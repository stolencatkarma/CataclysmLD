import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict

import pyglet
import glooey
from pyglet.window import key as KEY
from pyglet import clock

from Mastermind._mm_client import MastermindClientTCP

from src.action import Action
from src.blueprint import Blueprint
from src.command import Command
from src.item import Item, ItemManager
from src.player import Player
from src.position import Position
from src.recipe import Recipe, RecipeManager
from src.tileManager import TileManager
from src.worldmap import Worldmap


class Client(MastermindClientTCP): # extends MastermindClientTCP
    def __init__(self, first_name, last_name):
        MastermindClientTCP.__init__(self)
        self.chunk_size = (13,13)
        self.TileManager = TileManager()
        pyglet.resource.path = ['tilesets/Chesthole32/tiles','tilesets/Chesthole32/tiles/background','tilesets/Chesthole32/tiles/monsters','tilesets/Chesthole32/tiles/terrain']
        pyglet.resource.reindex()
        self.ItemManager = ItemManager()
        self.RecipeManager = RecipeManager() # contains all the known recipes in the game. for reference.
        self.player = Player(str(first_name) + str(last_name)) # recieves updates from server. the player and all it's stats.
        self.localmap = None
        self.hotbars = []
        self.map_grid = glooey.Grid(self.chunk_size[0], self.chunk_size[1], 32, 32) # chunk_size + tilemap size
        self.map_grid.set_left_padding(32) # for the border.
        self.map_grid.set_top_padding(32)
                
        for i in range(self.chunk_size[0]): # glooey uses y,x for grids from the top left.
            for j in range(self.chunk_size[1]):
                self.map_grid.add(i, j, glooey.images.Image(pyglet.resource.texture('t_grass.png'))) # before we get an update we need to init the map with grass.

        #self.hotbars.insert(0, Hotbar(self.screen, 10, 10))
        
        window = pyglet.window.Window(854, 480)
        
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        
        gui = glooey.Gui(window)

        bg = glooey.Background()
        bg.set_appearance(
            center=pyglet.resource.texture('center.png'),
            top=pyglet.resource.texture('top.png'),
            bottom=pyglet.resource.texture('bottom.png'),
            left=pyglet.resource.texture('left.png'),
            right=pyglet.resource.texture('right.png'),
            top_left=pyglet.resource.texture('top_left.png'),
            top_right=pyglet.resource.texture('top_right.png'),
            bottom_left=pyglet.resource.texture('bottom_left.png'),
            bottom_right=pyglet.resource.texture('bottom_right.png')
            )

        gui.add(bg)
        gui.add(self.map_grid)

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == KEY.RETURN:
                print('return')
            if symbol == KEY.W:
                command = Command(self.player.name, 'move', ['north'])
                client.send(command)


    def find_player_in_localmap(self):
        for tile in self.localmap:
            if(tile['creature'] is not None):
                if(tile['creature'].name == self.player.name):
                    return tile['creature']
        else:
            print('couldn\'t find player')

    def convert_chunks_to_localmap(self, list_of_chunks):
        tiles = []
        for chunk in list_of_chunks:
            for tile in chunk.tiles:
                tiles.insert(len(tiles), tile)
        return tiles

    def lerp(self, start, end, t):
        return start + t * (end-start)

    def lerp_point(self, p0, p1, t):
        return (int(self.lerp(p0[0], p1[0], t)), int(self.lerp(p0[1], p1[1], t)))

    def diagonal_distance(self, p0, p1):
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        return max(abs(dx), abs(dy))

    def line(self, p0, p1):
        points = []
        diagonal_distance = self.diagonal_distance(p0, p1)
        for step in range(diagonal_distance):
            points.append(self.lerp_point(p0, p1, step/diagonal_distance))
        return points # so now we have a set of points along a line.

    def trim_localmap(self, origin_position, radius=10):
        # origin_position = origin_position # store the player position for fov origin
        # convert chunks to grid
        level = defaultdict(dict)
        for tile in self.localmap[:]: # we only need the tiles around radius.
            if int(tile['position'].x) < origin_position.x-radius or int(tile['position'].x) > origin_position.x+radius+1:
                self.localmap.remove(tile)
            elif int(tile['position'].y) < origin_position.y-radius or int(tile['position'].y) > origin_position.y+radius+1:
                self.localmap.remove(tile)
            else:
                level[str(tile['position'].x)][str(tile['position'].y)] = tile['terrain'].impassable # so either remove a tile or figure out if it's impassable.

        # draw a line to each edge of the viewport using grid_edges
        # x's include top row and bottom rows, y's include min and max of viewport.
        grid_edges = []
        # now we have a level grid. let's get our edges so we can plot lines from origin to edge.
        for x in range(origin_position.x-radius, origin_position.x+radius+1): # X
            grid_edges.append((x, origin_position.y-radius))
            grid_edges.append((x, origin_position.y+radius))
        for y in range(origin_position.y-radius, origin_position.y+radius+1): # Y
            grid_edges.append((origin_position.x-radius, y))
            grid_edges.append((origin_position.x+radius, y))
        #print('grid_edges: ' + str(len(grid_edges)))

        tiles_to_keep = []
        # now we need to remove tiles which are out of our field of view.
        for destination in grid_edges:
            for point in self.line((origin_position.x, origin_position.y), destination):
                if level[str(point[0])][str(point[1])] == True: # (impassable)
                    tiles_to_keep.append(point) # do this to keep the blocking wall visible.
                    break # hit a wall. move on to the next ray.
                else:
                    tiles_to_keep.append(point)

        for tiles in self.localmap[:]: # iterate a copy to remove correctly.
            for point in tiles_to_keep:
                if tiles['position'].x == point[0] and tiles['position'].y == point[1]:
                    break
            else:
                self.localmap.remove(tiles)

    def update_map_for_position(self, position):
        if(self.localmap is not None):
            # our map_grid is 13x13 but our localmap contains 13*3 x 13*3 tiles worth of chunks so we need
            # to draw the viewport from the position only 13x13
            position = self.convert_position_to_local_coords(position)
            # first set terrain to the terrain image
            for tile in self.localmap:
                _pos = self.convert_position_to_local_coords(tile['position']) # (0-38, 0-38)
                x = _pos.x - position.x + 6
                y = _pos.y - position.y + 6
                if(x < 0 or x > 12):
                    continue
                if(y < 0 or y > 12):
                    continue
                self.map_grid[x, y].set_image(pyglet.resource.texture(tile['terrain'].ident + '.png')) # must be (0-12, 0-12)
            
                # then overlay furniture on that.
                if(tile['furniture'] is not None):
                    self.map_grid[x, y].set_image(pyglet.resource.texture(tile['furniture'].ident + '.png'))
                
                # then overlay items on that.
                if(tile['items'] is not None and len(tile['items']) > 0):
                    self.map_grid[x, y].set_image(pyglet.resource.texture(tile['items'][0].ident + '.png')) # just show the first item

                # then overlay creatures on that.
                if(tile['creature'] is not None):
                    self.map_grid[x, y].set_image(pyglet.resource.texture(tile['creature'].tile_ident + '.png'))
            
            print('FPS:', pyglet.clock.get_fps())

    def convert_position_to_local_coords(self, position):
        # local coordinates are always from (0,0) to (chunk.size[1] * 3 , chunk.size[0] * 3)
        # and must return a position within that size.
        x = position.x
        y = position.y
        z = position.z

        while x >= self.chunk_size[0]*3:
            x = x - self.chunk_size[0]*3
        while y >= self.chunk_size[1]*3:
            y = y - self.chunk_size[1]*3
        
        return Position(x,y,z)

    def draw_view_at_position(self, draw_position):
        #TODO: lerp the positions of creatures from one frame to the next.
        self.trim_localmap(draw_position) # update field of view and lighting

        # at this point the localmap should've been trimmed of unseeable tiles. draw what's left at position.
        for tile in self.localmap: # draw the localmap for the controlling player.
            terrain = tile['terrain']
            position = tile['position'] # Position(x, y, z)
            creature = tile['creature'] # Creature()
            furniture = tile['furniture'] # Furniture()
            items = tile['items'] # list [] of Item()
            light_intensity = tile['lumens']

            fg = self.TileManager.TILE_TYPES[terrain.ident]['fg']
            bg = self.TileManager.TILE_TYPES[terrain.ident]['bg']

            x = draw_position.x - position.x - (self.chunk_size[0]//2) # offset to put position in middle of viewport
            y = draw_position.y - position.y - (self.chunk_size[1]//2) # offset to put position in middle of viewport

            '''# first blit terrain
            if(bg is not None):
                self.screen.blit(self.TileManager.TILE_MAP[bg], (x*24, y*24)) # blit background of the terrain
            if(fg is not None):
                self.screen.blit(self.TileManager.TILE_MAP[fg], (x*24, y*24)) # blit foreground of the terrain

            # then blit furniture
            if(furniture is not None):
                fg = self.TileManager.TILE_TYPES[furniture.ident]['fg']
                self.screen.blit(self.TileManager.TILE_MAP[fg], (x*24, y*24))

            # then blit items (if there is a pile of items check and see if any are blueprints. if so show those.)
            if(len(items) > 0):
                for item in items:
                    # always show blueprints on top.
                    if(isinstance(item, Blueprint)):
                        fg = self.TileManager.TILE_TYPES[items[0].ident]['fg']
                        self.screen.blit(self.TileManager.TILE_MAP[fg], (x*24, y*24))
                        break
                else:
                    # only display the first item 
                    fg = self.TileManager.TILE_TYPES[items[0].ident]['fg']
                    self.screen.blit(self.TileManager.TILE_MAP[fg], (x*24, y*24))

            # then blit vehicles

            # then blit player and creatures and monsters (all creature types)
            if(creature is not None):
                self.screen.blit(self.TileManager.TILE_MAP[creature.tile_id], (x*24, y*24)) # TODO: need to build it if the player is wearing clothes, etc...
            '''
            # darken based on lumen level of the tile
            # light_intensity # 10 is max light level although lumen level may be higher.
            # light_intensity = min(int((255-(light_intensity*25))/3), 255)
            # light_intensity = max(light_intensity, 0)
            # self.screen.fill((light_intensity, light_intensity, light_intensity), rect=(x*24, y*24, 24, 24), special_flags=pygame.BLEND_SUB)

            # render debug text


            # then blit weather. Weather is the only thing above players and creatures.
            #TODO: blit weather
      

    def open_crafting_menu(self):
        list_of_known_recipes = []
        for key, value in self.RecipeManager.RECIPE_TYPES.items(): #TODO: Don't just add them all. Pull them from creature.known_recipes
            list_of_known_recipes.append(value)


    def open_movement_menu(self, pos, tile):
        #_command = Command(client.player.name, 'calculated_move', (tile['position'].x, tile['position'].y, tile['position'].z)) # send calculated_move action to server and give it the position of the tile we clicked.
        # return _command
        pass

    def open_super_menu(self, pos, tile):
        pass

    def open_blueprint_menu(self, pos, tile):
        # blueprint_menu = Blueprint_Menu(self.screen, (0, 0, 400, 496), self.FontManager, self.TileManager)
        pass 

    def open_equipment_menu(self):
        # equipment_menu = Equipment_Menu(self.screen, (0, 0, 400, 496), self.FontManager, self.TileManager, self.player.body_parts)
        pass

    def open_items_on_ground(self, pos, tile):
        # _command = Command(self.player.name, 'move_item_to_player_storage', (tile['position'].x, tile['position'].y, tile['position'].z, item.ident)) # ask the server to pickup the item by ident. #TODO: is there a better way to pass it to the server without opening ourselves up to cheating?
        # return _command
        pass


#
#   if we start a client directly
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cataclysm LD Client', epilog="Please start the client with a first and last name for your character.")
    parser.add_argument('--host', metavar='Host', help='Server host', default='localhost')
    parser.add_argument('--port', metavar='Port', type=int, help='Server port', default=6317)
    parser.add_argument('first_name', help='Player\'s first name')
    parser.add_argument('last_name', help='Player\'s last name')

    args = parser.parse_args()
    ip = args.host
    port = args.port

    client = Client(args.first_name, args.last_name)
    client.connect(ip, port)
    command = Command(client.player.name, 'login', ['password'])
    client.send(command)
    command = Command(client.player.name, 'request_localmap_update')
    client.send(command)
    command = None

    # if we recieve an update from the server process it. do this first.
    
    def check_messages_from_server(dt):
        next_update = client.receive(False)
        if(next_update is not None):
            #print('--next_update--') # we recieved a message from the server. let's process it.
            #print(type(next_update))
            if(isinstance(next_update, Player)):
                #print('got playerupdate')
                client.player = next_update # client.player is updated
            elif(isinstance(next_update, list)): # this is the list of chunks for the localmap compressed with zlib and pickled to binary
                #print('got local mapupdate')
                client.localmap = client.convert_chunks_to_localmap(next_update)
                client.player = client.find_player_in_localmap()
                client.update_map_for_position(client.player.position)
                # client.draw_view_at_position(client.player.position) # update after everything is complete.

           
        
    def ping(dt):
        command = Command(client.player.name, 'ping')
        client.send(command)

    clock.schedule_interval(check_messages_from_server, 0.25)
    clock.schedule_interval(ping, 30.0) # our keep-alive event. without this the server would disconnect if we don't send data within the timeout for the server.
    
    
    pyglet.app.event_loop.run() # main event loop starts here.

    
