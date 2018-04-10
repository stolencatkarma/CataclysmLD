# this file contains all the classes to build GUI components.
import pygame
import pygame.locals

class Menu_item:
    # a single menu item that when clicked does something.
    def __init__(self):
        return

class Popup_menu:
    # needs popup menus in popup menus
    def __init__(self):
        menu_items = []
        return

class Hotbar: # contains a list of Item() that the player has and shows up on the screen
    def __init__(self, screen, x=0, y=0):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.item_list = []
        self.hotbar_drag_icon = pygame.image.load('hotbar_drag_icon.png').convert_alpha()
        self.hotbar_item_background = pygame.image.load('hotbar_item_background.png').convert_alpha()

    def add(self, item, surface):
        # we'll need a refernce to the .png (surface) when we add an item otherwise we'd have to pass the whole list for each hotbar.
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
            return self.item_list[self.page*items_per_page+item_clicked]


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
        self.screen.blit(self.surface_text, (self.x + 4, 2 + self.y))

class FontManager:
    def __init__(self):
        self.tilemapPx = 6
        self.tilemapPy = 8
        self.CHARACTER_MAP = self.load_font_table("font6x8.png", self.tilemapPx, self.tilemapPy)

    def load_font_table(self, filename, width, height):
        print('loading font table: ' + str(filename))
        #print(width)
        #print(height)
        image = pygame.image.load(filename).convert_alpha()
        image_width, image_height = image.get_size()
        #print(str(image_width))
        #print(str(image_height))

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
                '}', ':', ';', ' ']
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

    def __init__(self, screen, list_of_known_recipes, rect):
        self.rect = rect
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.screen = screen
        # build the menu

        self.UI_components = []
        self.UI_components.append(TextBox(self.screen, (0, 0, 200), (0, 0, self.width, 24), 'Crafting Menu'))
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
            self.UI_components.append(Button(self.screen, unique_skill, (0,150,150), ((self.x + button_width)*count, 24, button_width, 48)))
            count = count+1
        # now add the listboxes
        lb1 = ListBox(self.screen, (0,0,0), (0,72,150,self.height-72))


        self.UI_components.append(ListBox(self.screen, (0,0,0), (125,72,150,self.height-72)))
        self.UI_components.append(ListBox(self.screen, (0,0,0), (250,72,150,self.height-72)))
        # and populate them
        for recipe in list_of_known_recipes:
            item_to_add = Listbox_item(recipe['result'], recipe)
            if(len(lb1.item_list) < int(lb1.height/14)):
                lb1.add(item_to_add)
            #TODO: fill the other two listboxes if this one is full.

        self.UI_components.append(lb1)
        # now add the Sidebar
        self.UI_components.append(TextBox(self.screen, (0,0,200), (375, 72, self.width-375, self.height-72), 'Sidebar'))


    def on_clicked(self, button, click_pos_x, click_pos_y):
        pass

    def close(self):
        pass

    def open(self):
        # needs a list of recipes the player knows. should store that in player.known_recipes
        # parse the list keeping favorites at the top and un-craftable at the bottom.
        # build this menu from UI components
        pass
