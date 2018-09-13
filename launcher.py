import argparse
import json
import math
import os
import sys
import time
import subprocess
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
                                Popup_menu, Super_menu, TextBox, InputBox, CheckBox)
from client import Client

# Purpose: creates a GUI login screen and launches the client with the name, password, and server:port passed to the client.

# if launched directly. (it should always be launched directly. there are no classes in here.)
if __name__ == "__main__":
    with open('client.json', encoding='utf-8') as data_file:
        data = json.load(data_file)
    

    pygame.init()
    pygame.display.set_caption('Cataclysm: Looming Darkness')
    
    _screen = pygame.display.set_mode((854, 480), pygame.ANYFORMAT)
    _FontManager = FontManager('./img/font6x8.png')
    _backdrop = pygame.image.load('./img/client_login.png').convert_alpha()
    
    firstNameInputBox = InputBox(_screen, (340,131,192,24), _FontManager)
    firstNameInputBox.value = data['firstName']
    
    lastNameInputBox = InputBox(_screen, (340,162,192,24), _FontManager)
    lastNameInputBox.value = data['lastName']
    
    passwordInputBox = InputBox(_screen, (340,191,192,24), _FontManager, 'yes')
    passwordInputBox.value = data['password']
    
    savePassword = CheckBox(_screen, (304,222,24,24))
    if(data['savePassword']):
        savePassword.checked == 'yes'

    serverList = ListBox(_screen, (128,128,128), (278,256,480,120))
    for server in data['serverList']:
        print(server)
        _surface = _FontManager.convert_string_to_surface(server)
        item_to_add = Listbox_item(server, _surface, None)
        serverList.add(item_to_add)

    _surface = _FontManager.convert_string_to_surface('Connect')
    connectButton = Button(_screen, _surface, (155,155,155), (660,380,96,48), None)


    UI_Components = []
    # UI_Components.append(_backdrop)
    UI_Components.append(firstNameInputBox)
    UI_Components.append(lastNameInputBox)
    UI_Components.append(passwordInputBox)
    UI_Components.append(savePassword)
    UI_Components.append(serverList)
    UI_Components.append(connectButton)
    _active_component = None
    _highlighted_server = 'Please pick a server from the list.' # the last one we used.

    while True:
        pygame.event.pump() # required so the game doesn't lock up
        _screen.blit(_backdrop, (0,0,854,480))
        for ui_component in UI_Components:
            ui_component.draw() # our homebrew components.
            if(isinstance(ui_component, ListBox)):
                for item in ui_component.item_list:
                # highlight the highlighted server
                    if(item.text == _highlighted_server):
                        _surface = _FontManager.convert_string_to_surface(_highlighted_server)
                        _screen.blit(_surface, (342,230)) # draw the chosen server at a hard-coded location for now.
                        break
                else:
                    _surface = _FontManager.convert_string_to_surface(_highlighted_server)
                    _screen.blit(_surface, (342,230)) # draw the chosen server at a hard-coded location for now.

        pygame.display.flip() # flip the screen after we've .draw() the UI_components
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if(event.type == pygame.MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                print(pos)
                # iterate through our UI_Components and see if we clicked in any of them.
                mouse_x = pos[0]
                mouse_y = pos[1]
                for ui_component in UI_Components:
                    #print(ui_component.rect)
                    if(mouse_x > ui_component.rect[0] and mouse_x < ui_component.rect[0] + ui_component.rect[2]):
                        if(mouse_y > ui_component.rect[1] and mouse_y < ui_component.rect[1] + ui_component.rect[3]):
                            print(ui_component)
                            if(isinstance(ui_component, CheckBox)):
                                ui_component.on_clicked()
                                if(ui_component.checked == 'yes'):
                                    data['savePassword'] = True
                                else:
                                    data['savePassword'] = False
                            elif(isinstance(ui_component, ListBox)):
                                if(ui_component.on_clicked(event.button, pos[0] - ui_component.x, pos[1] - ui_component.y) is not None):
                                    _highlighted_server = ui_component.on_clicked(event.button, pos[0] - ui_component.x, pos[1] - ui_component.y).text
                                    print(_highlighted_server)
                            elif(isinstance(ui_component, InputBox)):
                                _active_component = ui_component
                            elif(isinstance(ui_component, Button)):
                                # we only have one button on this screen so it must be the connect button.
                                subprocess.run(['python', 'client.py', '--host', _highlighted_server.split(':')[0], '--port', _highlighted_server.split(':')[1], firstNameInputBox.value, lastNameInputBox.value])
                            with open('client.json', 'w') as outfile:
                                json.dump(data, outfile, sort_keys = True, indent = 4)
            if(event.type == pygame.KEYUP and _active_component is not None):
                _key = pygame.key.name(event.key)
                if(_key == 'backspace'):
                    _active_component.value = _active_component.value[:-1]
                elif(len(_key) == 1):
                    _active_component.value = _active_component.value + _key
            



