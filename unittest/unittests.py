import os
import sys
import json
from collections import defaultdict
import pygame
import pygame.locals

from item import Item, ItemManager
from recipe import RecipeManager, Recipe
from furniture import FurnitureManager, Furniture

from user_interface import Hotbar, Button, TextBox, ListBox, Listbox_item, FontManager

class Unittest:
    def __init__(self):
        #self.TileManager = TileManager()
        self.ItemManager = ItemManager()
        self.RecipeManager = RecipeManager() # contains all the known recipes in the game. for reference.
        self.FurnitureManager = FurnitureManager()
        #self.FontManager = FontManager()

if __name__ == "__main__":
    unit_test = Unittest()
    print('unit test Successful')
