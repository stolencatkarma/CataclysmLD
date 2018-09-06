import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict

import pygame
import pygame.locals

from Mastermind._mm_client import MastermindClientTCP
from src.action import Action
from src.blueprint import Blueprint
from src.command import Command
from src.item import Item, ItemManager
from src.messagebox import MessageBox
from src.player import Player
from src.position import Position
from src.recipe import Recipe, RecipeManager
from src.tileManager import TileManager
from src.user_interface import (Button, Crafting_Menu, Directional_choice,
                                Equipment_Button, Equipment_Open_Container_Button, Equipment_Menu, FontManager,
                                Hotbar, ListBox, Listbox_item, Movement_menu,
                                Popup_menu, Super_menu, TextBox)
from src.worldmap import Worldmap


class Client(MastermindClientTCP): # extends MastermindClientTCP
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
            #print(list_of_chunks)
            for tile in chunk.tiles:
                tiles.insert(len(tiles), tile)
        #print('length of returned localmap: ' + str(len(tiles)))
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
        #print('origin_position: ' + str(origin_position))
        # origin_position = origin_position # store the player position for fov origin
        # convert chunks to grid
        level = defaultdict(dict)
        #light_map = defaultdict(dict)
        for tile in self.localmap[:]: # we only need the tiles around radius.
            if int(tile['position'].x) < origin_position.x-radius or int(tile['position'].x) > origin_position.x+radius+1:
                self.localmap.remove(tile)
            elif int(tile['position'].y) < origin_position.y-radius or int(tile['position'].y) > origin_position.y+radius+1:
                self.localmap.remove(tile)
            else:
                level[str(tile['position'].x)][str(tile['position'].y)] = tile['terrain'].impassable # so either remove a tile or figure out if it's impassable.
                #light_map = [str(tile['position'].x)][str(tile['position'].y)] = tile['lumens']
        # draw a line to each edge of the viewport using grid_edges
        #x's include top row and bottom rows
        #y's include min and max of viewport.
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
        #now we need to remove tiles which are out of our field of view.
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
        #print('len of new localmap:' + str(len(self.localmap)))

    def draw_view_at_position(self, draw_position):
        #TODO: lerp the positions of creatures from one frame to the next.
        self.screen.fill((55, 55, 55)) # clear screen between frames
        self.trim_localmap(draw_position) # update field of view and lighting

        # at this point the localmap should've been trimmed of unseeable tiles. draw what's left at position.
        for tile in self.localmap: # draw the localmap for the controlling player.
            terrain = tile['terrain']
            position = tile['position'] # Position(x, y, z)
            creature = tile['creature'] # Creature()
            furniture = tile['furniture'] # Furniture()
            items = tile['items'] # list [] of Item()
            light_intensity = tile['lumens']
            #print(terrain.ident)
            fg = self.TileManager.TILE_TYPES[terrain.ident]['fg']
            bg = self.TileManager.TILE_TYPES[terrain.ident]['bg']

            x = draw_position.x - position.x - 9 # offset to put position in middle of viewport
            y = draw_position.y - position.y - 9 # offset to put position in middle of viewport

            x = x * -1 # x needs to be flipped to display to make 0,0 top left (maps are loaded row, column top to bottom)
            y = y * -1 # y needs to be flipped to display correctly.

            # first blit terrain
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

                    # only display the first item for now
                    fg = self.TileManager.TILE_TYPES[items[0].ident]['fg']
                    self.screen.blit(self.TileManager.TILE_MAP[fg], (x*24, y*24))

            # then blit vehicles

            # then blit player and creatures and monsters (all creature types)
            if(creature is not None):
                self.screen.blit(self.TileManager.TILE_MAP[creature.tile_id], (x*24, y*24)) # TODO: need to build it if the player is wearing clothes, etc...

            # darken based on lumen level of the tile
            # light_intensity # 10 is max light level although lumen level may be higher.
            light_intensity = min(int((255-(light_intensity*25))/3), 255)
            light_intensity = max(light_intensity, 0)
            #print(light_intensity, end=',')
            self.screen.fill((light_intensity, light_intensity, light_intensity), rect=(x*24, y*24, 24, 24), special_flags=pygame.BLEND_SUB)

            # render debug text
            '''
            myfont = pygame.font.SysFont("monospace", 8)
            label1 = myfont.render(str(position.x), 1, (255,255,0))
            label2 = myfont.render(str(position.y), 1, (255,255,0))
            self.screen.blit(label1, (x*24, y*24))
            self.screen.blit(label2, (x*24, y*24+8))
            '''

            # then blit weather. Weather is the only thing above players and creatures.
            #TODO: blit weather

        for hotbar in self.hotbars: #draw the hotbars
            hotbar.draw()

        for button in self.buttons: #draw the buttons
            button.draw()

        for listbox in self.listboxes: #draw the listboxes
            listbox.draw()

        for textbox in self.textboxes: #draw the textboxes
            textbox.draw()

    def __init__(self, first_name, last_name):
        MastermindClientTCP.__init__(self)
        pygame.init()
        pygame.display.set_caption('Cataclysm: Looming Darkness')
        self.screen = pygame.display.set_mode((854, 480), pygame.ANYFORMAT)
        self.TileManager = TileManager()
        self.ItemManager = ItemManager()
        self.RecipeManager = RecipeManager() # contains all the known recipes in the game. for reference.
        self.FontManager = FontManager()
        self.player = Player(str(first_name) + str(last_name)) # recieves updates from server. the player and all it's stats. #TODO: name and password.
        self.localmap = None
        self.hotbars = []
        self.hotbars.insert(0, Hotbar(self.screen, 10, 10))


        # insert buttons when we open a screen and destroy them when we leave it.
        self.buttons = []
        #self.buttons.insert(0, Button(self.screen, 'BUTTON!', (120,120,120), (50,50,50,50)))
        #self.buttons.insert(0, Button(self.screen, 'BUTTON!', (120,120,120), (150,50,50,50)))
        #self.buttons.insert(0, Button(self.screen, 'BUTTON!', (120,120,120), (150,150,50,50)))
        #self.buttons.insert(0, Button(self.screen, 'BUTTON!', (120,120,120), (50,150,50,50)))
        self.textboxes = []
        self.listboxes = []
        #self.listboxes.insert(0, ListBox(self.screen, (0,0,0), (160, 50, 200,200)))
        #self.listboxes[0].add(Listbox_item('item 0', Item('brewing_cookbook')))
        #self.listboxes[0].add(Listbox_item('item 1', Item('brewing_cookbook')))
        #self.listboxes[0].add(Listbox_item('item 2', Item('brewing_cookbook')))
        #self.listboxes[0].add(Listbox_item('item 3', Item('brewing_cookbook')))
        #self.listboxes[0].add(Listbox_item('item 4', Item('brewing_cookbook')))
        #self.listboxes[0].add(Listbox_item('item 5', Item('brewing_cookbook')))
        #self.listboxes[0].add(Listbox_item('item 6', Item('brewing_cookbook')))
        #self.listboxes[0].add(Listbox_item('item 7', Item('brewing_cookbook')))

        self.messageBox = MessageBox(self.screen)

    def open_crafting_menu(self):
        #TODO: allow passing a string to skip to the choose direction part.
        list_of_known_recipes = []
        for key, value in self.RecipeManager.RECIPE_TYPES.items(): #TODO: Don't just add them all. Pull them from creature.known_recipes
            list_of_known_recipes.append(value)
        #print(list_of_known_recipes)
        crafting_menu = Crafting_Menu(self.screen, list_of_known_recipes, (0, 0, 854, 480), self.FontManager)
        self.screen.fill((55, 55, 55), special_flags=pygame.BLEND_SUB) # darken the screen to indicate an action is required.

        # work out the internal list of UI_components so we can iterate them if needed.
        _listboxes = []
        _textboxes = []
        _buttons = []
        for UI_component in crafting_menu.UI_components:
            UI_component.draw() # blit them to the screen.

            if(isinstance(UI_component, ListBox)):
                _listboxes.append(UI_component)
            elif(isinstance(UI_component, TextBox)):
                _textboxes.append(UI_component)
            elif(isinstance(UI_component, Button)):
                _buttons.append(UI_component)

        # now that we've drawn the crafting menu we need to wait until the player clicks a UI_component or clicks to craft.
        pygame.event.clear() # clear the event queue so we can wait for player feedback.
        sidebar_components = []
        while True:
            for UI_component in crafting_menu.UI_components:
                UI_component.draw() # blit them to the screen.
            for component in sidebar_components:
                component.draw()
            pygame.display.flip() # flip the screen after we've .draw() the UI_components
            event = pygame.event.wait() # wait for player input.
            if event.type == pygame.QUIT:
                client.disconnect()
                pygame.quit()
                sys.exit()
            elif(event.type == pygame.MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                for button in _buttons:
                    if pos[0] >= button.x and pos[0] <= button.x + button.width:
                        if pos[1] >= button.y and pos[1] <= button.y + button.height:
                            button.on_clicked(event.button, pos[0] - button.x, pos[1] - button.y)
                            print(button.command)
                            if(button.command == 'craft'):
                                # close the crafting window and bring up a directional window

                                # if player clicked the craft button then we need to close the menu and get a direction.
                                # open up the directional menu and wait for a input
                                w = int(client.screen.get_width()/2)
                                h = int(client.screen.get_height()/2)
                                directional_menu = Directional_choice(client.screen, (w, h)) # draw it at center of screen.
                                pygame.event.clear()
                                while True:
                                    client.screen.blit(directional_menu.surface, (100,100))
                                    pygame.display.flip() # now we have a fully built frame, display it
                                    event = pygame.event.wait()
                                    if event.type == pygame.KEYUP:
                                        #print(event.key)
                                        if event.key == pygame.K_KP2:
                                            return crafting_menu.sidebar['result'], 'south'
                                        if event.key == pygame.K_KP8:
                                            return crafting_menu.sidebar['result'], 'north'
                                        if event.key == pygame.K_KP4:
                                            return crafting_menu.sidebar['result'], 'west'
                                        if event.key == pygame.K_KP6:
                                            return crafting_menu.sidebar['result'], 'east'

                            elif(button.command.split('_')[0] == 'skill'):
                                # TODO: a skill button was pressed. handle it.
                                # load button.command.split('_')[1]
                                pass

                for listbox in _listboxes:
                    if pos[0] >= listbox.x and pos[0] <= listbox.x + listbox.width:
                        if pos[1] >= listbox.y and pos[1] <= listbox.y + listbox.height:
                            item_clicked = listbox.on_clicked(event.button, pos[0] - listbox.x, pos[1] - listbox.y)
                            # fill the Sidebar with the relavent info when we click a listbox item
                            crafting_menu.sidebar = {} # reset the sidebar.
                            for key, value in item_clicked.reference_object.items():
                                crafting_menu.sidebar[key] = value

                sidebar_components = []
                count = 1 # start after the main textbox.
                w = int(client.screen.get_width())
                h = int(client.screen.get_height())
                print('---------------------------------------------')
                for key, value in crafting_menu.sidebar.items():
                    print(value)
                    if(key == 'components'):
                        #_surface = self.FontManager.convert_string_to_surface(str(key))
                        #sidebar_components.append(TextBox(self.screen, (0,0,200), (w-288, 72+(count*12), w, h-72), _surface))
                        count = count + 1
                        for dict_or_list in value:
                            if(type(dict_or_list) == list): # this is a OR list of components
                                for item in dict_or_list:
                                    _surface = self.FontManager.convert_string_to_surface(str(item['amount']))
                                    sidebar_components.append(TextBox(self.screen, (0,0,200), (w-268, 72+(count*12), w, 8), _surface))
                                    _surface = self.FontManager.convert_string_to_surface(str(item['ident'])+str('    OR'))
                                    sidebar_components.append(TextBox(self.screen, (0,0,200), (w-248, 72+(count*12), w, 8), _surface))
                                    count = count + 1
                            else:
                                _surface = self.FontManager.convert_string_to_surface(str(dict_or_list['amount']))
                                sidebar_components.append(TextBox(self.screen, (0,0,200), (w-268, 72+(count*12), w, 8), _surface))
                                _surface = self.FontManager.convert_string_to_surface(str(dict_or_list['ident'])+str('    AND'))
                                sidebar_components.append(TextBox(self.screen, (0,0,200), (w-248, 72+(count*12), w, 8), _surface))
                                count = count + 1

                    else:
                        _surface = self.FontManager.convert_string_to_surface(str(key))
                        sidebar_components.append(TextBox(self.screen, (0,0,200), (w-288, 72+(count*12), w, 8), _surface))
                        _surface = self.FontManager.convert_string_to_surface(str(value))
                        sidebar_components.append(TextBox(self.screen, (0,0,200), (w-168, 72+(count*12), w, 8), _surface))
                        count = count + 1 #crafting menu takes up the whole screen, don't need pos unless that changes.

    def open_movement_menu(self, pos, tile):
        print(pos)
        movement_menu = Movement_menu(client.screen, (pos[0], pos[1], 72, 144), client.FontManager)

        pygame.event.clear() # clear the event queue so we can wait for player feedback.
        _listboxes = []
        _textboxes = []
        _buttons = []

        for UI_component in movement_menu.UI_components:
            UI_component.draw() # blit them to the screen.

            if(isinstance(UI_component, ListBox)):
                _listboxes.append(UI_component)
            elif(isinstance(UI_component, TextBox)):
                _textboxes.append(UI_component)
            elif(isinstance(UI_component, Button)):
                _buttons.append(UI_component)

        print('len of _listboxes', end = ': ')
        print(str(len(_listboxes)))

        print('opening movement menu')
        pygame.event.clear() # clear the event queue so we can wait for player feedback.
        clicked = ''
        while clicked == '':
            for UI_component in movement_menu.UI_components:
                UI_component.draw() # blit them to the screen.

            pygame.display.flip() # flip the screen after we've .draw() the UI_components
            event = pygame.event.wait() # wait for player input.
            if event.type == pygame.QUIT:
                client.disconnect()
                pygame.quit()
                sys.exit()
            elif(event.type == pygame.MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                for listbox in _listboxes:
                    if pos[0] >= listbox.x and pos[0] <= listbox.x + listbox.width:
                        if pos[1] >= listbox.y and pos[1] <= listbox.y + listbox.height:
                            item_clicked = listbox.on_clicked(event.button, pos[0] - listbox.x, pos[1] - listbox.y)
                            if(item_clicked == None):
                                pass
                            else:
                                print('movement_menu selected: ' + str(item_clicked.text))
                                clicked = item_clicked.text

        if(clicked == 'move'):
            print('clicked move. sending command')
            _command = Command(client.player.name, 'calculated_move', (tile['position'].x, tile['position'].y, tile['position'].z)) # send calculated_move action to server and give it the position of the tile we clicked.
            return _command

    def open_super_menu(self, pos, tile):
        print(pos)
        super_menu = Super_menu(client.screen, tile, (pos[0], pos[1], 72, 144), client.FontManager) # initialize it.
        self.screen.fill((55, 55, 55), special_flags=pygame.BLEND_SUB) # darken the screen to indicate an action is required.
        pygame.event.clear() # clear the event queue so we can wait for player feedback.
        _listboxes = []
        _textboxes = []
        _buttons = []
        for UI_component in super_menu.UI_components:
            UI_component.draw() # blit them to the screen.

            if(isinstance(UI_component, ListBox)):
                _listboxes.append(UI_component)
            elif(isinstance(UI_component, TextBox)):
                _textboxes.append(UI_component)
            elif(isinstance(UI_component, Button)):
                _buttons.append(UI_component)

        clicked = ''
        while clicked == '':
            pygame.display.flip() # flip the screen after we've .draw() the UI_components
            event = pygame.event.wait() # wait for player input.
            if event.type == pygame.QUIT:
                client.disconnect()
                pygame.quit()
                sys.exit()
            elif(event.type == pygame.MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                for listbox in _listboxes:
                    if pos[0] >= listbox.x and pos[0] <= listbox.x + listbox.width:
                        if pos[1] >= listbox.y and pos[1] <= listbox.y + listbox.height:
                            item_clicked = listbox.on_clicked(event.button, pos[0] - listbox.x, pos[1] - listbox.y)
                            if(item_clicked == None):
                                #user clicked an empty spot.
                                pass
                            else:
                                print(str(item_clicked.text))
                                clicked = item_clicked.text

        #print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        if clicked == 'Movement':
            return client.open_movement_menu(pos, tile) # pass back the results of the movement window. returned as command 'calculated_move'
        elif clicked == 'Terrain':
            return client.open_terrain_menu(pos)
        elif clicked == 'Creature':
            pass
        elif clicked == 'Items':
            # TODO: I assume the player wants to look at the items to decide what to take.
            return client.open_items_on_ground(pos, tile)

    def open_equipment_menu(self):
        self.screen.fill((55, 55, 55), special_flags=pygame.BLEND_SUB) # darken the screen to indicate an action is required.
        equipment_menu = Equipment_Menu(self.screen, (0, 0, 400, 496), self.FontManager, self.TileManager, self.player.body_parts)

        # work out the internal list of UI_components so we can iterate them if needed.
        _listboxes = []
        _textboxes = []
        _buttons = []
        _equipment_buttons = []
        for UI_component in equipment_menu.UI_components:
            UI_component.draw() # blit them to the screen.

            if(isinstance(UI_component, ListBox)):
                _listboxes.append(UI_component)
            elif(isinstance(UI_component, TextBox)):
                _textboxes.append(UI_component)
            elif(isinstance(UI_component, Button)):
                _buttons.append(UI_component)
            elif(isinstance(UI_component, Equipment_Button)):
                _equipment_buttons.append(UI_component)
            elif(isinstance(UI_component, Equipment_Open_Container_Button)):
                _equipment_buttons.append(UI_component)

        # clicking on a area where an item is equipped.
        #  with no item 'grabbed' and no item in slot.
        #   open menu > equip/wear item -> parse_items_for_equippable_locations()[] -> click_item() -> wear_item()
        # with item 'grabbed' and no item in slot
        #  check_equippable() -> wear/weild item
        # with no item 'grabbed' and item in slot
        #  'grab' item
        # with item grabbed and item in slot
        #  swap()?
        # with item 'grabbed' and cursor outside equipment screen.
        #  drop() item on ground relative the the position of the equipment screen (drop right on screen drops right of player)
        # click a container with an item 'grabbed'
        #  put() item in container. (containers can only hold empty containers. or closed containers.)

        # now that we've drawn the equipment menu we need to wait until the player clicks a UI_component.
        pygame.event.clear() # clear the event queue so we can wait for player feedback.
        _grabbed = self.player.grabbed
        while True:
            self.screen.blit(equipment_menu.surface, (equipment_menu.x, equipment_menu.y))
            for UI_component in equipment_menu.UI_components:
                UI_component.draw() # blit them to the screen.
            pygame.display.flip() # flip the screen after we've .draw() the UI_components
            event = pygame.event.wait() # wait for player input.
            #TODO: drag the grabbed item with the mouse. right now it shows nothing.
            if event.type == pygame.QUIT:
                client.disconnect()
                pygame.quit()
                sys.exit()
            elif(event.type == pygame.MOUSEBUTTONDOWN):
                # dragging from somwhere. we need to keep drawing so handle that
                # wait until we let go of the mouse and handle it.
                pass
            elif(event.type == pygame.MOUSEBUTTONUP):
                # we clicked somewhere while the equipment screen is up.
                # if we clicked an equipment tile we need to open a sub-menu for options for that the item can do. (activate, equip, etc..)
                pos = pygame.mouse.get_pos()
                for UI_component in equipment_menu.UI_components:
                    if pos[0] >= UI_component.position[0] and pos[0] <= UI_component.position[0] + 24:
                        if pos[1] >= UI_component.position[1] and pos[1] <= UI_component.position[1] + 24:
                            print('clicked', UI_component )
                            if(_grabbed is None): # the temporary spot where the cursor is holding the item.
                                _grabbed = UI_component.item
                                UI_component.item = None # this only happens locally for now. The server doesn't care about the item on the cursor.
                            else: # we are holding an item
                                if(UI_component.item is None):
                                    UI_component.item = _grabbed
                                    _grabbed = None # place the item into the blank spot.
                                    #TODO: tell the server to move the item server-side
                                else:

                                    _tmp1 = UI_component.item # swap the items.
                                    _tmp2 = _grabbed
                                    UI_component.item = _tmp2
                                    _grabbed = _tmp1
                                    _tmp1 = None
                                    _tmp2 = None

                                    #_grabbed = _tmp1
                                    #TODO: tell the server to swap the items server-side
                                    '''
                                    _player_requesting = self.players[data.ident]
                                    _item = data.args[0] # the item we are moving.
                                    _from_type = data.args[1] # creature.held_item, creature.held_item.container, bodypart.equipped, bodypart.equipped.container, position, blueprint
                                    _from_list = [] # the object list that contains the item. parse the type and fill this properly.
                                    _to_list = data.args[2] # the list the item will end up. passed from command.
                                    _position = Position(data.args[3], data.args[4], data.args[5]) # pass the position even if we may not need it.
                                    '''

                                    _command = Command(self.player.name, 'move_item', (tile['position'].x, tile['position'].y, tile['position'].z)) # send calculated_move action to server and give it the position of the tile we clicked.
                                    return _command

            elif(event.type == pygame.KEYUP):
                # when we want to do something with the keyboard.
                if event.key == pygame.K_m:
                    #(m)ove an item
                    pass
                elif(event.key == pygame.K_ESCAPE): # close the menu
                    return

    def open_items_on_ground(self, pos, tile):
        self.items_on_ground_background = pygame.image.load('./img/items_on_ground.png').convert_alpha()
        _start_item_x = 400
        _start_item_y = 250
        self.screen.blit(self.items_on_ground_background, (_start_item_x, _start_item_y))
        _items = tile['items'] #need to get the items from the position
        _page = 0 # internal int to keep track of what _item_groups page we are looking at currently.
        _max_items_per_group = 16
        # draw a box for the contained items.

        _item_groups = defaultdict(list)
        # first find out how many items we have and sort them into groups.

        # i need them 'paginated' so the order could be used as as x, y locations.
        _count = 0
        _group = 0
        for item in _items:
            if(_count > _max_items_per_group):
                _group = _group + 1
                _count = 0
            _item_groups[_group].append(item)
            _count = _count + 1


        # now that we've drawn the open_items_on_ground menu we need to wait until the player clicks a item.
        pygame.event.clear() # clear the event queue so we can wait for player feedback.
        while True:
                # blit the current _page worth of items.
                #TODO: take into consideration where the window opens.

                _item_x = _start_item_x + 3 # adjust for within image offset.
                _item_y = _start_item_y + 13

                # blit
                for item in _item_groups[_page]:
                    print(item)
                    fg = self.TileManager.TILE_TYPES[item.ident]['fg']
                    self.screen.blit(self.TileManager.TILE_MAP[fg], (_item_x, _item_y))
                    _item_x = _item_x + 24
                    if(_item_x > 24*3+_start_item_x):
                        _item_y = _item_y + 24
                        _item_x = _start_item_x + 3

                pygame.display.flip() # flip the screen
                event = pygame.event.wait() # wait for player input.
                if event.type == pygame.QUIT:
                    client.disconnect()
                    pygame.quit()
                    sys.exit()
                elif(event.type == pygame.MOUSEBUTTONDOWN):
                    # dragging to somwhere. need a check for bounds of the item while the mouse is being heldself.
                    pass
                elif(event.type == pygame.MOUSEBUTTONUP):
                    # we clicked somewhere while the menu is up.
                    # if we clicked an item we need to get the position and see what item it was.
                    pos = pygame.mouse.get_pos()
                    print('pos:', pos)
                    _x_count = 0
                    _y_count = 0
                    for item in _item_groups[_page]:
                        print('item.ident:', item.ident, end=' ')
                        # return the item clicked and do something with it.
                        _item_x_min = _x_count * 24 + _start_item_x
                        _item_x_max = _x_count * 24 + 23 + _start_item_x
                        print(_item_x_min, ',', _item_x_max)

                        if(_x_count > 3):
                            _x_count = 0
                            _y_count = _y_count + 1
                        _item_y_min = _y_count * 24 + _start_item_y
                        _item_y_max = _y_count * 24 - 23 + _start_item_x
                        print(_item_y_min, _item_y_max)

                        if(pos[0] > _item_x_min and pos[0] < _item_x_max):
                            # print('in x')
                            if(pos[1] > _item_y_min and pos[1] < _item_y_max):
                                print('clicked', str(item.ident))

                                # now we know the ident of the item we can pass that info to the server and let it parse and handle it.

                                _command = Command(self.player.name, 'move_item_to_player_storage', (tile['position'].x, tile['position'].y, tile['position'].z, item.ident)) # ask the server to pickup the item by ident. #TODO: is there a better way to pass it to the server without opening ourselves up to cheating?
                                return _command

                elif(event.type == pygame.KEYUP):
                    # when we want to do something with the keyboard.
                    if event.key == pygame.K_m:
                        #(m)ove an item
                        pass
                    elif(event.key == pygame.K_ESCAPE): # close the menu
                        return


#
#   if we start a client directly
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cataclysm LD Client', epilog="Please start the client with a first and last name for your character.")
    parser.add_argument('--host', metavar='Host', help='Server host', default='localhost')
    parser.add_argument('-p', '--port', metavar='Port', type=int, help='Server port', default=6317)
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
    last_time = time.time()
    while True:
        # if we recieve an update from the server process it. do this first.
        next_update = client.receive(False)
        if(next_update is not None):
            #print('--next_update--') # we recieved a message from the server. let's process it.
            #print(next_update)
            if(isinstance(next_update, Player)):
                #print('got playerupdate')
                client.player = next_update # client.player is updated
            if(isinstance(next_update, list)): # this is the list of chunks for the localmap
                #print('got localmapupdate')
                client.localmap = client.convert_chunks_to_localmap(next_update)
                client.player = client.find_player_in_localmap()
                client.draw_view_at_position(client.player.position) # update after everything is complete.
                client.messageBox.draw(client.screen) # update the screen after we've recieved an updated local view.
                pygame.display.flip() # now we have a fully built frame, display it
                last_time = time.time() # save the last time we got a localmap update


        # we also need to check and see if the player wants to do anything.
        ##################################
        # Handle Keys here.
        ##################################
        command = None # the command we will send to the server for processing.
        pygame.event.pump() # required so the game doesn't lock up

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.disconnect()
                pygame.quit()
                sys.exit()
            if(event.type == pygame.MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                for hotbar in client.hotbars:
                    if pos[0] >= hotbar.x and pos[0] <= hotbar.x + hotbar.width:
                        if pos[1] >= hotbar.y and pos[1] <= hotbar.y + hotbar.height:
                            hotbar.on_clicked(event.button, pos[0] - hotbar.x, pos[1] - hotbar.y)
                            pos = None # do this so we don't call any other UI element
                            break

                for button in client.buttons:
                    if pos is not None and pos[0] >= button.x and pos[0] <= button.x + button.width:
                        if pos[1] >= button.y and pos[1] <= button.y + button.height:
                            button.on_clicked(event.button, pos[0] - button.x, pos[1] - button.y)
                            pos = None
                            break

                for listbox in client.listboxes:
                    if pos is not None and pos[0] >= listbox.x and pos[0] <= listbox.x + listbox.width:
                        if pos[1] >= listbox.y and pos[1] <= listbox.y + listbox.height:
                            listbox.on_clicked(event.button, pos[0] - listbox.x, pos[1] - listbox.y)
                            pos = None
                            break

                # check to see if we clicked a localmap tile.
                if pos is not None and pos[0] >= 0 and pos[0] <= 20*24:
                    if pos[1] >= 0 and pos[1] <= 20*24:
                        _x = int(pos[0]/24)-1
                        _y = int(pos[1]/24)-1
                        # we clicked a tile: open the super menu
                        print('clicked tile: ' + str(_x) + ', ' + str(_y))
                        # tiles are 0-19 in x and y, need to extract the tiles for the map only and return it multi-dimensional array

                        # get the lowest value for x, y and subtract that from position to convert to 0,0

                        lowest_x = math.inf
                        lowest_y = math.inf
                        for tile in client.localmap[:]:
                            if tile['position'].x < lowest_x:
                                lowest_x = tile['position'].x
                            if tile['position'].y < lowest_y:
                                lowest_y = tile['position'].y

                        for tile in client.localmap[:]:
                            #we only want the spots the player can see.
                            if int(tile['position'].x - client.player.position.x) < -10 or int(tile['position'].x - client.player.position.x) > 10:
                                continue
                            if int(tile['position'].y - client.player.position.y) < -10 or int(tile['position'].y - client.player.position.y) > 10:
                                continue

                            if int(tile['position'].x - lowest_x - 1) == _x and int(tile['position'].y - lowest_y - 1) == _y:
                                command = client.open_super_menu(pos, tile) # next command becomes the result of the super_menu
                                break



            if event.type == pygame.KEYUP:
                #print(event.key)
                if event.key == pygame.K_KP2:
                    command = Command(client.player.name, 'move', ['south'])
                elif event.key == pygame.K_KP8:
                    command = Command(client.player.name, 'move', ['north'])
                elif event.key == pygame.K_KP4:
                    command = Command(client.player.name, 'move', ['west'])
                elif event.key == pygame.K_KP6:
                    command = Command(client.player.name, 'move', ['east'])
                elif event.key == pygame.K_KP_PLUS:
                    command = Command(client.player.name, 'move', ['up'])
                elif event.key == pygame.K_KP_MINUS:
                    command = Command(client.player.name, 'move', ['down'])
                elif event.key == pygame.K_b: # bash
                    print('open bash menu')
                    client.screen.fill((55, 55, 55), special_flags=pygame.BLEND_SUB) # darken the screen to indicate an action is required.
                    # open up the directional menu and wait for a input
                    w = int(client.screen.get_width()/2)
                    h = int(client.screen.get_height()/2)
                    directional_menu = Directional_choice(client.screen, (w, h)) # draw it at center of screen.
                    pygame.event.clear()
                    while True:
                        client.screen.blit(directional_menu.surface, (100,100))
                        pygame.display.flip() # now we have a fully built frame, display it
                        event = pygame.event.wait()
                        if event.type == pygame.KEYUP:
                            #print(event.key)
                            if event.key == pygame.K_KP2:
                                command = Command(client.player.name, 'bash', ['south'])
                            elif event.key == pygame.K_KP8:
                                command = Command(client.player.name, 'bash', ['north'])
                            elif event.key == pygame.K_KP4:
                                command = Command(client.player.name, 'bash', ['west'])
                            elif event.key == pygame.K_KP6:
                                command = Command(client.player.name, 'bash', ['east'])
                            break # break even if we don't choose a valid direction and leave the command as None
                elif event.key == pygame.K_c: # crafting menu
                    ident, direction = client.open_crafting_menu() # once the menu closes we should have a direction and an ident for a recipe
                    command = Command(client.player.name, 'create_blueprint', [ident, direction])
                elif event.key == pygame.K_e: # crafting menu
                    client.open_equipment_menu()
                elif event.key == pygame.K_ESCAPE: # close all menus
                    #TODO: print('closing all Buttons, listboxes, and textboxes')
                    client.buttons = []
                    client.listboxes = []
                    client.textboxes = []



        if(command is not None): # if we have a command to send then send it.
            client.send(command)

        if(time.time() - last_time >= 1.0): # if we haven't gotten an update lately let's request one.
            command = Command(client.player.name, 'request_localmap_update')
            client.send(command)
            last_time = time.time()
