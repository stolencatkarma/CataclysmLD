# this was a small side project to see how feasible a isometric mapedito would look and run. 
# it won't be part of the project anytime soon but contains a lot of good code for glooey UI components.
# that's why it's included for now - Andrew 1-11-2019

import json
import math
import os
import sys
import time
import pickle

import glooey
import pyglet
from pyglet import clock
from pyglet.window import key as KEY

from src.command import Command
from src.item import Item, ItemManager
from src.position import Position
from src.recipe import Recipe, RecipeManager
from src.tilemanager import TileManager
from src.worldmap import Plane, Chunk

# load all the resources we can use and index them.

for folder in [
    # load tileset resources
    "tiles/grassland/bg",
    "tiles/grassland/fg",
    "tiles/grassland/objects",
    "tiles/global",
    "tiles/items",
    "tiles/containers"
    "tiles/monsters",
    "tiles/terrain",

    # load UI graphicss
    "gfx/inputbox",
    "gfx/background",
    "gfx/scrollbox/vbar/backward",
    "gfx/scrollbox/vbar/forward",
    "gfx/scrollbox/vbar/decoration",
    "gfx/scrollbox/vbar/grip",
    "gfx/scrollbox/frame/decoration",
]:
    pyglet.resource.path.append(folder)
    print("Loaded resource folder", folder)

pyglet.resource.reindex()


class CustomBackground(glooey.Background):
    custom_center = pyglet.resource.texture('center.png')
    custom_top = pyglet.resource.texture('top.png')
    custom_bottom = pyglet.resource.texture('bottom.png')
    custom_left = pyglet.resource.texture('left.png')
    custom_right = pyglet.resource.texture('right.png')
    custom_top_left = pyglet.resource.image('top_left.png')
    custom_top_right = pyglet.resource.image('top_right.png')
    custom_bottom_left = pyglet.resource.image('bottom_left.png')
    custom_bottom_right = pyglet.resource.image('bottom_right.png')


class PaletteButton(glooey.Button):
    custom_padding = 8

    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 10
        custom_vert_padding = 8
        custom_horz_padding = 8

    Label = MyLabel
    custom_alignment = 'center'

    Base = CustomBackground

    class Over(glooey.Background):
        custom_color = "#3465a4"

    class Down(glooey.Background):
        custom_color = "#729fcff"

    def __init__(self, text, image=None):
        super().__init__(text, image)


class MapEditorButton(glooey.Button):
    custom_padding = 8

    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 14
        custom_vert_padding = 16
        custom_horz_padding = 8

    Label = MyLabel
    custom_alignment = 'center'

    Base = CustomBackground

    class Over(glooey.Background):
        custom_color = "#3465a4"

    class Down(glooey.Background):
        custom_color = "#729fcff"

    def __init__(self, text, image=None):
        super().__init__(text, image)


class CreatureButton(glooey.Button):
    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 14
        custom_vert_padding = 40
        custom_horz_padding = 16

    Label = MyLabel
    custom_alignment = 'center'
    custom_padding = 8

    Base = CustomBackground

    class Over(glooey.Background):
        custom_color = "#3465a4"

    class Down(glooey.Background):
        custom_color = "#729fcff"

    def __init__(self, text, image=None):
        super().__init__(text, image)


class LumensButton(glooey.Button):
    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 14
        custom_vert_padding = 32
        custom_horz_padding = 32

    Label = MyLabel
    custom_alignment = 'center'

    Base = CustomBackground

    class Over(glooey.Background):
        custom_color = "#3465a4"

    class Down(glooey.Background):
        custom_color = "#729fcff"

    def __init__(self, text, image=None):
        super().__init__(text, image)


class Menu_Bar(glooey.HBox):
    custom_alignment = 'top'
    custom_top_padding = 16

    def __init__(self):
        super().__init__()
        # New, Open, Save, SaveAs, Editing: Foreground or Background
        self.menu_new = MapEditorButton('New')
        self.add(self.menu_new)

        self.menu_open = MapEditorButton('Open')
        self.add(self.menu_open)

        self.menu_save = MapEditorButton('Save')
        self.add(self.menu_save)

        self.menu_saveAs = MapEditorButton('SaveAs')
        self.add(self.menu_saveAs)

        self.menu_editing = MapEditorButton('Editing: Foreground')
        self.add(self.menu_editing)


class Palette_Bar(glooey.HBox):
    custom_alignment = 'bottom'

    def __init__(self):
        super().__init__()
        self.list_of_palette_buttons = list()
        # 1 to 9 then 0 like a keyboard
        for i in range(1, 10):
            _button = PaletteButton(str(i), pyglet.resource.image('blank.png'))
            self.list_of_palette_buttons.append(_button)
        _button = PaletteButton(str(0), pyglet.resource.image('blank.png'))
        self.list_of_palette_buttons.append(_button)
        for button in self.list_of_palette_buttons:
            self.add(button)


class CustomScrollBox(glooey.ScrollBox):
    # custom_alignment = 'center'
    custom_size_hint = 200, 200
    # custom_height_hint = 200

    class Frame(glooey.Frame):
        custom_padding = 8

        class Decoration(glooey.Background):
            custom_center = pyglet.resource.texture("scrollbox_center.png")

        class Box(glooey.Bin):
            custom_horz_padding = 2

    class VBar(glooey.VScrollBar):
        class Decoration(glooey.Background):
            custom_top = pyglet.resource.image("bar_top.png")
            custom_center = pyglet.resource.texture("bar_vert.png")
            custom_bottom = pyglet.resource.image("bar_bottom.png")

        class Forward(glooey.Button):
            class Base(glooey.Image):
                custom_image = pyglet.resource.image("forward_base.png")

            class Over(glooey.Image):
                custom_image = pyglet.resource.image("forward_over.png")

            class Down(glooey.Image):
                custom_image = pyglet.resource.image("forward_down.png")

        class Backward(glooey.Button):
            class Base(glooey.Image):
                custom_image = pyglet.resource.image("backward_base.png")

            class Over(glooey.Image):
                custom_image = pyglet.resource.image("backward_over.png")

            class Down(glooey.Image):
                custom_image = pyglet.resource.image("backward_down.png")

        class Grip(glooey.ButtonScrollGrip):
            class Base(glooey.Background):
                custom_top = pyglet.resource.image("grip_top_base.png")
                custom_center = pyglet.resource.texture("grip_vert_base.png")
                custom_bottom = pyglet.resource.image("grip_bottom_base.png")

            class Over(glooey.Background):
                custom_top = pyglet.resource.image("grip_top_over.png")
                custom_center = pyglet.resource.texture("grip_vert_over.png")
                custom_bottom = pyglet.resource.image("grip_bottom_over.png")

            class Down(glooey.Background):
                custom_top = pyglet.resource.image("grip_top_down.png")
                custom_center = pyglet.resource.texture("grip_vert_down.png")
                custom_bottom = pyglet.resource.image("grip_bottom_down.png")


class ScrollBoxListButton(glooey.Button):
    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 12
        custom_alignment = 'center'

    Label = MyLabel
    custom_alignment = 'fill'
    custom_height_hint = 12

    Base = CustomBackground

    class Over(glooey.Background):
        custom_color = "#204a87"

    class Down(glooey.Background):
        custom_color = "#729fcff"

    def __init__(self, text):
        super().__init__(text)


class MapEditorLabel(glooey.Button):
    custom_alignment = "center"

    class MyLabel(glooey.Label):
        custom_alignment = 'center'
        custom_color = "#babdb6"
        custom_font_size = 12
        custom_padding = 4

    Label = MyLabel

    class Base(glooey.Background):
        custom_center = pyglet.resource.texture("form_center.png")
        custom_left = pyglet.resource.image("form_left.png")
        custom_right = pyglet.resource.image("form_right.png")

    def __init__(self, text):
        super().__init__(text=text)


class Tile_Editing(glooey.Frame):
    custom_alignment = 'bottom right'
    custom_vert_padding = 32

    def __init__(self):
        super().__init__()
        self.grid = glooey.Grid(0, 0, 0, 0)
        self.grid.cell_alignment = 'right'
        # create selected tile window
        # - bg image, fg image
        # - creature - None or One
        # - items - empty list or list with items.
        # - lumens - integer of brightness 0-15000 (15,000 is full daylight)
        # - exit - None or Exit()
        # - flags - dict of flag:value pairs.
        bg_label = MapEditorLabel('Tile Background')
        self.grid[0, 0] = bg_label

        self.bg_button = MapEditorButton(
            '', pyglet.resource.image('blank.png'))
        self.grid[0, 1] = self.bg_button

        fg_label = MapEditorLabel('Tile Foreground')
        self.grid[1, 0] = fg_label

        self.fg_button = MapEditorButton(
            '', pyglet.resource.image('blank.png'))
        self.grid[1, 1] = self.fg_button

        creature_label = MapEditorLabel('Creature')
        self.grid[2, 0] = creature_label

        self.creature_button = CreatureButton(
            '', pyglet.resource.image('blank.png'))
        self.grid[2, 1] = self.creature_button

        lumens_label = MapEditorLabel('Lumens')
        self.grid[3, 0] = lumens_label

        self.lumens_button = LumensButton(
            '', pyglet.resource.image('blank.png'))
        self.grid[3, 1] = self.lumens_button

        exit_label = MapEditorLabel('Exit')
        self.grid[4, 0] = exit_label

        self.exit_button = MapEditorButton(
            '', pyglet.resource.image('blank.png'))
        self.grid[4, 1] = self.exit_button

        items_label = MapEditorLabel('Items')
        self.grid[5, 0] = items_label

        flags_label = MapEditorLabel('Flags')
        self.grid[5, 1] = flags_label

        self.items_list = CustomScrollBox()
        _button = ScrollBoxListButton('Add')
        self.items_list.add(_button)
        self.grid[6, 0] = self.items_list

        self.flags_list = CustomScrollBox()
        _button = ScrollBoxListButton('Add')
        self.flags_list.add(_button)
        # add a button to add a item to this list.
        self.grid[6, 1] = self.flags_list

        self.add(self.grid)


class MapTile(glooey.Image):
    # because they way they stack make height and width
    custom_height_hint = 16
    custom_width_hint = 32

    def __init__(self, x, y, image):
        super().__init__(pyglet.resource.image(image))
        self.x = x
        self.y = y
        self.terrain = 't_grass'
        self.creature = None
        self.items = list()
        self.lumens = 1
        self.exit = None
        self.flags = dict()

        @self.event
        def on_mouse_release(x, y, button, modifiers):
            # trim presses outside the trapezoidal area.
            if(abs(x - self.get_rect().center_x) > 16):
                return
            if(abs(y - self.get_rect().center_y) > 16):
                return
            # did we click a tile? then select it. if not ignore.
            print(self.x, self.y)
            self.get_parent().selected_tile = self
            print(self.get_parent().selected_tile)


class GenericButton(glooey.Button):
    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 14
        custom_vert_padding = 8
        custom_horz_padding = 8

    Label = MyLabel


class InputForm(glooey.Form):
    custom_alignment = "center"
    custom_height_hint = 12

    class Label(glooey.EditableLabel):
        custom_font_size = 10
        custom_color = "#b9ad86"
        custom_alignment = "center"
        custom_horz_padding = 4
        custom_top_padding = 2
        custom_width_hint = 200
        custom_height_hint = 12
        # TODO: import string; def format_alpha(entered_string): return "".join(char for char in entered_string if char in string.ascii_letters) # only allow valid non-space asicii

    class Base(glooey.Background):
        custom_center = pyglet.resource.texture("form_center.png")
        custom_left = pyglet.resource.image("form_left.png")
        custom_right = pyglet.resource.image("form_right.png")


class YesNoDialog(glooey.YesNoDialog):
    custom_alignment = "center"
    custom_height_hint = 12

    Decoration = CustomBackground

    class Box(glooey.Grid):
        custom_right_padding = 14
        custom_top_padding = 14
        custom_left_padding = 17
        custom_bottom_padding = 17
        custom_cell_padding = 9

    class Buttons(glooey.HBox):
        custom_cell_padding = 3

    class YesButton(GenericButton):
        custom_text = 'Ok'

    class NoButton(GenericButton):
        custom_text = 'Cancel'


# maps are loaded as planes
# on load load the whole map directory.
# move chunk postions with wasd
class mainWindow(glooey.containers.Stack):
    def __init__(self):
        super().__init__()
        self.tile_half_width, self.tile_half_height = 32, 16

        # selected tile to load into the TileEditor()
        self.selected_tile = None

        # selected palette brush
        self.selected_brush = None

        # are we editing background or foreground tiles.
        self.editing = 'foreground'

        # folder_name is the folder that all the map chunks get saved under.
        self.folder_name = 'new'

        # dictionary of chunks by '0_0' key
        self.plane = None

        # the current chunk of the map we are editing.
        self.chunk_x = 0
        self.chunk_y = 0

        # size in x,y (0-24)
        self.chunk_size = (25, 25)
        self.bg_map_grid = None
        self.fg_map_grid = None
        self.bg_dict = dict()
        self.fg_dict = dict()
        self.reset_bg_and_fg_grids()

        # insert our custom Background into an OrderedGroup
        self.insert(CustomBackground(), 0)

        # insert mapgrids into our ordered groups.
        self.insert(self.bg_map_grid, 1)
        self.insert(self.fg_map_grid, 2)

        # only propagate mouse events to the front or back depends on what's selected.
        self.bg_map_grid.propagate_mouse_events = False
        self.fg_map_grid.propagate_mouse_events = True

        # Menu Bar
        # New, Open, Save, SaveAs, Editing: Foreground or Background
        self.menu_bar = Menu_Bar()
        self.insert(self.menu_bar, 3)
        self.menu_bar.menu_new.push_handlers(on_click=self.click_menu_new)
        self.menu_bar.menu_open.push_handlers(on_click=self.click_menu_open)
        self.menu_bar.menu_save.push_handlers(on_click=self.click_menu_save)
        self.menu_bar.menu_saveAs.push_handlers(
            on_click=self.click_menu_saveAs)
        self.menu_bar.menu_editing.push_handlers(on_click=self.toggle_editing)

        # create selected tile window
        tile_editing = Tile_Editing()
        self.insert(tile_editing, 3)

        self.palette_bar = Palette_Bar()
        self.insert(self.palette_bar, 3)

        # create last used tiles window 2*64 wide 5*32 tall
        # list of 10 tiles in a 2x5 grid that gets updated when you select a tile_type

    def reset_bg_and_fg_grids(self):
        self.bg_map_grid = glooey.Board()
        # self.chunk_size[0], self.chunk_size[1], 32, 64)
        self.fg_map_grid = glooey.Board()

        for i in range(self.chunk_size[0]):
            for j in range(self.chunk_size[1]):
                # before update we need to init the map with grass.
                # 0,0 = tile_half_width, tile_half_height
                # 2,1 = 64, 16

                x = 808 - self.tile_half_width + \
                    ((i * self.tile_half_width) - (j * self.tile_half_width))
                y = 912 - self.tile_half_height - \
                    ((i * self.tile_half_height) + (j * self.tile_half_height))
                # print('trying',x,y)
                bg_mp = MapTile(i, j, 't_grass.png')
                # can't be none so show transparent tile.
                fg_mp = MapTile(i, j, 'blank.png')

                self.bg_map_grid.add(
                    widget=bg_mp, rect=glooey.Rect(x, y, 32, 16))
                self.fg_map_grid.add(
                    widget=fg_mp, rect=glooey.Rect(x, y, 32, 16))
        
        self.plane = Plane(self.folder_name)


    def load_chunk_into_grid(self, x, y):
        # load chunk x,y into the bg and fg_grids
        for tile in self.bg_map_grid._pins:
            print(tile.x, tile.y)

   


    # button handlers
    def toggle_editing(self, editing):
        print(editing)
        if self.editing == 'foreground':
            self.editing = 'background'
            self.menu_bar.menu_editing.text = 'Editing: Background'
            self.bg_map_grid.propagate_mouse_events = True
            self.fg_map_grid.propagate_mouse_events = False
        else:
            self.editing = 'foreground'
            self.menu_bar.menu_editing.text = 'Editing: Foreground'
            self.bg_map_grid.propagate_mouse_events = False
            self.fg_map_grid.propagate_mouse_events = True

    # Menu Items

    def click_menu_new(self, menu_new):
        # wipe out the bg and fg and reset to blank.
        self.reset_bg_and_fg_grids()
        self.folder_name = 'new'

    def click_yes_button(self, text):
        # wipe out the bg and fg and reset to blank.
        self.folder_name = text
        print(self.folder_name)
        # call menu save now that we've set our folder name
        self.click_menu_save()

    def click_menu_saveAs(self, menu_saveAs):
        # use the self.folder_name to save the current map
        self.yesNoDialog = YesNoDialog()
        self.inputForm = InputForm()
        self.yesNoDialog.add(self.inputForm)
        self.yesNoDialog.open(self.get_parent())
        # if this isn't lambda it calls the function on creation.
        self.yesNoDialog.get_yes_button().push_handlers(
            on_click=lambda w: self.click_yes_button(self.inputForm.get_label().get_text()))

    def click_menu_save(self, menu_save):
        # use the self.folder_name to save the current map and directory.
        #  for each chunk
        #     for each bg tile and fg tile write it to folder_name directory.
        self.plane.save()

    def click_menu_open(self, menu_open):
        # open a input box for the user to select a self.folder_name
        self.folderList = CustomScrollBox()
        self.folderList.size_hint = 100, 400
        vbox_for_folderList = glooey.VBox(0)

        for folder in os.listdir('./planes/'):
            _button = GenericButton(folder)
            # sets the active server to the one you press.
            _button.push_handlers(on_click=lambda w: self.click_open_button(w.text))
            vbox_for_folderList.add(_button)
        self.folderList.add(vbox_for_folderList)

        self.yesNoDialog = YesNoDialog()
        self.yesNoDialog.add(self.folderList)
        self.yesNoDialog.open(self.get_parent())
        
        

    def click_open_button(self, text):
        self.folder_name = text
        print(self.folder_name)
        self.plane = Plane(text)
        # load the first chunk into memory 
        self.plane.load(0,0)

    # Palette bar button
    def click_palette_bar_button(self, palette_bar):
        # open a window to select a palette fg or bg or creature.
        pass

    # TileEditing()
    def click_tile_background(self, tile_background):
        # open a new window to select a bg
        pass

    def click_tile_foreground(self, tile_foreground):
        # open a new window to select a fg
        pass

    def click_tile_creature(self, tile_creature):
        # open a new window to select a creature
        pass

    def click_tile_lumens(self, tile_lumens):
        # open a new window to select lumen level
        pass

    def click_tile_exit(self, tile_exit):
        # open a new window to select a plane, chunk, x, and y
        pass

    def click_tile_items_listitem(self, tile_items_listitem):
        # if we click 'add' button open a new window to select an item to add and amount
        # if we click a item we added edit it with option to delete.
        pass

    def click_tile_flags_listitem(self, tile_flags_listitem):
        # if we click 'add' button open a new window to select an flag to add and amount
        # if we click a flag we added edit it with option to delete.
        pass


class MapEditor:
    def __init__(self):
        self.window = pyglet.window.Window(1916, 1010)
        self.window.set_location(0, 32)

        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA,
                              pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

        self.gui = glooey.Gui(self.window)

        self.gui.add(mainWindow())


#
#   if we start a client directly
#
if __name__ == "__main__":

    mapeditor = MapEditor()

    pyglet.app.event_loop.run()  # main event loop starts here.
