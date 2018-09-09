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
    _FontManager = FontManager()
    _backdrop = pygame.image.load('./img/client_login.png').convert_alpha()
    firstNameInputBox = InputBox(_screen, (340,131,192,24), _FontManager)
    firstNameInputBox.value = 'Andrew'
    lastNameInputBox = InputBox(_screen, (340,162,192,24), _FontManager)
    lastNameInputBox.value = 'Zen'
    passwordInputBox = InputBox(_screen, (340,191,192,24), _FontManager)
    passwordInputBox.value = '****************'
    savePassword = CheckBox(_screen, (304,222,24,24))
    serverList = ListBox(_screen, (128,128,128), (278,256,480,120))
    for server in data['serverList']:
        print(server)
        _surface = _FontManager.convert_string_to_surface(server)
        item_to_add = Listbox_item(server, _surface, None)

    UI_Components = []
    # UI_Components.append(_backdrop)
    UI_Components.append(firstNameInputBox)
    UI_Components.append(lastNameInputBox)
    UI_Components.append(passwordInputBox)
    UI_Components.append(savePassword)
    UI_Components.append(serverList)

    while True:
        pygame.event.pump() # required so the game doesn't lock up
        _screen.blit(_backdrop,(0,0,854,480))
        for ui_component in UI_Components:
            ui_component.draw()
        pygame.display.flip() # flip the screen after we've .draw() the UI_components
        #event = pygame.event.wait() # wait for player input.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if(event.type == pygame.MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                print(pos)
                # check if we clicked on a textbox if so activate it so we can start typing.
