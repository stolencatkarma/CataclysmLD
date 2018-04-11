# WYSIWYG editor for Cataclysm: Looming Darkness

# needs to load all items, furniture, terrain, and tilemap.png
import os
import sys
import json
from collections import defaultdict
import pygame
import pygame.locals

from tile import TileManager, Terrain
from item import Item, ItemManager
from recipe import RecipeManager, Recipe
from furniture import FurnitureManager, Furniture

from user_interface import Hotbar, Button, TextBox, ListBox, Listbox_item, FontManager

# need to create a pygame window and show a 2d view.
# ground floor is zero
# basements are -1 to -10
# pick and paint type actions.

# imports, exports to json
# eventual c:dda export support
# that's it?

class Editor:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Cataclysm: Looming Darkness WYSIWYG Building Editor')
        self.screen = pygame.display.set_mode((720, 480), pygame.ANYFORMAT)
        self.TileManager = TileManager()
        self.ItemManager = ItemManager()
        self.RecipeManager = RecipeManager() # contains all the known recipes in the game. for reference.
        self.FurnitureManager = FurnitureManager()
        self.FontManager = FontManager()
        self.curFloor = 0
        self.group = 'small residential'
        self.overmap_terrain = 'residential'
        self.comment = 'put a comment here'
        self.comment2 = 'put another comment here'
        self.comment3 = 'put one more comment here'
        self.fill_terrain = 't_floor'
        self.building_layout = defaultdict(dict)
        self.chunk_width = 1
        self.chunk_size = 13
        print(str(pygame.display.Info().current_w) + ', ' + str(pygame.display.Info().current_h))
        self.textboxes = []
        self.listboxes = []
        self.buttons = []
        # z-level UI components
        self.buttons.insert(0, Button(self.screen, self.FontManager.convert_string_to_surface('+'), (120,120,120), (pygame.display.Info().current_w-48,pygame.display.Info().current_h-24,24,24),'+'))
        self.buttons.insert(0, Button(self.screen, self.FontManager.convert_string_to_surface('-'), (120,120,120), (pygame.display.Info().current_w-24,pygame.display.Info().current_h-24,24,24),'-'))
        self.textboxes.insert(0, TextBox(self.screen, (120,120,120), (pygame.display.Info().current_w-72,pygame.display.Info().current_h-24,24,24), self.FontManager.convert_string_to_surface(str(self.curFloor))))

        # Listboxes for terrain, furniture, items.
        self.listboxes.insert(0, ListBox(self.screen, (120,120,120), (pygame.display.Info().current_w-360,0,120,240)))
        for k, item in self.TileManager.TILE_TYPES.items():
            #print(k.split('_'))
            if(k.split('_')[0] != 't'): #only load terrain here
                continue
            #print(k, item)
            self.listboxes[0].item_list.insert(len(self.listboxes[0].item_list), Listbox_item(k, self.FontManager.convert_string_to_surface(k), item))
        self.listboxes[0].item_list.sort(key=lambda x: x.text)

        self.listboxes.insert(1, ListBox(self.screen, (120,120,120), (pygame.display.Info().current_w-240,0,120,240)))
        for k, item in self.FurnitureManager.FURNITURE_TYPES.items():
            if(k.split('_')[0] != 'f'): #only load terrain here
                continue
            self.listboxes[1].item_list.insert(len(self.listboxes[1].item_list), Listbox_item(k, self.FontManager.convert_string_to_surface(k), item))
        self.listboxes[1].item_list.sort(key=lambda x: x.text)

        self.listboxes.insert(2, ListBox(self.screen, (120,120,120), (pygame.display.Info().current_w-120,0,120,240)))
        for k, item in self.ItemManager.ITEM_TYPES.items():
            print(k.split('_'))
            #print(k, item)
            self.listboxes[2].item_list.insert(len(self.listboxes[2].item_list), Listbox_item(k, self.FontManager.convert_string_to_surface(k), item))
        self.listboxes[2].item_list.sort(key=lambda x: x.text)


        ## selected stuff. left click listboxes to set
        self.selected_terrain = None
        self.textboxes.insert(1, TextBox(self.screen, (120,120,120), (pygame.display.Info().current_w-360,240,120,24), self.FontManager.convert_string_to_surface(None)))
        self.selected_furniture = None
        self.textboxes.insert(2, TextBox(self.screen, (120,120,120), (pygame.display.Info().current_w-240,240,120,24), self.FontManager.convert_string_to_surface(None)))
        self.selected_item = None
        self.textboxes.insert(3, TextBox(self.screen, (120,120,120), (pygame.display.Info().current_w-120,240,120,24), self.FontManager.convert_string_to_surface(None)))
        # export button.
        self.buttons.insert(0, Button(self.screen, self.FontManager.convert_string_to_surface('Export'), (120,120,120), (pygame.display.Info().current_w-256,pygame.display.Info().current_h-24,128,24),'Export'))
        self.buttons.insert(0, Button(self.screen, self.FontManager.convert_string_to_surface('Import'), (120,120,120), (pygame.display.Info().current_w-256,pygame.display.Info().current_h-48,128,24),'Import'))
        self.generate_z_level(0) # generate the base z-level. ground floor is always 0

    def generate_z_level(self, z_level):

        print('generating z_level:' + str(z_level))
        for i in range(self.chunk_size):
            for j in range(self.chunk_size):
                tile = {}
                tile['terrain'] = Terrain(self.fill_terrain)
                tile['items'] = [] # can be more then one item in a tile.
                tile['furniture'] = None # single furniture per tile
                tile['trap'] = None # one per tile
                tile['lumens'] = 0 # used in lightmap calculations
                try:
                    self.building_layout[i][j][z_level] = tile
                except Exception:
                    self.building_layout[i][j] = dict()
                    self.building_layout[i][j][z_level] = tile

    def draw_screen(self):
        self.screen.fill((55, 55, 55)) # clear screen between frames
        for i in range(self.chunk_size*self.chunk_width):
            for j in range(self.chunk_size*self.chunk_width):
                #print(self.building_layout[i][j].keys())
                if(not self.curFloor in self.building_layout[i][j]):
                    self.generate_z_level(self.curFloor)
                terrain = self.building_layout[i][j][self.curFloor]['terrain']
                furniture = self.building_layout[i][j][self.curFloor]['furniture'] # Furniture()
                items = self.building_layout[i][j][self.curFloor]['items'] # list [] of Item()
                light_intensity = self.building_layout[i][j][self.curFloor]['lumens']
                #print(terrain.ident)

                fg = self.TileManager.TILE_TYPES[terrain.ident]['fg']
                bg = self.TileManager.TILE_TYPES[terrain.ident]['bg']
                x = i
                y = j

                # first blit terrain
                if(bg is not None):
                    self.screen.blit(self.TileManager.TILE_MAP[bg], (x*24, y*24)) # blit background of the terrain
                if(fg is not None):
                    self.screen.blit(self.TileManager.TILE_MAP[fg], (x*24, y*24)) # blit foreground of the terrain

                # then blit furniture
                if(furniture is not None):
                    fg = self.TileManager.TILE_TYPES[furniture.ident]['fg']
                    self.screen.blit(self.TileManager.TILE_MAP[fg], (x*24, y*24))

                # then blit items (if there is a pile of items )
                if(len(items) > 0):
                    #only display the last item for now
                    fg = self.TileManager.TILE_TYPES[items[0].ident]['fg']
                    self.screen.blit(self.TileManager.TILE_MAP[fg], (x*24, y*24))

                # then blit vehicles

                # darken based on lumen level of the tile
                # light_intensity # 10 is max light level although lumen level may be higher.
                light_intensity = min(int((255-(light_intensity*25))/3), 255)
                light_intensity = max(light_intensity, 0)
                #print(light_intensity, end=',')
                #self.screen.fill((light_intensity, light_intensity, light_intensity), rect=(x*24, y*24, 24, 24), special_flags=pygame.BLEND_SUB)

                # render debug text
                #myfont = pygame.font.SysFont("monospace", 8)
                #label = myfont.render(str(position.x)+','+str(position.y), 1, (255,255,0))
                #self.screen.blit(label, (x*24, y*24))
                for button in self.buttons: #draw the buttons
                    button.draw()

                for listbox in self.listboxes: #draw the listboxes
                    listbox.draw()

                for textbox in self.textboxes: #draw the textboxes
                    textbox.draw()

    def export_to_file(self):
        # export the building into json format.
        terrain_keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        furniture_keys = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
        export = {}
        export['group'] = self.group
        export['overmap_terrain'] = self.overmap_terrain
        export['comment'] = self.comment
        export['comment2'] = self.comment2
        export['comment3'] = self.comment3
        export['fill_terrain'] = self.fill_terrain
        export['floors'] = {}
        export['terrain'] = {}
        export['furniture'] = {}
        export['traps'] = {}
        export['place_loot'] = {}
        export['place_monsters'] = {}
        # need to go through all the tiles and make a map of terrain, furniture, and loot groups.
        for floor_index in range(-10,10):
            for j in range(self.chunk_size):
                for i in range(self.chunk_size): #j, then i to record as rows.
                    try:
                        if(self.building_layout[i][j][floor_index]['terrain'].ident not in export['terrain'].values()):
                            #print('not in')
                            for key in terrain_keys:
                                if(key in export['terrain'].keys()):
                                    #print('continued')
                                    continue
                                else:
                                    export['terrain'][key] = self.building_layout[i][j][floor_index]['terrain'].ident
                                    break

                        if(self.building_layout[i][j][floor_index]['furniture'].ident not in export['furniture'].values()):
                            #print('not in')
                            for key in furniture_keys:
                                if(key in export['furniture'].keys()):
                                    #print('continued')
                                    continue
                                else:
                                    export['furniture'][key] = self.building_layout[i][j][floor_index]['furniture'].ident
                                    break
                    except Exception:
                        pass # this is sloppy.

        #print(export['terrain'].items())



        # write the floor rows
        for floor_index in range(-10,10):
            try:
                print(self.building_layout[i][j][floor_index]['terrain'].ident)
            except Exception:
                continue
            export['floors'][floor_index] = [] # list of strings, one per chunk_size
            for j in range(self.chunk_size):
                row = ''
                for i in range(self.chunk_size): #j, then i to record as rows.
                    try:
                        #get the ident and traslate it to the key.
                        for key, value in export['terrain'].items():
                            #print(key, value)
                            if(value == self.building_layout[i][j][floor_index]['terrain'].ident):
                                row = row + key
                    except Exception:
                        pass
                export['floors'][floor_index].append(row)

        with open('buildingeditortest.json', 'w') as outfile:
            json.dump(export, outfile, indent=4)

    def import_from_file(self):
        with open('buildingeditortest.json') as data_file: # load tile config so we know what tile foes with what ident
            data = json.load(data_file)

        terrain_keys = {}
        for key, terrain in data['terrain'].items():
            terrain_keys[key] = terrain

        furniture_keys = {}
        for key, furniture in data['furniture'].items():
            terrain_keys[key] = terrain

        place_loot_keys = {}
        for key, place_loot in data['place_loot'].items():
            place_loot_keys[key] = place_loot

        # fill editor.building_layout with floor data.
        for key, value in data.items():
            print(key, value)

            if(key == 'group'):
                self.group = value
            elif(key == 'overmap_terrain'):
                self.overmap_terrain = value
            elif(key == 'comment2'):
                self.comment2 = value
            elif(key == 'comment3'):
                self.comment3 = value
            elif(key == 'fill_terrain'):
                self.fill_terrain = value
            elif(key == 'floors'):
                for key, floor in value.items(): # for floor in floors
                    print('floor: ' + str(floor))
                    i, j = 0, 0
                    for row in floor:
                        print('row: ' + str(row))
                        for char in row:
                            for key2, value2 in terrain_keys.items():
                                if(char == key2):
                                    tile = {}
                                    tile['terrain'] = Terrain(value2)
                                    tile['items'] = [] # can be more then one item in a tile.
                                    tile['furniture'] = None # single furniture per tile
                                    tile['trap'] = None # one per tile
                                    tile['lumens'] = 0 # used in lightmap calculations
                                    print('-------------------')
                                    print(value2)
                                    print(i)
                                    print(j)
                                    print(int(key))
                                    if(not int(key) in self.building_layout[i][j]):
                                        self.generate_z_level(int(key))
                                    self.building_layout[i][j][int(key)] = tile
                            i = i + 1
                        j = j + 1
                        i = 0 # reset x for each row



            '''
            for key, value in item.items():
                print(str(value) + ' : ' + str(type(value)))
                if(isinstance(value, list)):
                    self.ITEM_TYPES[item['ident']][key] = []
                    for add_value in value:
                        self.ITEM_TYPES[item['ident']][key].append(str(add_value))
                else:
                    self.ITEM_TYPES[item['ident']][key] = str(value)'''
                #print('.', end='')

                            #print('x', end='')
if __name__ == "__main__": # if we start directly
    editor = Editor()
    while True:
        pygame.event.pump() # required so the pygame doesn't lock up
        editor.screen.fill((55, 55, 55)) # clear screen between frames
        editor.draw_screen()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif(event.type == pygame.MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                print(str(pos[0]) + ', ' + str(pos[1]))
                if pos[0] >= 0 and pos[0] <= editor.chunk_size*editor.chunk_width*24:
                    if pos[1] >= 0 and pos[1] <= editor.chunk_size*editor.chunk_width*24:
                        print('clicked tile: ' + str(int(pos[0]/24)) + ', ' + str(int(pos[1]/24)))
                        if(event.button == 1):
                            if(editor.selected_item is not None):
                                editor.building_layout[int(pos[0]/24)][int(pos[1]/24)][editor.curFloor]['items'].append(Item(editor.selected_item))
                            elif(editor.selected_furniture is not None):
                                editor.building_layout[int(pos[0]/24)][int(pos[1]/24)][editor.curFloor]['terrain'] = Terrain(editor.fill_terrain) # can only place furniture on fill_terrain otherwise the chars would overwrite each other.
                                editor.building_layout[int(pos[0]/24)][int(pos[1]/24)][editor.curFloor]['furniture'] = Furniture(editor.selected_furniture)
                            elif(editor.selected_terrain is not None):
                                editor.building_layout[int(pos[0]/24)][int(pos[1]/24)][editor.curFloor]['terrain'] = Terrain(editor.selected_terrain)
                                editor.building_layout[int(pos[0]/24)][int(pos[1]/24)][editor.curFloor]['furniture'] = None
                        elif(event.button == 3):
                            editor.building_layout[int(pos[0]/24)][int(pos[1]/24)][editor.curFloor]['items'] = []
                            editor.building_layout[int(pos[0]/24)][int(pos[1]/24)][editor.curFloor]['furniture'] = None
                            editor.building_layout[int(pos[0]/24)][int(pos[1]/24)][editor.curFloor]['terrain'] = Terrain(editor.fill_terrain)

                for button in editor.buttons:
                    if pos[0] >= button.x and pos[0] <= button.x + button.width:
                        if pos[1] >= button.y and pos[1] <= button.y + button.height:
                            if button.command == '+':
                                editor.curFloor = editor.curFloor + 1
                                if(editor.curFloor > 10):
                                    editor.curFloor = 10
                                editor.textboxes[0] = TextBox(editor.screen, (120,120,120), (pygame.display.Info().current_w-72,pygame.display.Info().current_h-24,24,24), editor.FontManager.convert_string_to_surface(str(editor.curFloor)))
                            elif button.command == '-':
                                editor.curFloor = editor.curFloor - 1
                                if(editor.curFloor < -10):
                                    editor.curFloor = -10
                                editor.textboxes[0] = TextBox(editor.screen, (120,120,120), (pygame.display.Info().current_w-72,pygame.display.Info().current_h-24,24,24), editor.FontManager.convert_string_to_surface(str(editor.curFloor)))
                            elif button.command == 'Export':
                                editor.export_to_file()
                            elif button.command == 'Import':
                                editor.import_from_file()


                listbox = editor.listboxes[0]
                if pos[0] >= listbox.x and pos[0] <= listbox.x + listbox.width:
                    if pos[1] >= listbox.y and pos[1] <= listbox.height:
                        if(event.button == 1):
                            text = listbox.on_clicked(event.button, pos[0] - listbox.x, pos[1] - listbox.y).text
                            editor.textboxes[1].surface_text = editor.FontManager.convert_string_to_surface(text)
                            editor.selected_terrain = text
                            #clear the textbox.
                        elif(event.button == 3):
                            editor.textboxes[1].surface_text = editor.FontManager.convert_string_to_surface(None)
                            editor.selected_terrain = None
                        else:
                            listbox.on_clicked(event.button, pos[0] - listbox.x, pos[1] - listbox.y)
                listbox = editor.listboxes[1]
                if pos[0] >= listbox.x and pos[0] <= listbox.x + listbox.width:
                    if pos[1] >= listbox.y and pos[1] <= listbox.height:
                        if(event.button == 1):
                            text = listbox.on_clicked(event.button, pos[0] - listbox.x, pos[1] - listbox.y).text
                            editor.textboxes[2].surface_text = editor.FontManager.convert_string_to_surface(text)
                            editor.selected_furniture = text
                            #clear the textbox.
                        elif(event.button == 3):
                            editor.textboxes[2].surface_text = editor.FontManager.convert_string_to_surface(None)
                            editor.selected_furniture = None
                        else:
                            listbox.on_clicked(event.button, pos[0] - listbox.x, pos[1] - listbox.y)
                listbox = editor.listboxes[2]
                if pos[0] >= listbox.x and pos[0] <= listbox.x + listbox.width:
                    if pos[1] >= listbox.y and pos[1] <= listbox.height:
                        if(event.button == 1):
                            text = listbox.on_clicked(event.button, pos[0] - listbox.x, pos[1] - listbox.y).text
                            editor.textboxes[3].surface_text = editor.FontManager.convert_string_to_surface(text)
                            editor.selected_item = text
                            #clear the textbox.
                        elif(event.button == 3):
                            editor.textboxes[3].surface_text = editor.FontManager.convert_string_to_surface(None)
                            editor.selected_item = None
                        else:
                            listbox.on_clicked(event.button, pos[0] - listbox.x, pos[1] - listbox.y)
