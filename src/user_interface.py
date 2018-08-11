# this file contains all the classes to build GUI components.
import pygame
import pygame.locals

class Menu_item:
    # a single menu item that when clicked does something.
    def __init__(self):
        return

# Popup_menu consists of 1 textbox and 1 listbox.
class Popup_menu:
    # needs popup menus in popup menus
    def __init__(self, screen):
        self.screen = screen
        menu_items = []
        return


class Directional_choice:
    # the image that pops up when a direction is required.
    # we should loop until we get a direction.
    def __init__(self, screen, x=0, y=0):
        # popup the png and wait for a click.
        self.screen = screen
        self.x = x
        self.y = y
        self.surface = pygame.image.load('./img/direction.png') #.convert_alpha()
        #self.screen.blit(self.surface, (self.x, self.y))

class Hotbar: # contains a list of Item() that the player has and shows up on the screen
    def __init__(self, screen, x=0, y=0):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.item_list = []
        self.hotbar_drag_icon = pygame.image.load('./img/hotbar_drag_icon.png').convert_alpha()
        self.hotbar_item_background = pygame.image.load('./img/hotbar_item_background.png').convert_alpha()

    def add(self, item, surface):
        # we'll need a reference to the .png (surface) when we add an item otherwise we'd have to pass the whole list for each hotbar.
        item.surface = surface
        self.item_list.append(item)

    def remove(self, item):
        for value in self.item_list[:]:
            if(value == item):
                self.item_list.remove(item)

    def draw(self): # call this at the end of the drawing routine for each hotbar we have.
        rect = (self.x, self.y, int(len(self.item_list)+1) * 28 + 4, 32)
        self.width = int(len(self.item_list)+1) * 28 + 4
        pygame.draw.rect(self.screen, (0, 125, 125), rect, 0) # draw the background to the Hotbar procedurally while setting up a rect.
        self.screen.blit(self.hotbar_drag_icon, (self.x + 2, self.y + 2)) # draw the drag bar
        count = 4 # start 4 pixels in
        for item in self.item_list:
            count = count + 28 # skip the first one. that's the drag bar position.
            self.screen.blit(self.hotbar_item_background, (self.x + count, self.y + 4)) # draw an item box for each item.
            self.screen.blit(item.surface, (self.x + count, self.y + 4)) # draw an item box for each item.

    def on_clicked(self, button, click_pos_x, click_pos_y):
        # if the user clicks the bar what happens?
        #print('clicked mouse: ' + str(button) + ' @ ' + str(click_pos_x) + ', ' + str(click_pos_x))
        item_clicked = int(click_pos_x/28)
        #print('item clicked: ' + str(item_clicked))
        if(item_clicked > 0):
            item_clicked = item_clicked - 1
            print('clicked item: ' + str(item_clicked))
        else:
            print('clicked drag bar')

    def on_dragged_to(self):
        # when the user drags an item to the bar.
        return

class Button:
    def __init__(self, screen, surface_text, color, rect, command):
        self.rect = rect
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.screen = screen
        self.color = color
        self.surface_text = surface_text
        self.command = command

    def draw(self):
        pygame.draw.rect(self.screen, (255,255,255), self.rect)
        pygame.draw.rect(self.screen, self.color, (self.x+1, self.y+1, self.width-2, self.height-2))
        center_x = int(self.width/2+self.x)
        center_y = int(self.height/2+self.y)
        text_center_x = center_x - self.surface_text.get_width()/2
        text_center_y = center_y - self.surface_text.get_height()/2
        self.screen.blit(self.surface_text, (text_center_x, text_center_y))

    def on_clicked(self, button, click_pos_x, click_pos_y):
        # if the user clicks the bar what happens?
        if(button == 1):
            print('left click')
        elif(button == 3):
            print('right click')
        elif(button == 2):
            print('middle click')
        return

class ListBox:
    def __init__(self, screen, color, rect):
        self.rect = rect
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.screen = screen
        self.color = color
        self.item_list = [] # we need a listbox container item.
        self.page = 0 # keep track of what page you're on.

    def draw(self):
        pygame.draw.rect(self.screen, (255,255,255), self.rect)
        pygame.draw.rect(self.screen, self.color, (self.x+1, self.y+1, self.width-2, self.height-2))
        items_per_page = int(self.height/12)
        spacing_y = 12
        count = 0
        for item in self.item_list[int(self.page*items_per_page):int(self.page*items_per_page)+items_per_page]:
            self.screen.blit(item.surface_text, (self.x + 4, 2 + self.y + int(count * spacing_y)))
            count = count + 1

    def add(self, reference_object):
        self.item_list.append(reference_object)

    def on_clicked(self, button, click_pos_x, click_pos_y):
        spacing_y = 12
        # if the user clicks the bar what happens?
        print('clicked mouse: ' + str(button) + ' @ ' + str(click_pos_x) + ', ' + str(click_pos_x))
        item_clicked = int(click_pos_y/spacing_y)
        #print('clicked item: ' + str(item_clicked))
        if(str(button) == str(4)):
            if(self.page > 0):
                self.page = self.page - 1
                return
        elif(str(button) == str(5)):
            max_pages = int(len(self.item_list) / int(self.height/12))
            if(self.page < max_pages):
                self.page = self.page + 1
                return
        elif(str(button) == str(1)):
            items_per_page = int(self.height/12)
            if(self.page*items_per_page+item_clicked <= len(self.item_list)):
                return self.item_list[self.page*items_per_page+item_clicked]
            else:
                return None

class Listbox_item:
    def __init__(self, text, surface_text, reference_object):
        self.text = text
        self.surface_text = surface_text
        self.reference_object = reference_object
        #text

class TextBox:
    def __init__(self, screen, color, rect, surface_text):
        self.rect = rect
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.screen = screen
        self.color = color
        self.surface_text = surface_text

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
        #print(self.x, self.y)
        self.screen.blit(self.surface_text, (self.x, self.y))

class FontManager:
    def __init__(self):
        self.tilemapPx = 6
        self.tilemapPy = 8
        self.CHARACTER_MAP = self.load_font_table("./img/font6x8.png", self.tilemapPx, self.tilemapPy)

    def load_font_table(self, filename, width, height):
        print('loading font table: ' + str(filename))
        image = pygame.image.load(filename).convert_alpha()
        image_width, image_height = image.get_size()

        tile_table = []
        for tile_y in range(0, int(image_height/height)):
            line = []
            for tile_x in range(0, int(image_width/width)):
                rect = (tile_x*width, tile_y*height, width, height)
                #pygame.image.save(image.subsurface(rect), './fontmap/' + str(int(len(tile_table))) + '.png') # for saving the tilemap to individual files
                tile_table.insert(int(len(tile_table)), image.subsurface(rect))
        return tile_table

    def convert_string_to_surface(self, string):
        # 0-29    uppercase row
        if string is None:
            string = 'None'
        _map_8x12 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                'T', 'U', 'V', 'W', 'X', 'Y', 'Z', ' ', ' ', ' ', ' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', ' ',
                ' ', ' ', ' ', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '\`', '-', '=', ' ', ' ', ' ',
                ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ')', '!', '@', '#', '$',
                '%', '^', '&', '*', '(', '~', '_', '+', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ',
                ' ', ' ', ' ', ' ', ' ', ' ', '{', '}', '|', ':', '\"', '<', '>', '?']
        _map_8x10 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6',
                '7', '8', '9', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '=', '_', '+', '[', ']', '{',
                '}', '\\', '|', ':', ';', '\"', '\'', '/', '~', '\`', ' ']
        _map_6x8 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6',
                '7', '8', '9', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '=', '_', '+', '[', ']', '{',
                '}', ':', ';', ',', ' ']
        count = 0
        surface = pygame.Surface((self.tilemapPx*len(string), self.tilemapPy))
        surface.fill((255,255,255,255))
        for char in string:
            # find the corresponding fontmap image and append it to the surface
            surface.blit(self.CHARACTER_MAP[_map_8x10.index(char)], ((count*self.tilemapPx), 0))
            count = count + 1

        return surface

class Crafting_Menu:
    # the menu that holds all a character's (player or NPC) recipes.
    # title
    # 8 buttons (one per skill used)
    # 3 listboxes
    # A container for the side bar info
    # Sidebar
    # Title - Items Needed
    # Difficulty
    # required components
    # required tool tags
    # required tools
    # time to complete
    # if player chooses one to craft make a blueprint with the recipe. the blueprint is a container that needs to be filled with the required items.
    # any player may dump items into the blueprint and any player can work on the blueprint as a team or solo provided there is enough room around it to work.

    def __init__(self, screen, list_of_known_recipes, rect, ref_FontManager):
        self.rect = rect
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.screen = screen
        # Sidebar stuff
        self.sidebar = {}
        self.sidebar['result'] = ''
        self.sidebar['skill_used'] = ''
        self.sidebar['difficulty'] = 0
        self.sidebar['time'] = 0
        self.sidebar['learned_from'] = ''
        self.sidebar['required_tool_tag'] = []
        self.sidebar['tools'] = []
        self.sidebar['components'] = []
        '''
        result: halberd
        skill_used: fabrication
        difficulty: 7
        time: 360000
        learned_from: [['textbook_weapwest', 6]]
        required_tool_tag: ['HAMMER', 'CHISEL']
        tools: [[['TONGS', -1]], [['ANVIL', -1]], [['swage', -1]], [['FORGE', 350], ['OXY_TORCH', 70]]]
        components: [[['steel_lump', 3], ['steel_chunk', 12], ['scrap', 36]], [['2x4', 4], ['stick', 8]], [['fur', 2], ['leather', 2]]]
        '''
        # build the menu

        self.UI_components = []
        _surface = ref_FontManager.convert_string_to_surface('Crafting Menu')
        self.UI_components.append(TextBox(self.screen, (0, 0, 200), (0, 0, self.width, 24), _surface))
        # get the list of skills used in the list of known recipes.
        unique_skill_used = []
        # parse the list and fill our internal lists with the items contained
        for recipe in list_of_known_recipes:
            if(recipe['skill_used'] not in unique_skill_used):
                unique_skill_used.append(recipe['skill_used'])
        #print(unique_skill_used)
        num_buttons = len(unique_skill_used) # make a number of buttons equal to the number of unique skills found
        #print('num_buttons: ' +str(num_buttons))
        #print(self.width)
        button_width = int(self.width / num_buttons)
        #print('button_width: ' +str(button_width))
        count = 0
        for unique_skill in unique_skill_used:
            # screen, surface_text, color, rect, command
            _surface = ref_FontManager.convert_string_to_surface(unique_skill)
            self.UI_components.append(Button(self.screen, _surface, (0,150,150), ((self.x + button_width)*count, 24, button_width, 48), 'skill_' + str(unique_skill)))
            count = count + 1

        # now add the listboxes
        listbox_width = int((self.width-288)/3)
        lb1 = ListBox(self.screen, (0,0,0), (0,72,listbox_width,self.height-72))
        lb2 = ListBox(self.screen, (0,0,0), (listbox_width,72,listbox_width,self.height-72))
        lb3 = ListBox(self.screen, (0,0,0), (listbox_width*2,72,listbox_width,self.height-72))
        # and populate them
        for recipe in list_of_known_recipes:
            _surface = ref_FontManager.convert_string_to_surface(recipe['result'])
            item_to_add = Listbox_item(recipe['result'], _surface, recipe)
            if(len(lb1.item_list) < int(lb1.height/12)):
                lb1.add(item_to_add)
            elif(len(lb2.item_list) < int(lb2.height/12)):
                lb2.add(item_to_add)
            elif(len(lb3.item_list) < int(lb3.height/12)):
                lb3.add(item_to_add)
        self.UI_components.append(lb1)
        self.UI_components.append(lb2)
        self.UI_components.append(lb3)

        # now add the Sidebar
        _surface = ref_FontManager.convert_string_to_surface('Sidebar')
        self.UI_components.append(TextBox(self.screen, (0,0,200), (self.width-288, 72, self.width, self.height-72), _surface))
        # now add the crafting button
        _surface = ref_FontManager.convert_string_to_surface('craft')
        self.UI_components.append(Button(self.screen, _surface, (0,150,150), ((self.width-100), self.height-48, 100, 48), 'craft'))


# we need a way to convert tile properties to actions. might as well make a class for each.
class Movement_menu:
    def __init__(self, screen, rect, ref_FontManager):
        possible_actions = ['move', 'attack_move']
        self.rect = rect
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.screen = screen
        self.UI_components = []

        _surface = ref_FontManager.convert_string_to_surface('Movement')
        self.UI_components.append(TextBox(self.screen, (0, 0, 200), (self.x, self.y, self.width, 12), _surface))
        # create a listbox and fill it with menu_items

        lb1 = ListBox(self.screen, (0,0,0), (self.x, self.y+12,self.width, self.height-12))
        # and populate them
        for possible_action in possible_actions:
            print(possible_action)
            _surface = ref_FontManager.convert_string_to_surface(possible_action)
            item_to_add = Listbox_item(possible_action, _surface, possible_action)
            if(len(lb1.item_list) < int(lb1.height/12)):
                lb1.add(item_to_add)
            else:
                break
        self.UI_components.append(lb1)
        print('movement menu created.')

# differs from a regular button because it always displays the background even without an item.
class Equipment_Button:
    def __init__(self, screen, position, item=None):
        self.equipment_item_background = pygame.image.load('./img/equipment_item_background.png').convert_alpha()
        self.position = position
        self.item = item
        self.screen = screen

    def draw(self):
        self.screen.blit(self.equipment_item_background, self.position)
        if(self.item is not None):
            # blit item as well.
            pass

class Equipment_Menu:
    # equipment menu needs
    #  an overlay of the character.
    #  2 slots per body part arranged over the overlay.
    #  Head  - 152,4  - 224,4
    #  Torso - 188,62 - 188,100
    #  rgtArm- 110,48 - 110,76
    #  lftArm- 264,48 - 264,76
    #  rgtHnd- 114,110- 142,128 - equip  62,110
    #  lftHnd- 262,110- 234,128 - equip 312, 110
    #  rgtLeg- 116,170- 144,170
    #  lftLeg- 234,170- 262,170
    #  rgtft-  112,214- 140,214
    #  lftft-  236,214- 264,214

    #  8x16 empty grid which points to an equipped container.contained_items. it leaves an empty space at the end for adding more items through drag and drop.
    #   8,296 start, 384, 192 size
    #  auto-sort should be OFF for anything container related so player's can move and sort as they wish and it will stay that way.

    def __init__(self, screen, rect, ref_FontManager, bodyParts):
        # this is called when the menu is opened. we should destroy it and create it as it's opened or closed to properly keep things initalized

        # screen locations for the equipment. needs reference item and screen location.
        self.equipment_slots = {}
        self.UI_components = []
        self.surface = pygame.image.load('./img/equipment_overlay.png').convert_alpha()

        self.rect = rect
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.screen = screen
        self.bodyParts = bodyParts


        # overlay
        self.open_containers = [] # these show up on the grid at the bottom. a list
        self.open_container_grid = {} # 16 across and 8 down grid to hold the items in open containers.
        for i in range(16):
            self.open_container_grid[i] = {}
            for j in range(8):
                self.open_container_grid[i][j] = None # initialize it with no Item in this position.
        for container in self.open_containers:
            for item in container.contained_items:
                pass


        self.update()

    # this refreshes self.UI_components
    def update(self):
        self.equipment_slots = {} # reset everything
        for bodyPart in self.bodyParts:
            print('===============================================')
            #print('bodyPart', bodyPart)
            #print('bodyPart.ident', bodyPart.ident)
            print('bodyPart.ident.split(\'_\')', bodyPart.ident.split('_'))
            ident, location = bodyPart.ident.split('_') # HEAD_0 becomes 'HEAD', '0' ARM_LEFT becomes 'ARM', 'LEFT'

            if(ident not in self.equipment_slots):
                self.equipment_slots[ident] = {}  # initialize if it doesn't exist.
            if(location not in ident):
                self.equipment_slots[ident][location] = {}  # initialize if it doesn't exist.
                if('slot0' not in self.equipment_slots[ident][location]):
                    self.equipment_slots[ident][location]['slot0'] = {}
                if('item' not in self.equipment_slots[ident][location]['slot0']):
                    self.equipment_slots[ident][location]['slot0']['item'] = None
                if('position' not in self.equipment_slots[ident][location]['slot0']):
                    self.equipment_slots[ident][location]['slot0']['position'] = (-999,-999)

                if('slot1' not in self.equipment_slots[ident][location]):
                    self.equipment_slots[ident][location]['slot1'] = {}
                if('item' not in self.equipment_slots[ident][location]['slot1']):
                    self.equipment_slots[ident][location]['slot1']['item'] = None
                if('position' not in self.equipment_slots[ident][location]['slot1']):
                    self.equipment_slots[ident][location]['slot1']['position'] = (-999,-999)

                if(ident == 'HAND' and 'slot_equipped' not in self.equipment_slots[ident][location]):
                    self.equipment_slots[ident][location]['slot_equipped'] = {}

            if(ident == 'HEAD'):
                # first setup slot0
                self.equipment_slots[ident][location]['slot0']['item'] = bodyPart.slot0
                self.equipment_slots[ident][location]['slot0']['position'] = (152, 4)
                # then slot1
                self.equipment_slots[ident][location]['slot1']['item'] = bodyPart.slot1
                self.equipment_slots[ident][location]['slot1']['position'] = (224, 4)

            if(ident == 'TORSO'):
                self.equipment_slots[ident][location]['slot0']['item'] = bodyPart.slot0
                self.equipment_slots[ident][location]['slot0']['position'] = (188, 62)
                self.equipment_slots[ident][location]['slot1']['item'] = bodyPart.slot1
                self.equipment_slots[ident][location]['slot1']['position'] = (188, 100)
            if(ident == 'ARM'): # need to be able to handle a arbitrary number of arms in the future.
                if(location == 'RIGHT'):
                    self.equipment_slots[ident][location]['slot0']['item'] = bodyPart.slot0
                    self.equipment_slots[ident][location]['slot0']['position'] = (110, 48)
                    self.equipment_slots[ident][location]['slot1']['item'] = bodyPart.slot1
                    self.equipment_slots[ident][location]['slot1']['position'] =  (110, 76)
                elif(location == 'LEFT'):
                    self.equipment_slots[ident][location]['slot0']['item'] = bodyPart.slot0
                    self.equipment_slots[ident][location]['slot0']['position'] = (264, 48)
                    self.equipment_slots[ident][location]['slot1']['item'] = bodyPart.slot1
                    self.equipment_slots[ident][location]['slot1']['position'] = (264, 76)
            if(ident == 'HAND'): # need to be able to handle a arbitrary number of hands in the future.
                if(location == 'RIGHT'):
                    self.equipment_slots[ident][location]['slot0']['item'] = bodyPart.slot0
                    self.equipment_slots[ident][location]['slot0']['position'] = (114, 110)
                    self.equipment_slots[ident][location]['slot1']['item'] = bodyPart.slot1
                    self.equipment_slots[ident][location]['slot1']['position'] = (142, 128)
                    self.equipment_slots[ident][location]['slot_equipped']['item'] = bodyPart.slot_equipped
                    self.equipment_slots[ident][location]['slot_equipped']['position'] = (62, 110)
                elif(location == 'LEFT'):
                    self.equipment_slots[ident][location]['slot0']['item'] = bodyPart.slot0
                    self.equipment_slots[ident][location]['slot0']['position'] = (262, 110)
                    self.equipment_slots[ident][location]['slot1']['item'] = bodyPart.slot1
                    self.equipment_slots[ident][location]['slot1']['position'] = (234, 128)
                    self.equipment_slots[ident][location]['slot_equipped']['item'] = bodyPart.slot_equipped
                    self.equipment_slots[ident][location]['slot_equipped']['position'] = (312, 110)
            if(ident == 'LEG'): # need to be able to handle a arbitrary number of legs in the future.
                if(location == 'RIGHT'):
                    self.equipment_slots[ident][location]['slot0']['item'] = bodyPart.slot0
                    self.equipment_slots[ident][location]['slot0']['position'] = (116, 170)
                    self.equipment_slots[ident][location]['slot1']['item'] = bodyPart.slot1
                    self.equipment_slots[ident][location]['slot1']['position'] = (144, 170)
                elif(location == 'LEFT'):
                    self.equipment_slots[ident][location]['slot0']['item'] = bodyPart.slot0
                    self.equipment_slots[ident][location]['slot0']['position'] = (234, 170)
                    self.equipment_slots[ident][location]['slot1']['item'] = bodyPart.slot1
                    self.equipment_slots[ident][location]['slot1']['position'] = (262, 170)
            if(ident == 'FOOT'): # need to be able to handle a arbitrary number of feet in the future.
                if(location == 'RIGHT'):
                    self.equipment_slots[ident][location]['slot0']['item'] = bodyPart.slot0
                    self.equipment_slots[ident][location]['slot0']['position'] = (112, 214)
                    self.equipment_slots[ident][location]['slot1']['item'] = bodyPart.slot1
                    self.equipment_slots[ident][location]['slot1']['position'] = (140, 214)
                elif(location == 'LEFT'):
                    self.equipment_slots[ident][location]['slot0']['item'] = bodyPart.slot0
                    self.equipment_slots[ident][location]['slot0']['position'] = (236, 214)
                    self.equipment_slots[ident][location]['slot1']['item'] = bodyPart.slot1
                    self.equipment_slots[ident][location]['slot1']['position'] = (264, 214)
        self.UI_components = []
        for key, ident in self.equipment_slots.items():
            print(key, ident)
            for key, location in ident.items():
                print(location)
                # always blit the background if the limb exists.
                #screen, position, item=None
                self.UI_components.append(Equipment_Button(self.screen, location['slot0']['position']))
                self.UI_components.append(Equipment_Button(self.screen, location['slot1']['position']))
                # usually only hands have a 'slot_equipped' slot
                if('slot_equipped' in location):
                    self.UI_components.append(Equipment_Button(self.screen, location['slot_equipped']['position']))

                # append the items if it exists in the slot.
                if(location['slot0']['item'] is not None):
                    self.UI_components.append(location['slot0']['item'], location['slot0']['position'])
                if(location['slot1']['item'] is not None):
                    self.UI_components.append(location['slot1']['item'], location['slot1']['position'])
                if('slot_equipped' in location):
                    if(location['slot_equipped']['item'] is not None):
                        self.UI_components.append(location['slot_equipped']['item'], location['slot_equipped']['position'])

        #TODO: open_container_grid at the bottom.


# class for when you create a super menu item for creature
class Super_menu_creature:
    def __init__(self):
        possible_actions = ['attack', 'attack_repeat', 'talk']
        # also the actions the player can use on the target.
        # TODO: attack submenu will let you target limbs and know the chance to hit.
        pass

class Super_menu_furniture:
    def __init__(self):
        possible_actions = ['smash', 'drag', 'use']
        pass

class Super_menu_blueprint:
    def __init__(self):
        possible_actions = ['fill_or_take_items', 'examine', 'work_on']
        pass

class Super_menu_items:
    def __init__(self):
        # TODO: open item management screen
        pass

class Super_menu_vehicle:
    def __init__(self):
        possible_actions = []
        '''- if not in
         - get in
         - get on
         - open vehicle management screen
        - if in
         - drive/stop driving
         - switch seats -> open submenu
         '''
        pass

class Super_menu:
    # the base level, the first thing the player always sees when clicking a tile.
    def __init__(self, screen, tile, rect, ref_FontManager):
        self.rect = rect
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.screen = screen
        self.menu_items = []
        self.UI_components = []

        print('------------ SUPER MENU ------------')
        self.menu_items.append('Movement')

        if tile['creature'] is not None: # is there a creature here to interact with?
            self.menu_items.append('Creature')
        if tile['terrain'] is not None: # there should always be terrain there but check anyways.
            #self.menu_items.append('Terrain')
            #TODO: Support terrain super menu item.
            pass
        if len(tile['items']) > 0: # if there's at least 1 item here that's enough.
            self.menu_items.append('Items')
        if tile['furniture'] is not None: # add the furniture submenu
            self.menu_items.append('Furniture')
        if tile['vehicle'] is not None: # add the vehicle submenu
            #self.menu_items.append('Vehicle')
            pass # TODO: add trap disarming actions.
        if tile['trap'] is not None:
            pass # TODO: add trap disarming actions.
        # if tile['bullet'] is not None: # in the future it may be possible to react to bullets in flight but not right now.
        print('Menu Items Parsed: ')
        for obj in self.menu_items:
            print(obj)
        print('---------- END SUPER MENU ----------')

        # create the textbox for the top.
        _surface = ref_FontManager.convert_string_to_surface('Super Menu') # create a surface from string.
        self.UI_components.append(TextBox(self.screen, (0, 0, 200), (self.x, self.y, self.width, 12), _surface)) # draw the converted string from surface.

        # create a listbox and fill it with menu_items
        lb1 = ListBox(self.screen, (0,0,0), (self.x, self.y+12,self.width, self.height-12))
        # and populate them
        for menu_item in self.menu_items:
            _surface = ref_FontManager.convert_string_to_surface(menu_item)
            item_to_add = Listbox_item(menu_item, _surface, menu_item)
            if(len(lb1.item_list) < int(lb1.height/12)):
                lb1.add(item_to_add)
            else:
                break
        self.UI_components.append(lb1)

        # this should now be setup.
