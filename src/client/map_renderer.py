import tcod
from typing import Any, Dict, Tuple

# MapRenderer implementation moved here from old location.

class MapRenderer:
    def __init__(self):
        self.tile_colors = {
            't_floor': (128, 128, 128),
            't_wall': (255, 255, 255),
            't_door_c': (139, 69, 19),
            't_door_o': (101, 67, 33),
            't_window': (173, 216, 230),
            't_grass': (34, 139, 34),
            't_dirt': (139, 119, 101),
            't_pavement': (105, 105, 105),
            't_road': (64, 64, 64),
            't_water': (0, 100, 200),
            't_tree': (0, 100, 0),
            't_open_air': (135, 206, 235),
        }
        self.tile_chars = {
            't_floor': '.',
            't_wall': '#',
            't_door_c': '+',
            't_door_o': '/',
            't_window': '"',
            't_grass': '.',
            't_dirt': '.',
            't_pavement': '.',
            't_road': '.',
            't_water': '~',
            't_tree': 'T',
            't_open_air': ' ',
        }
        self.default_color = (100, 100, 100)
        self.default_char = '?'
        self.player_char = '@'
        self.player_color = (255, 255, 0)
        self.item_color = (255, 255, 0)
        self.furniture_color = (139, 69, 19)
        self.monster_color = (255, 0, 0)
    def render(self, console, localmap, area, character_data):
        x, y, w, h = area
        if not localmap:
            console.print(x + 2, y + 2, "No map data available")
            return
        # Determine chunks
        if isinstance(localmap, list):
            chunks = localmap
        elif isinstance(localmap, dict):
            chunks = localmap.get('chunks', [])
        else:
            chunks = []
        # Center on player if possible
        player_pos = None
        if character_data and 'position' in character_data:
            player_pos = character_data['position']
        if player_pos:
            center_x = player_pos.get('x', 0)
            center_y = player_pos.get('y', 0)
            offset_x = center_x - w // 2
            offset_y = center_y - h // 2
        else:
            offset_x = 0
            offset_y = 0
        # Draw tiles
        for chunk in chunks:
            if not isinstance(chunk, dict) or 'tiles' not in chunk:
                continue
            for tile in chunk['tiles']:
                if not isinstance(tile, dict) or 'position' not in tile:
                    continue
                tile_pos = tile['position']
                screen_x = tile_pos['x'] - offset_x
                screen_y = tile_pos['y'] - offset_y
                if 0 <= screen_x < w and 0 <= screen_y < h:
                    self._render_tile(console, x + screen_x, y + screen_y, tile)
        # Draw player '@' after all tiles
        if player_pos:
            px = x + (player_pos.get('x', 0) - offset_x)
            py = y + (player_pos.get('y', 0) - offset_y)
            if 0 <= px < x + w and 0 <= py < y + h:
                console.print(px, py, '@', fg=self.player_color)
    def _render_tile(self, console, x, y, tile):
        # Get terrain ident
        terrain = tile.get('terrain', {})
        terrain_ident = terrain.get('ident', 'unknown')
        char = self.tile_chars.get(terrain_ident, self.default_char)
        fg = self.tile_colors.get(terrain_ident, self.default_color)
        bg = (0, 0, 0)
        # Check for furniture
        if tile.get('furniture'):
            char = 'f'
            fg = self.furniture_color
        # Check for items
        items = tile.get('items', [])
        if items:
            item = items[0]
            if item.get('ident') == 'blueprint':
                char = 'B'
                fg = (0, 255, 255)
            else:
                char = '!'
                fg = self.item_color
        # Check for creature/monster
        if tile.get('creature'):
            char = 'M'
            fg = self.monster_color
        console.print(x, y, char, fg=fg, bg=bg)
