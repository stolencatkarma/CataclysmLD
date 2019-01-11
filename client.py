#!/usr/bin/env python3

import argparse
import jsonpickle
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
from src.passhash import hashPassword
from src.character import Character

# load the tileset TODO: support different tilesets.
pyglet.resource.path = [
    "tilesets/Chesthole32/tiles",
    "tilesets/Chesthole32/tiles/background",
    "tilesets/Chesthole32/tiles/monsters",
    "tilesets/Chesthole32/tiles/terrain",
]
for folder in [
    "/gfx/",
    "gfx/inputbox",
    "gfx/background",
    "gfx/scrollbox/vbar/backward",
    "gfx/scrollbox/vbar/forward",
    "gfx/scrollbox/vbar/decoration",
    "gfx/scrollbox/vbar/grip",
    "gfx/scrollbox/frame/decoration",
]:
    pyglet.resource.path.append(folder)
    print("Loaded gfx folder", folder)
pyglet.resource.reindex()

from Mastermind._mm_client import MastermindClientTCP

from src.action import Action
from src.blueprint import Blueprint
from src.command import Command
from src.item import Item, ItemManager
from src.character import Character
from src.position import Position
from src.recipe import Recipe, RecipeManager
from src.tileManager import TileManager
from src.worldmap import Worldmap


class CustomBackground(glooey.Background):
    custom_center = pyglet.resource.texture("center.png")
    custom_top = pyglet.resource.texture("top.png")
    custom_bottom = pyglet.resource.texture("bottom.png")
    custom_left = pyglet.resource.texture("left.png")
    custom_right = pyglet.resource.texture("right.png")
    custom_top_left = pyglet.resource.image("top_left.png")
    custom_top_right = pyglet.resource.image("top_right.png")
    custom_bottom_left = pyglet.resource.image("bottom_left.png")
    custom_bottom_right = pyglet.resource.image("bottom_right.png")


class InputBox(glooey.Form):
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


class CharacterGenerationInputBox(glooey.Form):
    custom_alignment = "center"
    custom_height_hint = 12

    class Label(glooey.EditableLabel):
        custom_font_size = 12
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


class CustomScrollBox(glooey.ScrollBox):
    # custom_alignment = 'center'
    custom_size_hint = 300, 200
    custom_height_hint = 200

    class Frame(glooey.Frame):
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


class CharacterGenerationScrollBox(glooey.ScrollBox):
    custom_alignment = "center"
    custom_size_hint = 200, 300
    custom_height_hint = 200

    class Frame(glooey.Frame):
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


class ConnectButton(glooey.Button):
    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 14

    Label = MyLabel
    # custom_alignment = 'fill'
    # custom_height_hint = 12

    class Base(glooey.Background):
        custom_color = "#204a87"

    class Over(glooey.Background):
        custom_color = "#3465a4"

    class Down(glooey.Background):
        custom_color = "#729fcf"

    def __init__(self, text):
        super().__init__(text)


class CharacterListButton(glooey.Button):
    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 14

    Label = MyLabel
    # custom_alignment = 'fill'
    custom_height_hint = 12

    class Base(glooey.Background):
        custom_color = "#204a87"

    class Over(glooey.Background):
        custom_color = "#3465a4"

    class Down(glooey.Background):
        custom_color = "#729fcf"

    def __init__(self, text):
        super().__init__(text)


class CreateNewCharacterButton(glooey.Button):
    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 14

    Label = MyLabel
    # custom_alignment = 'fill'
    custom_height_hint = 12

    class Base(glooey.Background):
        custom_color = "#204a87"

    class Over(glooey.Background):
        custom_color = "#3465a4"

    class Down(glooey.Background):
        custom_color = "#729fcf"

    def __init__(self):
        super().__init__("Create a Character")


class CharacterGenButton(glooey.Button):
    custom_padding = 8

    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 12
        custom_padding = 2

    Label = MyLabel
    # custom_alignment = 'fill'
    custom_height_hint = 12

    class Base(glooey.Background):
        custom_color = "#204a87"

    class Over(glooey.Background):
        custom_color = "#3465a4"

    class Down(glooey.Background):
        custom_color = "#729fcf"

    def __init__(self, text):
        super().__init__(text)


class ServerListButton(glooey.Button):
    class MyLabel(glooey.Label):
        custom_color = "#babdb6"
        custom_font_size = 12

    Label = MyLabel
    # custom_alignment = 'fill'
    custom_height_hint = 12

    class Base(glooey.Background):
        custom_color = "#3465a4"

    class Over(glooey.Background):
        custom_color = "#204a87"

    class Down(glooey.Background):
        custom_color = "#729fcf"

    def __init__(self, text):
        super().__init__(text)


# the first Window the user sees.
class LoginWindow(glooey.containers.VBox):
    def __init__(self):
        super().__init__()

        self.username = InputBox()
        self.password = InputBox()

        self.password.push_handlers(
            on_unfocus=lambda w: print(f"password: ***************")
        )

        self.serverIP = InputBox()
        self.serverPort = InputBox()
        self.serverIP.push_handlers(on_unfocus=lambda w: print(f"serverIP: '{w.text}'"))
        self.serverPort.push_handlers(
            on_unfocus=lambda w: print(f"serverPort: '{w.text}'")
        )

        self.grid = glooey.Grid(0, 0, 0, 0)
        self.padding = 16

        self.titleLabel = glooey.Label("Cataclysm: Looming Darkness")

        self.grid[0, 1] = self.titleLabel

        self.grid[1, 0] = glooey.Label("Username:")

        self.grid[1, 1] = self.username
        self.grid[3, 0] = glooey.Label("password:")
        self.grid[3, 1] = self.password
        self.grid[4, 0] = glooey.Label("Server IP:")
        self.grid[4, 1] = self.serverIP
        self.grid[5, 0] = glooey.Label("Server Port:")
        self.grid[5, 1] = self.serverPort

        with open("client.json") as f:
            client_data = json.load(f)

        self.username.text = client_data["username"]
        self.password.text = client_data["password"]
        self.serverList = client_data["serverList"]

        connectButton = ConnectButton("Connect")
        self.grid[6, 1] = connectButton

        serverListScrollBox = CustomScrollBox()
        serverListScrollBox.size_hint = 100, 100
        vbox_for_serverlist = glooey.VBox(0)
        for server in self.serverList:
            _button = ServerListButton(server)
            # sets the active server to the one you press.
            _button.push_handlers(on_click=self.set_host_and_port_InputBoxes)
            vbox_for_serverlist.add(_button)
        serverListScrollBox.add(vbox_for_serverlist)
        self.grid[6, 0] = serverListScrollBox

        self.add(self.grid)

        # self.grid.debug_drawing_problems()
        # self.grid.debug_placement_problems()

    def set_host_and_port_InputBoxes(self, server_and_port):
        self.serverIP.text = server_and_port.text.split(":")[0]
        self.serverPort.text = server_and_port.text.split(":")[1]


# The window that let's the user select a character or leads to a Window where you can generate a new one.
class CharacterSelectWindow(glooey.containers.VBox):
    def __init__(self, list_of_characters):
        super().__init__()

        self.grid = glooey.Grid(0, 0, 0, 0)
        self.grid.padding = 16

        self.titleLabel = glooey.Label("Please Select or Create a Character.")

        self.grid[0, 1] = self.titleLabel

        self.add(self.grid)

        self.fill_character_list(list_of_characters)

    def fill_character_list(self, list_of_characters):
        characterListScrollBox = CustomScrollBox()
        characterListScrollBox.size_hint = 100, 100
        self.vbox_for_characterlist = glooey.VBox(0)
        # add the create new character button first then add the list the of characters for the user.
        self.create_button = CreateNewCharacterButton()

        # add the first button
        self.vbox_for_characterlist.add(self.create_button)
        # add the character buttons
        for character in list_of_characters:
            print(character)
            _decoded = jsonpickle.decode(character, keys=True)
            _button = CharacterListButton(_decoded["name"])
            _button.push_handlers(on_click=self.select_character)
            self.vbox_for_characterlist.add(_button)

        characterListScrollBox.add(self.vbox_for_characterlist)
        self.grid[2, 0] = characterListScrollBox

    def select_character(self, dt):
        # need to setup the MainWindow and show it.
        pass


class CharacterGenerationWindow(glooey.containers.VBox):
    custom_padding = 16
    # minimum size
    custom_default_cell_size = 2
    # has 6 unchanging buttons on top which control which screen the player is on for genning
    # screens are 'scenario', 'profession', 'traits', 'stats', 'skills', 'description'
    def __init__(self):
        super().__init__()

        # our points available to spend on traits
        self.points = 8
        

        _screens = [
            "scenario",
            "profession",
            "traits",
            "stats",
            "skills",
            "description",
        ]

        # the row of buttons on top. responsible for switching the subcontext below points left.
        top_buttons = glooey.HBox(0)

        # finish_button is self. so we can access it easier.
        self.finish_button = ConnectButton("Commit")

        for screen in _screens:
            _button = CharacterGenButton(screen)
            top_buttons.add(_button)

        top_buttons.add(self.finish_button)

        self.add(top_buttons)

        # now add the remaining points label
        points_box = glooey.HBox()
        pointsLabel = glooey.Label("Points Left:")
        points_box.add(pointsLabel)

        self.pointsLeftLabel = glooey.Label(str(self.points))
        points_box.add(self.pointsLeftLabel)
        self.add(points_box)

        # our main_frame will be a single use container that we replace the contents of.
        self.main_frame = glooey.containers.Bin()
        self.main_frame.custom_padding = 8
        self.main_frame.add(self.descriptionTab())
        self.add(self.main_frame)

        self.name = ''
        self.gender = ''

    class descriptionTab(glooey.containers.Grid):
        def __init__(self):
            super().__init__(0, 0, 0, 0)

            self[0, 0] = glooey.Label("Name:")
            self[0, 1] = CharacterGenerationInputBox()
            self[0, 2] = glooey.Label("Gender:")
            self[0, 3] = CharacterGenerationInputBox()
            self[1, 0] = glooey.Label("Profession:")
            self[1, 1] = glooey.Label("Default")
            self[1, 2] = glooey.Label("Scenario:")
            self[1, 3] = glooey.Label("Evacuee")
            self[2, 0] = glooey.Label("Stats:")
            self[2, 1] = glooey.Label("Traits:")
            self[2, 2] = glooey.Label("Skills:")
            self[3, 0] = CharacterGenerationScrollBox()
            self[3, 1] = CharacterGenerationScrollBox()
            self[3, 2] = CharacterGenerationScrollBox()
        

        # nameLabel -       nameInputBox -          genderLabel -       genderInputBox
        # professionLabel - selectedProfession -    scenarioLabel -     selectedScenario
        # statsLabel -      TraitsLabel -           SkillsLabel
        # statsScrollbox -  TraitsScrollbox -       SkillsScrollBox


# The window after we login with a character. Where the Main game is shown.
class mainWindow(glooey.containers.Stack):
    def __init__(self):
        super().__init__()

        self.chunk_size = (13, 13)  # the only tuple you'll see I swear.

        self.map_grid = glooey.Grid(
            self.chunk_size[0], self.chunk_size[1], 32, 32
        )  # chunk_size + tilemap size
        self.map_grid.set_left_padding(32)  # for the border.
        self.map_grid.set_top_padding(32)

        for i in range(
            self.chunk_size[0]
        ):  # glooey uses x,y for grids from the top left.
            for j in range(self.chunk_size[1]):
                self.map_grid.add(
                    i, j, glooey.images.Image(pyglet.resource.texture("t_grass.png"))
                )  # before we get an update we need to init the map with grass.

        # insert the background into our ordered groups.
        self.insert(CustomBackground(), 0)

        # insert the map_grid into our ordered group.
        self.insert(self.map_grid, 1)

        # TODO: lerp the positions of creatures from one frame to the next.
        # self.old_map = self.localmap

        # our keep-alive event. without this the server would disconnect if we don't send data within the timeout for the server. (usually 60 seconds)
        # clock.schedule_interval(self.ping, 30.0)

    def ping(self, dt):
        command = Command(client.character.name, "ping")
        client.send(command)

    def find_character_in_localmap(self):
        for tile in self.localmap:
            if tile["creature"] is not None:
                if tile["creature"].name == self.character.name:
                    return tile["creature"]
        else:
            print("couldn't find character")

    def convert_chunks_to_localmap(self, list_of_chunks):
        tiles = []
        for chunk in list_of_chunks:
            for tile in chunk.tiles:
                tiles.insert(len(tiles), tile)
        return tiles

    def lerp(self, start, end, t):
        return start + t * (end - start)

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
            points.append(self.lerp_point(p0, p1, step / diagonal_distance))
        return points  # so now we have a set of points along a line.

    def trim_localmap(self, origin_position, radius=10):
        # origin_position = origin_position # store the player position for fov origin
        # convert chunks to grid
        level = defaultdict(dict)
        for tile in self.localmap[:]:  # we only need the tiles around radius.
            if (
                int(tile["position"].x) < origin_position.x - radius
                or int(tile["position"].x) > origin_position.x + radius + 1
            ):
                self.localmap.remove(tile)
            elif (
                int(tile["position"].y) < origin_position.y - radius
                or int(tile["position"].y) > origin_position.y + radius + 1
            ):
                self.localmap.remove(tile)
            else:
                level[str(tile["position"].x)][str(tile["position"].y)] = tile[
                    "terrain"
                ].impassable  # so either remove a tile or figure out if it's impassable.

        # draw a line to each edge of the viewport using grid_edges
        # x's include top row and bottom rows, y's include min and max of viewport.
        grid_edges = []
        # now we have a level grid. let's get our edges so we can plot lines from origin to edge.
        for x in range(origin_position.x - radius, origin_position.x + radius + 1):  # X
            grid_edges.append((x, origin_position.y - radius))
            grid_edges.append((x, origin_position.y + radius))
        for y in range(origin_position.y - radius, origin_position.y + radius + 1):  # Y
            grid_edges.append((origin_position.x - radius, y))
            grid_edges.append((origin_position.x + radius, y))
        # print('grid_edges: ' + str(len(grid_edges)))

        tiles_to_keep = []
        # now we need to remove tiles which are out of our field of view.
        for destination in grid_edges:
            for point in self.line((origin_position.x, origin_position.y), destination):
                if level[str(point[0])][str(point[1])] == True:  # (impassable)
                    tiles_to_keep.append(
                        point
                    )  # do this to keep the blocking wall visible.
                    break  # hit a wall. move on to the next ray.
                else:
                    tiles_to_keep.append(point)

        for tiles in self.localmap[:]:  # iterate a copy to remove correctly.
            for point in tiles_to_keep:
                if tiles["position"].x == point[0] and tiles["position"].y == point[1]:
                    break
            else:
                self.localmap.remove(tiles)

    def update_map_for_position(self, position):
        if self.localmap is not None:
            # our map_grid is 13x13 but our localmap contains 13*3 x 13*3 tiles worth of chunks so we need
            # to draw the viewport from the position only 13x13
            position = self.convert_position_to_local_coords(position)
            # first set terrain to the terrain image
            for tile in self.localmap:
                _pos = self.convert_position_to_local_coords(
                    tile["position"]
                )  # (0-38, 0-38)
                x = _pos.x - position.x + 6
                y = _pos.y - position.y + 6
                if x < 0 or x > 12:
                    continue
                if y < 0 or y > 12:
                    continue
                self.map_grid[x, y].set_image(
                    pyglet.resource.texture(tile["terrain"].ident + ".png")
                )  # must be (0-12, 0-12)

                # then overlay furniture on that.
                if tile["furniture"] is not None:
                    self.map_grid[x, y].set_image(
                        pyglet.resource.texture(tile["furniture"].ident + ".png")
                    )

                # then overlay items on that.
                if tile["items"] is not None and len(tile["items"]) > 0:
                    self.map_grid[x, y].set_image(
                        pyglet.resource.texture(tile["items"][0].ident + ".png")
                    )  # just show the first item

                # then overlay creatures on that.
                if tile["creature"] is not None:
                    self.map_grid[x, y].set_image(
                        pyglet.resource.texture(tile["creature"].tile_ident + ".png")
                    )

            # print("FPS:", pyglet.clock.get_fps())

    def convert_position_to_local_coords(self, position):
        # local coordinates are always from (0,0) to (chunk.size[1] * 3 , chunk.size[0] * 3)
        # and must return a position within that size.
        x = position.x
        y = position.y
        z = position.z

        while x >= self.chunk_size[0] * 3:
            x = x - self.chunk_size[0] * 3
        while y >= self.chunk_size[1] * 3:
            y = y - self.chunk_size[1] * 3

        return Position(x, y, z)

    def draw_view_at_position(self, draw_position):
        self.trim_localmap(draw_position)  # update field of view and lighting

        # at this point the localmap should've been trimmed of unseeable tiles. draw what's left at position.
        for tile in self.localmap:  # draw the localmap for the controlling player.
            terrain = tile["terrain"]
            position = tile["position"]  # Position(x, y, z)
            creature = tile["creature"]  # Creature()
            furniture = tile["furniture"]  # Furniture()
            items = tile["items"]  # list [] of Item()
            light_intensity = tile["lumens"]

            fg = self.TileManager.TILE_TYPES[terrain.ident]["fg"]
            bg = self.TileManager.TILE_TYPES[terrain.ident]["bg"]

            x = (
                draw_position.x - position.x - (self.chunk_size[0] // 2)
            )  # offset to put position in middle of viewport
            y = (
                draw_position.y - position.y - (self.chunk_size[1] // 2)
            )  # offset to put position in middle of viewport

            """# first blit terrain
        
            # then blit furniture
        

            # then blit items (if there is a pile of items check and see if any are blueprints. if so show those.)
            if(len(items) > 0):
                for item in items:
                    # always show blueprints on top.
                else:
                    # only display the first item 
        
            # then blit vehicles

            # then blit player and creatures and monsters (all creature types)
            """
            # darken based on lumen level of the tile
            # light_intensity # 10 is max light level although lumen level may be higher.
            # light_intensity = min(int((255-(light_intensity*25))/3), 255)
            # light_intensity = max(light_intensity, 0)
            # self.screen.fill((light_intensity, light_intensity, light_intensity), rect=(x*24, y*24, 24, 24), special_flags=pygame.BLEND_SUB)

            # render debug text

            # then blit weather. Weather is the only thing above players and creatures.
            # TODO: blit weather

    def open_crafting_menu(self):
        list_of_known_recipes = []
        for (
            key,
            value,
        ) in (
            self.RecipeManager.RECIPE_TYPES.items()
        ):  # TODO: Don't just add them all. Pull them from creature.known_recipes
            list_of_known_recipes.append(value)

    def open_movement_menu(self, pos, tile):
        # _command = Command(client.character.name, 'calculated_move', (tile['position'].x, tile['position'].y, tile['position'].z))
        # send calculated_move action to server and give it the position of the tile we clicked.
        # return _command
        pass

    def open_super_menu(self, pos, tile):
        pass

    def open_blueprint_menu(self, pos, tile):
        # blueprint_menu = Blueprint_Menu(self.screen, (0, 0, 400, 496), self.FontManager, self.TileManager)
        pass

    def open_equipment_menu(self):
        # equipment_menu = Equipment_Menu(self.screen, (0, 0, 400, 496), self.FontManager, self.TileManager, self.character.body_parts)
        pass

    def open_items_on_ground(self, pos, tile):
        # _command = Command(self.character.name, 'move_item_to_player_storage', (tile['position'].x, tile['position'].y, tile['position'].z, item.ident)) # ask the server to pickup the item by ident. #TODO: is there a better way to pass it to the server without opening ourselves up to cheating?
        # return _command
        pass


class Client(MastermindClientTCP):  # extends MastermindClientTCP
    def __init__(self):
        self.state = "login"  # character_select, character_gen, main
        MastermindClientTCP.__init__(self)

        self.window = pyglet.window.Window(896, 498)
        self.client_name = ''

        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

        self.gui = glooey.Gui(self.window)

        self.bg = glooey.Background()
        self.bg.set_appearance(
            center=pyglet.resource.texture("center.png"),
            top=pyglet.resource.texture("top.png"),
            bottom=pyglet.resource.texture("bottom.png"),
            left=pyglet.resource.texture("left.png"),
            right=pyglet.resource.texture("right.png"),
            top_left=pyglet.resource.texture("top_left.png"),
            top_right=pyglet.resource.texture("top_right.png"),
            bottom_left=pyglet.resource.texture("bottom_left.png"),
            bottom_right=pyglet.resource.texture("bottom_right.png"),
        )

        self.gui.add(self.bg)

        self.TileManager = TileManager
        self.ItemManager = ItemManager
        self.RecipeManager = RecipeManager

        # TODO: make new hotbar in pyglet.
        self.hotbars = []

        self.LoginWindow = LoginWindow()
        self.LoginWindow.grid[6, 1].push_handlers(on_click=self.login)  # Connect Button

        self.gui.add(self.LoginWindow)

        self.character = None
        self.localmap = None

        # init but don't show the window
        self.mainWindow = mainWindow

    # if we recieve an update from the server process it. do this first.
    # We always start out at the login window.
    # once we recieve a list of characters SWITCH to the character select view.
    # once the user selects a character ask the server to login into the world with it.
    # once we recieve a world state SWITCH to the mainWindow. client.character and localmap should be filled.
    def check_messages_from_server(self, dt):
        # commands recieved while in the login window
        next_update = client.receive(False)
        if self.state == "login":
            # we recieved a message from the server. let's process it.
            if next_update is not None:
                print("--next_update in login--")
                print(type(next_update))
                if isinstance(next_update, list):
                    # list of characters.
                    print("list:", next_update)
                    # open the character select screen.
                    self.gui.clear()
                    self.gui.add(CustomBackground())
                    self.CharacterSelectWindow = CharacterSelectWindow(next_update)
                    self.CharacterSelectWindow.create_button.push_handlers(
                        on_click=self.create_new_character
                    )
                    self.gui.add(self.CharacterSelectWindow)
                    self.state = "character_select"

                if isinstance(next_update, str):
                    if next_update == "disconnect":
                        self.disconnect()
                        return

                if isinstance(next_update, str):
                    print(next_update)
                    # server sent salt
                    _hashedPW = hashPassword(
                        self.LoginWindow.password.text, next_update
                    )
                    command = Command(
                        self.LoginWindow.username.text,
                        "hashed_password",
                        [str(_hashedPW)],
                    )
                    # send back hashed password.
                    self.send(command)

        if self.state == "character_select":
            if next_update is not None:
                print("--next_update in character_select--")
                if isinstance(next_update, list):
                    # list of characters.
                    print("list:", next_update)
                    # re-fresh the character select screen.
                    self.gui.clear()

                    self.gui.add(CustomBackground())
                    self.CharacterSelectWindow = CharacterSelectWindow(next_update)
                    self.CharacterSelectWindow.create_button.push_handlers(
                        on_click=self.create_new_character
                    )
                    self.gui.add(self.CharacterSelectWindow)
                    for button in self.CharacterSelectWindow.vbox_for_characterlist:
                        if button.text != "Create a Character":
                            button.push_handlers(
                                on_click=lambda w: self.choose_character(w.text)
                            )

        if self.state == "main":
            self.gui.clear()
            self.gui.add(self.mainWindow)
            print("--in state main--")
            if next_update is not None:
                print("next_update in main", next_update)
                # we recieved a localmap from the server.

        if self.state == "character_gen":
            if next_update is not None:
                print("--next_update in character_gen--")
                # print(next_update)

    def choose_character(self, name):
        self.state = "main"
        command = Command(self.client_name, "choose_character", [name])
        self.send(command)

    def create_new_character(self, dt):
        # switch to the character generation screen
        self.gui.clear()

        # init a blank character for us to send.
        self.character = Character()

        self.gui.add(CustomBackground())
        self.CharacterGenerationWindow = CharacterGenerationWindow()
        self.CharacterGenerationWindow.finish_button.push_handlers(
            on_click=self.send_completed_character
        )

        self.gui.add(self.CharacterGenerationWindow)
        self.state = "character_gen"

    def send_completed_character(self, dt):
        # gather up all the character info from the chargen window and send it. the 'commit' button

        self.character.name = self.CharacterGenerationWindow.main_frame.get_child()[0, 1].text
        self.character.gender = self.CharacterGenerationWindow.main_frame.get_child()[0, 3].text
        _data = jsonpickle.encode(self.character)

        # set this before sending the command to keep things in order.
        self.state = "character_select"

        command = Command(self.client_name, "completed_character", [_data])
        self.send(command)
        # go back to the charcterSelectWindow and update it with the new character and let them select it.

    def login(self, dt):
        # we'll do the below to login and recieve a list of characters.
        self.connect(
            self.LoginWindow.serverIP.text, int(self.LoginWindow.serverPort.text)
        )

        # set our client_name for future sending.
        self.client_name = self.LoginWindow.username.text 
        
        command = Command(self.LoginWindow.username.text, "login", ["noargs"])
        self.send(command)
        # -------------------------------------------------------
        clock.schedule_interval(self.check_messages_from_server, 0.1)

    # our keep-alive event. without this the server would disconnect if we don't send data within the timeout for the server. (usually 60 seconds)
    # clock.schedule_interval(self.ping, 30.0)
    def ping(self, dt):
        command = Command(self.username, "ping")
        client.send(command)


#
#   if we start a client directly
#
if __name__ == "__main__":

    client = Client()

    pyglet.app.event_loop.run()  # main event loop starts here.

