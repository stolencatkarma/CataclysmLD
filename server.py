import argparse
import json
import os
import random
import sys
import time
import pprint
from collections import defaultdict

import src.global_vars
from Mastermind._mm_server import MastermindServerTCP
from src.action import Action
from src.blueprint import Blueprint
from src.calendar import Calendar
from src.command import Command
from src.furniture import Furniture, FurnitureManager
from src.item import Container, Item
from src.options import Options
from src.player import Player
from src.position import Position
from src.recipe import Recipe, RecipeManager
from src.terrain import Terrain
from src.tileManager import TileManager
from src.profession import ProfessionManager, Profession
from src.monster import MonsterManager
#import game
from src.worldmap import Worldmap

#import pygame
#import pygame.locals




class OverMap: # when the player pulls up the OverMap. a OverMap for each player will have to be stored for undiscovered areas and when they use maps.
    def __init__(self): # the ident of the player who owns this overmap.
        # over map size is the worldmap size
        # build the overmap from seen tiles, roadmaps, maps.
        # if a player sees a chunk loaded it's safe to say they 'saw' that overmap tile.
        return

#ClassServer = MastermindServerTCP

class Server(MastermindServerTCP):
    def __init__(self):
        MastermindServerTCP.__init__(self, 0.5, 0.5, 300.0)
        self.players = {} # all the Players() that exist in the world whether connected or not.
        self.localmaps = {} # the localmaps for each player.
        self.overmaps = {} # the dict of all overmaps by player.name
        #self.options = Options()
        self.calendar = Calendar(0, 0, 0, 0, 0, 0) # all zeros is the epoch
        # self.options.save()
        self.worldmap = Worldmap(26) # create this many chunks in x and y (z is always 1 (level 0) for genning the world. we will build off that for caverns and ant stuff and z level buildings.
        self.starting_locations = [Position(23, 23, 0)] #TODO: starting locations should be loaded dynamically from secenarios
        for i in range(1, 13):
            self.starting_locations.append(Position(23*i, 23, 0))
        self.RecipeManager = RecipeManager()
        self.ProfessionManager = ProfessionManager()
        self.MonsterManager = MonsterManager()
        self.ItemManager = self.worldmap.ItemManager
        self.FurnitureManager = self.worldmap.FurnitureManager

    def calculate_route(self, pos0, pos1, consider_impassable=True): # normally we will want to consider impassable terrain in movement calculations. creatures that don't can walk or break through walls.
        #print('----------------Calculating Route---------------------')
        #print('pos0: ' + str(pos0))
        #print('pos1: ' + str(pos1))
        reachable = [ pos0 ]
        explored = []

        while len(reachable) > 0:
            position = random.choice(reachable) # get a random reachable position #TODO: be a little more intelligent about picking the best reachable position.

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

            new_reachable = self.worldmap.get_adjacent_positions_non_impassable(position)
            for adjacent in new_reachable:
                if(abs(adjacent.x - pos0.x) > 10 or abs(adjacent.y - pos0.y) > 10):
                    continue
                if adjacent not in reachable and adjacent not in explored:
                    adjacent.previous = position # Remember how we got there.
                    reachable.append(adjacent)

        return None

    def handle_new_player(self, ident):
        self.players[ident] = Player(ident)
        # self.players[ident].profession = 'survivor'
        self.players[ident].position = random.choice(self.starting_locations)
        self.worldmap.put_object_at_position(self.players[ident], self.players[ident].position)
        self.localmaps[ident] = self.worldmap.get_chunks_near_position(self.players[ident].position)
        # give the player their starting items by referencing the ProfessionManager.
        # print('profession items ')
        '''
        ident : survivor
        _comment : A basic as it comes. I'll use this for the default profession.
        name : Survivor
        description : Some would say that there's nothing particularly notable about you. But you survived. That's more than most can say right now.
        skills : ["{'survival': 1}"]
        points : 0
        items : {'equipped': [{'TORSO': 'backpack'}], 'in_containers': [{'backpack': 'cell_phone'}]}
        flags : []
        CBMs : []
        '''
        #print(self.players[ident].profession)
        for key, value in self.ProfessionManager.PROFESSIONS[str(self.players[ident].profession)].items():
            print(key, ':', value)
        
            # print(value.items())
            # TODO: load the items into the player equipment slots as well as future things like CBMs and flags
            if(key == 'equipped_items'):
                for equip_location, item_ident in value.items():
                    print(equip_location, item_ident)
                    for bodypart in self.players[ident].body_parts:
                        if(bodypart.ident.split('_')[0] == equip_location):
                            if(bodypart.slot0 is None):
                                bodypart.slot0 = Item(item_ident, self.ItemManager.ITEM_TYPES[item_ident]) # need to pass the reference to load the item with data.
                                break
                            elif(bodypart.slot1 is None):
                                bodypart.slot1 =  Item(item_ident, self.ItemManager.ITEM_TYPES[item_ident]) # need to pass the reference to load the item with data.
                                break
                    else:
                        print('player needed an item but no free slots found')
            elif(key == 'items_in_containers'):
                for location_ident, item_ident in value.items():
                    print(location_ident, item_ident)

        print('New player joined.', self.players[ident])

    def callback_client_handle(self, connection_object, data):
        #print("Server: Recieved data \""+str(data)+"\" from client \""+str(connection_object.address)+"\".")
        # use the data to determine what player is giving the command and if they are logged in yet.

        if(isinstance(data, Command)): # the data we recieved was a command. process it.
            if(data.command == 'login'):
                if(data.args[0] == 'password'): # TODO: put an actual password system in.
                    print('password accepted for ' + str(data.ident))
                    if(not data.ident in self.players): # this player doesn't exist in the world yet.
                        # check and see if the players has logged in before.
                        tmp_player = self.worldmap.get_player(data.ident) # by 'name'
                        if(tmp_player is not None): # player exists
                            print('player exists. loading.')
                            self.players[data.ident] = tmp_player
                            self.players[data.ident].position = tmp_player.position
                            self.localmaps[data.ident] = self.worldmap.get_chunks_near_position(self.players[data.ident].position)
                        else: # new player
                           self.handle_new_player(data.ident)

                    print('Player ' + str(data.ident) + ' entered the world at position ' + str(self.players[data.ident].position))
                    self.callback_client_send(connection_object, self.players[data.ident])
                else:
                    print('password not accepted.')
                    connection_object.disconnect()

            if(data.command == 'request_player_update'):
                self.callback_client_send(connection_object, self.players[data.ident])

            if(data.command == 'request_localmap_update'):
                self.localmaps[data.ident] = self.worldmap.get_chunks_near_position(self.players[data.ident].position)
                self.callback_client_send(connection_object, self.localmaps[data.ident])

            # all the commands that are actions need to be put into the command_queue then we will loop through the queue each turn and process the actions.
            if(data.command == 'move'):
                self.players[data.ident].command_queue.append(Action(self.players[data.ident], 'move', [data.args[0]]))

            if(data.command == 'bash'):
                self.players[data.ident].command_queue.append(Action(self.players[data.ident], 'bash', [data.args[0]]))

            if(data.command == 'create_blueprint'): #  [result, direction])
                # args 0 is ident args 1 is direction.
                print('creating blueprint ' + str(data.args[0]) + ' for player ' + str(self.players[data.ident]))
                # blueprint rules
                # * there should be blueprints for terrain, furniture, items, and anything else that takes a slot up in the Worldmap.
                # * they act as placeholders and then 'transform' into the type they are once completed.
                # Blueprint(type, recipe)
                position_to_create_at = None
                if(data.args[1] == 'south'):
                    position_to_create_at = Position(self.players[data.ident].position.x, self.players[data.ident].position.y+1, self.players[data.ident].position.z)
                elif(data.args[1] == 'north'):
                    position_to_create_at = Position(self.players[data.ident].position.x, self.players[data.ident].position.y-1, self.players[data.ident].position.z)
                elif(data.args[1] == 'east'):
                    position_to_create_at = Position(self.players[data.ident].position.x+1, self.players[data.ident].position.y, self.players[data.ident].position.z)
                elif(data.args[1] == 'west'):
                    position_to_create_at = Position(self.players[data.ident].position.x-1, self.players[data.ident].position.y, self.players[data.ident].position.z)

                _recipe = server.RecipeManager.RECIPE_TYPES[data.args[0]]
                type_of = _recipe['type_of']
                bp_to_create = Blueprint(type_of, _recipe)

                self.worldmap.put_object_at_position(bp_to_create, position_to_create_at)

            if(data.command == 'calculated_move'):
                print('Recieved calculated_move action. let\'s build a path for ' + str(data.ident))

                _position = Position(data.args[0], data.args[1], data.args[2])
                _route = self.calculate_route(self.players[data.ident].position, _position) # returns a route from point 0 to point 1 as a series of Position(s)
                print(_route)
                # fill the queue with move commands to reach the tile.
                _x = self.players[data.ident].position.x
                _y = self.players[data.ident].position.y
                _z = self.players[data.ident].position.z
                action = None
                if(_route is None):
                    print('No _route possible.')
                    return
                for step in _route:
                    _next_x = step.x
                    _next_y = step.y
                    _next_z = step.z
                    if(_x > _next_x):
                        action = Action(self.players[data.ident], 'move', ['west'])
                    elif(_x < _next_x):
                        action = Action(self.players[data.ident], 'move', ['east'])
                    elif(_y > _next_y):
                        action = Action(self.players[data.ident], 'move', ['north'])
                    elif(_y < _next_y):
                        action = Action(self.players[data.ident], 'move', ['south'])
                    elif(_z < _next_z):
                        action = Action(self.players[data.ident], 'move', ['up'])
                    elif(_z > _next_z):
                        action = Action(self.players[data.ident], 'move', ['down'])
                    self.players[data.ident].command_queue.append(action)
                    # pretend as if we are in the next position.
                    _x = _next_x
                    _y = _next_y
                    _z = _next_z

            if(data.command == 'move_item_to_player_storage'): # when the player clicked on a ground item.
                print('RECIEVED: move_item_to_player_storage', str(data))
                _player = self.players[data.ident]
                _from_pos = Position(data.args[0], data.args[1], data.args[2])
                _item_ident = data.args[3]
                _from_item = None
                _open_containers = []
                print(_player, _from_pos, _item_ident)
                # find the item that the player is requesting.
                for item in self.worldmap.get_tile_by_position(_from_pos)['items']:
                    if(item.ident == _item_ident):
                        # this is the item or at least the first one that matches the same ident.
                        _from_item = item  # save a reference to it to use.
                        break

                if(_from_item == None): # we didn't find one, player sent bad information (possible hack?)
                    print('_from_item not found. this is unusual.')
                    return

                # make a list of open_containers the player has to see if they can pick it up.
                for bodyPart in _player.body_parts:
                    if(bodyPart.slot0 is not None and isinstance(bodyPart.slot0, Container) and bodyPart.slot0.opened == 'yes'):
                        _open_containers.append(bodyPart.slot0)
                    if(bodyPart.slot1 is not None and isinstance(bodyPart.slot1, Container) and bodyPart.slot1.opened == 'yes'):
                        _open_containers.append(bodyPart.slot1)

                if(len(_open_containers) <= 0):
                    print('no open containers found.')
                    return # no open containers.

                # check if the player can carry that item.
                for container in _open_containers:
                    # then find a spot for it to go (open_containers)
                    if(container.add_item(item)): # if it added it sucessfully.
                        print('added item correctly. trying to remove it from the world.')
                        # remove it from the world.
                        for item in self.worldmap.get_tile_by_position(_from_pos)['items'][:]: # iterate a copy to remove properly.
                            if(item.ident == _item_ident):
                                self.worldmap.get_tile_by_position(_from_pos)['items'].remove(item)
                                print('removed item from the world successfully.')
                                break
                        return
                    else:
                        print('could not add item to player inventory.')
                    ### then send the player the updated version of themselves so they can refresh.
            #end move_item_to_player_storage

            if(data.command == 'move_item'):
                # client sends 'hey server. can you move this item from this to that?'
                _player_requesting = self.players[data.ident]
                _item = data.args[0] # the item we are moving.
                _from_type = data.args[1] # creature.held_item, creature.held_item.container, bodypart.equipped, bodypart.equipped.container, position, blueprint
                _from_list = [] # the object list that contains the item. parse the type and fill this properly.
                _to_list = data.args[2] # the list the item will end up. passed from command.
                _position = Position(data.args[3], data.args[4], data.args[5]) # pass the position even if we may not need it.

                # need to parse where it's coming from and where it's going.
                if(_from_type == 'bodypart.equipped'):
                    for bodypart in _player_requesting.body_parts[:]: # iterate a copy to remove properly.
                        if(_item in bodypart.equipped):
                            _from_list = bodypart.equipped
                            _from_list.remove(_item)
                            _to_list.append(_item)
                            print('moved correctly.')
                            return
                elif(_from_type == 'bodypart.equipped.container'):
                    for bodypart in _player_requesting.body_parts[:]: # iterate a copy to remove properly.
                        for item in bodypart.equipped: #could be a container or not.
                            if(isinstance(item, Container)): # if it's a container.
                                for item2 in item.contained_items[:]: # check every item in the container.
                                    if(item2 is _item):
                                        _from_list = item.contained_items
                                        _from_list.remove(_item)
                                        _to_list.append(_item)
                                        print('moved correctly.')
                                        return
                elif(_from_type == 'position'):
                    _from_list = self.worldmap.get_tile_by_position(_position)['items']
                    if(_item in _from_list):
                        _from_list.remove(_item)
                        _to_list.append(_item)
                        print('moved correctly.')
                        return
                elif(_from_type == 'blueprint'): # a blueprint is a type of container but can't be moved from it's world position.
                    for item in self.worldmap.get_tile_by_position(_position)['items']:
                        if(isinstance(item) == Blueprint): # only one blueprint allowed per space.
                            _from_list = item.contained_items
                            _from_list.remove(_item)
                            _to_list.append(_item)
                            print('moved correctly.')
                            return


                ### possible move types ###
                # creature(held) to creature(held) (give to another player)
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


        return super(Server,self).callback_client_handle(connection_object,data)

    def callback_client_send(self, connection_object, data, compression=None):
        #print("Server: Sending data \""+str(data)+"\" to client \""+str(connection_object.address)+"\" with compression \""+str(compression)+"\"!")
        return super(Server, self).callback_client_send(connection_object, data, compression)

    def callback_connect_client(self, connection_object):
        print("Server: Client from \""+str(connection_object.address)+"\" connected.")
        return super(Server, self).callback_connect_client(connection_object)

    def callback_disconnect_client(self, connection_object):
        print("Server: Client from \""+str(connection_object.address)+"\" disconnected.")
        return super(Server, self).callback_disconnect_client(connection_object)

    def process_creature_command_queue(self, creature):
        actions_to_take = creature.actions_per_turn
        for action in creature.command_queue[:]: # iterate a copy so we can remove on the fly.
            if(actions_to_take == 0):
                return # this creature is out of action points.

            if(creature.next_action_available > 0): # this creature can't act until x turns from now.
                creature.next_action_available = creature.next_action_available - 1
                return

            # if we get here we can process a single action
            if(action.action_type == 'move'):
                actions_to_take = actions_to_take - 1 # moving costs 1 ap.
                if(action.args[0] == 'south'):
                    if(self.worldmap.move_object_from_position_to_position(self.players[creature.name], self.players[creature.name].position, Position(self.players[creature.name].position.x, self.players[creature.name].position.y+1, self.players[creature.name].position.z))):
                        self.players[creature.name].position = Position(self.players[creature.name].position.x, self.players[creature.name].position.y+1, self.players[creature.name].position.z)
                    creature.command_queue.remove(action) # remove the action after we process it.
                if(action.args[0] == 'north'):
                    if(self.worldmap.move_object_from_position_to_position(self.players[creature.name], self.players[creature.name].position, Position(self.players[creature.name].position.x, self.players[creature.name].position.y-1, self.players[creature.name].position.z))):
                        self.players[creature.name].position = Position(self.players[creature.name].position.x, self.players[creature.name].position.y-1, self.players[creature.name].position.z)
                    creature.command_queue.remove(action) # remove the action after we process it.
                if(action.args[0] == 'east'):
                    if(self.worldmap.move_object_from_position_to_position(self.players[creature.name], self.players[creature.name].position, Position(self.players[creature.name].position.x+1, self.players[creature.name].position.y, self.players[creature.name].position.z))):
                        self.players[creature.name].position = Position(self.players[creature.name].position.x+1, self.players[creature.name].position.y, self.players[creature.name].position.z)
                    creature.command_queue.remove(action) # remove the action after we process it.
                if(action.args[0] == 'west'):
                    if(self.worldmap.move_object_from_position_to_position(self.players[creature.name], self.players[creature.name].position, Position(self.players[creature.name].position.x-1, self.players[creature.name].position.y, self.players[creature.name].position.z))):
                        self.players[creature.name].position = Position(self.players[creature.name].position.x-1, self.players[creature.name].position.y, self.players[creature.name].position.z)
                    creature.command_queue.remove(action) # remove the action after we process it.
                if(action.args[0] == 'up'):
                    if(self.worldmap.move_object_from_position_to_position(self.players[creature.name], self.players[creature.name].position, Position(self.players[creature.name].position.x, self.players[creature.name].position.y, self.players[creature.name].position.z+1))):
                        self.players[creature.name].position = Position(self.players[creature.name].position.x, self.players[creature.name].position.y, self.players[creature.name].position.z+1)
                    creature.command_queue.remove(action) # remove the action after we process it.
                if(action.args[0] == 'down'):
                    if(self.worldmap.move_object_from_position_to_position(self.players[creature.name], self.players[creature.name].position, Position(self.players[creature.name].position.x, self.players[creature.name].position.y, self.players[creature.name].position.z-1))):
                        self.players[creature.name].position = Position(self.players[creature.name].position.x, self.players[creature.name].position.y, self.players[creature.name].position.z-1)
                    creature.command_queue.remove(action) # remove the action after we process it.
            elif(action.action_type == 'bash'):
                actions_to_take = actions_to_take - 1 # bashing costs 1 ap.
                if(action.args[0] == 'south'):
                    self.worldmap.bash(self.players[creature.name], Position(self.players[creature.name].position.x, self.players[creature.name].position.y+1, self.players[creature.name].position.z))
                    self.localmaps[creature.name] = self.worldmap.get_chunks_near_position(self.players[creature.name].position)
                    creature.command_queue.remove(action) # remove the action after we process it.
                if(action.args[0] == 'north'):
                    self.worldmap.bash(self.players[creature.name], Position(self.players[creature.name].position.x, self.players[creature.name].position.y-1, self.players[creature.name].position.z))
                    self.localmaps[creature.name] = self.worldmap.get_chunks_near_position(self.players[creature.name].position)
                    creature.command_queue.remove(action) # remove the action after we process it.
                if(action.args[0] == 'east'):
                    self.worldmap.bash(self.players[creature.name], Position(self.players[creature.name].position.x+1, self.players[creature.name].position.y, self.players[creature.name].position.z))
                    self.localmaps[creature.name] = self.worldmap.get_chunks_near_position(self.players[creature.name].position)
                    creature.command_queue.remove(action) # remove the action after we process it.
                if(action.args[0] == 'west'):
                    self.worldmap.bash(self.players[creature.name], Position(self.players[creature.name].position.x-1, self.players[creature.name].position.y, self.players[creature.name].position.z))
                    self.localmaps[creature.name] = self.worldmap.get_chunks_near_position(self.players[creature.name].position)
                    creature.command_queue.remove(action) # remove the action after we process it.

    # this function handles overseeing all creature movement, attacks, and interactions
    def compute_turn(self):
        for player, chunks in self.localmaps.items():
            for chunk in chunks: # players typically get 9 chunks
                for tile in chunk.tiles:
                    tile['lumens'] = 0 # reset light levels.

        creatures_to_process = [] # we want a list that contains all the non-duplicate creatures on all localmaps around players.
        for player, chunks in self.localmaps.items():
            for chunk in chunks: # players typically get 9 chunks
                for tile in chunk.tiles:
                    if(tile['creature'] is not None and tile['creature'] not in creatures_to_process): # avoid duplicates
                        creatures_to_process.append(tile['creature'])



        for creature in creatures_to_process:
            if(len(creature.command_queue) > 0):
                print('doing actions for: ' + str(creature.name))
                self.process_creature_command_queue(creature)


        for tile in self.worldmap.get_all_tiles():
            if(tile['creature'] is not None):
                #TODO: don't just draw a light around every creature. we need to check for all lights. We also need to have light blocked by walls.
                for tile, distance in self.worldmap.get_tiles_near_position(tile['position'], 8):
                    tile['lumens'] = tile['lumens'] + int(8-distance)

        # now that we've processed what everything wants to do we can return.

    def generate_and_apply_city_layout(self, city_size):
        #city_size = 1
        city_layout = self.worldmap.generate_city(city_size)
        # for every 1 city size it's 12 tiles across and high
        for j in range(city_size*12):
            for i in range(city_size*12):
                if(server.worldmap.get_chunk_by_position(Position(i * server.worldmap.chunk_size + 1 , j * server.worldmap.chunk_size + 1, 0)).was_loaded == 'no'):
                    if(city_layout[i][j] == 'r'):
                        json_file = random.choice(os.listdir('./data/json/mapgen/residential/'))

                        server.worldmap.build_json_building_at_position('./data/json/mapgen/residential/' + json_file, Position(i * server.worldmap.chunk_size + 1 , j * server.worldmap.chunk_size + 1, 0))
                    elif(city_layout[i][j] == 'c'):
                        json_file = random.choice(os.listdir('./data/json/mapgen/commercial/'))
                        server.worldmap.build_json_building_at_position('./data/json/mapgen/commercial/' + json_file, Position(i * server.worldmap.chunk_size + 1 , j * server.worldmap.chunk_size + 1, 0))
                    elif(city_layout[i][j] == 'i'):
                        json_file = random.choice(os.listdir('./data/json/mapgen/industrial/'))
                        server.worldmap.build_json_building_at_position('./data/json/mapgen/industrial/' + json_file, Position(i * server.worldmap.chunk_size + 1 , j * server.worldmap.chunk_size + 1, 0))
                    elif(city_layout[i][j] == 'R'): # complex enough to choose the right rotation.
                        attached_roads = 0
                        try:
                            if(city_layout[int(i-1)][int(j)] == 'R'):
                                attached_roads = attached_roads + 1
                            if(city_layout[int(i+1)][int(j)] == 'R'):
                                attached_roads = attached_roads + 1
                            if(city_layout[int(i)][int(j-1)] == 'R'):
                                attached_roads = attached_roads + 1
                            if(city_layout[int(i)][int(j+1)] == 'R'):
                                attached_roads = attached_roads + 1
                            if(attached_roads == 4):
                                json_file = './data/json/mapgen/road/city_road_4_way.json'
                            elif(attached_roads == 3): #TODO: make sure the roads line up right.
                                if(city_layout[int(i+1)][int(j)] != 'R'):
                                    json_file = './data/json/mapgen/road/city_road_3_way_s0.json'
                                elif(city_layout[int(i-1)][int(j)] != 'R'):
                                    json_file = './data/json/mapgen/road/city_road_3_way_p0.json'
                                elif(city_layout[int(i)][int(j+1)] != 'R'):
                                    json_file = './data/json/mapgen/road/city_road_3_way_u0.json'
                                elif(city_layout[int(i)][int(j-1)] != 'R'):
                                    json_file = './data/json/mapgen/road/city_road_3_way_d0.json'
                            elif(attached_roads <= 2):
                                if(city_layout[int(i+1)][int(j)] == 'R'):
                                    json_file = './data/json/mapgen/road/city_road_h.json'
                                elif(city_layout[int(i-1)][int(j)] == 'R'):
                                    json_file = './data/json/mapgen/road/city_road_h.json'
                                elif(city_layout[int(i)][int(j+1)] == 'R'):
                                    json_file = './data/json/mapgen/road/city_road_v.json'
                                elif(city_layout[int(i)][int(j-1)] == 'R'):
                                    json_file = './data/json/mapgen/road/city_road_v.json'
                            server.worldmap.build_json_building_at_position(json_file, Position(i * server.worldmap.chunk_size + 1 , j * server.worldmap.chunk_size + 1, 0))
                        except:
                            #TODO: fix this blatant hack to account for coordinates outside the city layout.
                            pass

# do this if the server was started up directly.
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Cataclysm LD Server')
    parser.add_argument('--host', metavar='Host', help='Server host', default='0.0.0.0')
    parser.add_argument('-p', '--port', metavar='Port', type=int, help='Server port', default=6317)

    args = parser.parse_args()
    ip = args.host
    port = args.port

    server = Server()
    server.connect(ip, port)
    server.accepting_allow()

    dont_break = True
    time_offset = 1.0 # 0.5 is twice as fast, 2.0 is twice as slow
    last_turn_time = time.time()
    server.generate_and_apply_city_layout(2)

    print('Started up Cataclysm: Looming Darkness Server.')
    while dont_break:
        try:
            while(time.time() - last_turn_time < time_offset): # try to keep up with the time offset but never go faster than it.
                time.sleep(.001)
            server.calendar.advance_time_by_x_seconds(1) # a turn is one second.
            server.compute_turn() # where all queued creature actions get taken care of, as well as physics engine stuff.
            print('turn: ' + str(server.calendar.get_turn()))
            server.worldmap.update_chunks_on_disk() # if the worldmap in memory changed update it on the hard drive.
            #TODO: unload from memory chunks that have no updates required. (such as no monsters, players, or fires)
            last_turn_time = time.time() # based off of system clock.
        except KeyboardInterrupt:
            print('cleaning up before exiting.')
            server.accepting_disallow()
            server.disconnect_clients()
            server.disconnect()
            server.worldmap.update_chunks_on_disk() # if the worldmap in memory changed update it on the hard drive.
            dont_break = False
            print('done cleaning up.')
        except Exception as e:
            print('!! Emergency Exit due to Server Exception. !!')
            print(e)
            print()
            server.accepting_disallow()
            server.disconnect_clients()
            server.disconnect()
            server.worldmap.update_chunks_on_disk() # if the worldmap in memory changed update it on the hard drive.
            dont_break = False
            sys.exit()
