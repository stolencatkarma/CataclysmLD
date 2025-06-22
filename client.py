#!/usr/bin/env python3

import json
import os
import re
import threading
import time
import argparse
import tcod
import tcod.event
import tcod.console
from typing import Optional, List, Dict, Any, Tuple

from src.mastermind._mm_client import MastermindClientTCP
from src.command import Command

# --- Begin modular client classes integration ---

# GameState enum (from client_ui.py)
from enum import Enum
class GameState(Enum):
    LOGIN = "login"
    CHARACTER_SELECT = "character_select"
    CHARACTER_CREATION = "character_creation"
    PLAYING = "playing"

# UIManager (from client_ui.py)
class UIManager:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.messages = []
        self.max_messages = 20
    def add_message(self, message: str, color: Tuple[int, int, int] = (255, 255, 255)):
        self.messages.append((message, color))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    def render_login_screen(self, console: tcod.console.Console):
        console.clear()
        title = "CATACLYSM: LOOMING DARKNESS"
        x = (self.width - len(title)) // 2
        console.print(x, 5, title, fg=(255, 255, 0))
        instructions = [
            "Welcome to Cataclysm: Looming Darkness",
            "",
            "Press ENTER to login with default credentials",
            "Press ESC to quit",
            "",
            "Controls in game:",
            "  Arrow keys / Numpad - Move",
            "  L - Look around",
            "  C - Character sheet",
            "  R - Recipes",
            "  H - Help",
        ]
        start_y = 10
        for i, instruction in enumerate(instructions):
            x = (self.width - len(instruction)) // 2
            console.print(x, start_y + i, instruction)
    def render_character_select(self, console: tcod.console.Console, characters: List[Dict[str, Any]]):
        console.clear()
        title = "CHARACTER SELECTION"
        x = (self.width - len(title)) // 2
        console.print(x, 3, title, fg=(255, 255, 0))
        if characters:
            console.print(5, 8, "Available Characters:")
            for i, char in enumerate(characters):
                name = char.get('name', 'Unknown')
                profession = char.get('profession', 'Unknown')
                char_info = f"{i+1}. {name} ({profession})"
                console.print(7, 10 + i, char_info)
            console.print(5, 15 + len(characters), "Press ENTER to select first character")
        else:
            console.print(5, 8, "No existing characters found.")
        console.print(5, 20, "Press C to create new character")
        console.print(5, 22, "Press ESC to quit")
    def render_character_creation(self, console: tcod.console.Console):
        console.clear()
        title = "CHARACTER CREATION"
        x = (self.width - len(title)) // 2
        console.print(x, 3, title, fg=(255, 255, 0))
        instructions = [
            "Character creation is simplified for this demo.",
            "",
            "A basic survivor character will be created.",
            "",
            "Press ENTER to create character",
            "Press ESC to go back",
        ]
        start_y = 10
        for i, instruction in enumerate(instructions):
            console.print(10, start_y + i, instruction)
    def render_info_panel(self, console: tcod.console.Console, area: Tuple[int, int, int, int], character_data: Optional[Dict[str, Any]]):
        x, y, w, h = area
        console.draw_frame(x, y, w, h, "Character Info", fg=(255, 255, 255))
        if character_data:
            info_y = y + 2
            console.print(x + 2, info_y, f"Name: {character_data.get('name', 'Unknown')}")
            console.print(x + 2, info_y + 1, f"Profession: {character_data.get('profession', 'Unknown')}")
            stats_y = info_y + 3
            console.print(x + 2, stats_y, "Stats:", fg=(200, 200, 200))
            console.print(x + 2, stats_y + 1, f"STR: {character_data.get('strength', 0)}")
            console.print(x + 2, stats_y + 2, f"DEX: {character_data.get('dexterity', 0)}")
            console.print(x + 2, stats_y + 3, f"INT: {character_data.get('intelligence', 0)}")
            console.print(x + 2, stats_y + 4, f"PER: {character_data.get('perception', 0)}")
            console.print(x + 2, stats_y + 5, f"CON: {character_data.get('constitution', 0)}")
        else:
            console.print(x + 2, y + 2, "No character data")
    def render_messages_panel(self, console: tcod.console.Console, area: Tuple[int, int, int, int]):
        x, y, w, h = area
        console.draw_frame(x, y, w, h, "Messages", fg=(255, 255, 255))
        start_y = y + h - 2
        visible_messages = self.messages[-(h-2):]
        for i, (message, color) in enumerate(visible_messages):
            msg_y = start_y - len(visible_messages) + i + 1
            if msg_y >= y + 1:
                if len(message) > w - 4:
                    message = message[:w-7] + "..."
                console.print(x + 2, msg_y, message, fg=color)
    def render_status_bar(self, console: tcod.console.Console, area: Tuple[int, int, int, int]):
        x, y, w, h = area
        console.draw_frame(x, y, w, h, "Commands", fg=(255, 255, 255))
        help_text = [
            "Movement: Arrow Keys/Numpad  |  L:Look  C:Character  R:Recipes  H:Help  ESC:Quit",
            "Game Commands: Take, Craft, Work, Bash, Transfer, Recipe",
            "Type commands will be implemented in future versions"
        ]
        for i, text in enumerate(help_text):
            if i < h - 2:
                console.print(x + 2, y + 1 + i, text, fg=(200, 200, 200))

# MapRenderer (from client_map.py)
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

# CharacterManager (from client_character.py)
class CharacterManager:
    def __init__(self):
        self.character_data = None
        self.known_recipes = []
        self.inventory = []
        self.equipment = {}
    def update_character(self, data: Dict[str, Any]):
        self.character_data = data
    def get_character(self) -> Optional[Dict[str, Any]]:
        return self.character_data
    def add_recipe(self, recipe_name: str):
        if recipe_name not in self.known_recipes:
            self.known_recipes.append(recipe_name)
    def has_recipe(self, recipe_name: str) -> bool:
        return recipe_name in self.known_recipes
    def add_item(self, item: Dict[str, Any]):
        self.inventory.append(item)
    def remove_item(self, item_id: str):
        self.inventory = [item for item in self.inventory if item.get('id') != item_id]
    def equip_item(self, item_id: str):
        item = next((item for item in self.inventory if item.get('id') == item_id), None)
        if item:
            self.equipment[item.get('slot')] = item
    def unequip_item(self, slot: str):
        if slot in self.equipment:
            del self.equipment[slot]
    # ...rest of CharacterManager...

# --- End modular client classes integration ---


class CataclysmClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 6317):
        self.host = host
        self.port = port
        self.client = MastermindClientTCP(timeout_connect=5.0, timeout_receive=1.0)
        self.connected = False
        self.running = True
        
        # Game state
        self.username = ""
        self.password = ""
        self.character_name = ""
        self.game_state = GameState.LOGIN
        self.available_characters = []
        self.localmap = None
        self.character_data = None
        
        # UI components
        self.ui_manager = None
        self.map_renderer = None
        self.character_manager = None
          # Threading
        self.receive_thread = None
        self.receive_lock = threading.Lock()
        self.message_queue = []
        
        # Console setup
        self.console_width = 120
        self.console_height = 40
        self.console = None
        
        # Track last printed position
        self.last_player_position = None
        
    def setup_console(self):
        """Initialize the tcod console using modern context API"""
        try:
            # Use modern tcod context API
            tileset = None
            font_path = "data/fonts/dejavu10x10_gs_tc.png"
            if os.path.exists(font_path):
                tileset = tcod.tileset.load_tilesheet(font_path, 32, 8, tcod.tileset.CHARMAP_TCOD)
                print("Using custom font")
            else:
                print("Using default font (custom font not found)")
            self.context = tcod.context.new(
                columns=self.console_width,
                rows=self.console_height,
                tileset=tileset,
                title="Cataclysm: Looming Darkness",
                vsync=True
            )
            self.console = tcod.console.Console(self.console_width, self.console_height, order="F")
            self.ui_manager = UIManager(self.console_width, self.console_height)
            self.map_renderer = MapRenderer()
            self.character_manager = CharacterManager()
            return True
        except Exception as e:
            print(f"Failed to initialize console: {e}")
            return False
        
    def connect_to_server(self) -> bool:
        """Connect to the game server"""
        try:
            self.client.connect(self.host, self.port)
            self.connected = True
            print(f"Connected to server at {self.host}:{self.port}")
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self.receive_loop, daemon=True)
            self.receive_thread.start()
            
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def disconnect_from_server(self):
        """Disconnect from the game server"""
        if self.connected:
            self.running = False
            self.client.disconnect()
            self.connected = False
            print("Disconnected from server")
    
    def send_command(self, command: str, args: Any = None):
        """Send a command to the server"""
        if not self.connected:
            return
        try:
            # Use character_name as ident for in-game commands, username for login/character selection
            in_game_commands = {
                'move', 'look', 'character', 'recipe', 'help', 'take', 'craft', 'work', 'bash', 'transfer'
            }
            if command in in_game_commands:
                if not self.character_name:
                    print(f"[ERROR] Tried to send in-game command '{command}' but character_name is not set!")
                    return
                ident = self.character_name
            else:
                ident = self.username
            cmd = Command(ident, command, args)
            message = json.dumps(cmd)
            self.client.send(message)
        except Exception as e:
            print(f"Failed to send command: {e}")
    
    def receive_loop(self):
        """Background thread to receive messages from server"""
        buffer = ""
        while self.running and self.connected:
            try:
                data = self.client.receive(blocking=False)
                if data:
                    buffer += data
                    # Try to parse complete JSON objects from the buffer
                    while True:
                        try:
                            # Find the first complete JSON object
                            obj, idx = json.JSONDecoder().raw_decode(buffer)
                            with self.receive_lock:
                                self.message_queue.append(obj)
                            buffer = buffer[idx:].lstrip()
                        except Exception:
                            break
                time.sleep(0.01)  # Small delay to prevent busy waiting
            except Exception as e:
                if self.running:
                    print(f"Receive error: {e}")
                break
    
    def process_messages(self):
        """Process messages from the server"""
        while True:
            with self.receive_lock:
                if not self.message_queue:
                    break
                message = self.message_queue.pop(0)
            # Print concise debug info for localmap_update, full JSON for others
            if isinstance(message, dict) and message.get('command') == 'localmap_update':
                # Print summary: chunk count and player position if available
                localmap = message.get('args')
                if isinstance(localmap, dict):
                    chunks = localmap.get('chunks', [])
                elif isinstance(localmap, list):
                    chunks = localmap
                else:
                    chunks = []
                chunk_count = len(chunks)
                # Try to find player position
                player_pos = self._find_player_position_in_localmap(localmap) if hasattr(self, '_find_player_position_in_localmap') else None
                if player_pos:
                    pos_str = f"x={player_pos.get('x')}, y={player_pos.get('y')}, z={player_pos.get('z')}"
                else:
                    pos_str = "unknown"
            else:
                try:
                    raw_json = json.dumps(message)
                except Exception as e:
                    print(f"[DEBUG] Could not serialize message to JSON: {e}")
            self.handle_server_message(message)
    
    def handle_server_message(self, message: Dict[str, Any]):
        """Handle a message from the server"""
        if not isinstance(message, dict) or 'command' not in message:
            return
        command = message['command']
        # Only print the command name, not the full message
        if command == 'login':
            if message.get('args') == 'accepted':
                print("Login accepted")
                self.game_state = GameState.CHARACTER_SELECT
                self.send_command('request_character_list')
        elif command == 'character_list':
            self.available_characters = []
            for char_data in message.get('args', []):
                try:
                    char_info = json.loads(char_data)
                    self.available_characters.append(char_info)
                except Exception as e:
                    print(f"Failed to parse character: {e}")
            print(f"Received {len(self.available_characters)} characters")
        elif command == 'enter_game':
            print("Entering game!")
            self.game_state = GameState.PLAYING
            # Only send request_localmap if character_name is set
            if self.character_name:
                self.send_command('request_localmap')
            else:
                # print("[DEBUG] Not sending request_localmap: character_name not set yet.")
                pass
            self.send_command('character')  # Request character data
        elif command == 'localmap_update':
            self.localmap = message.get('args')
            # Try to find the player position in the localmap and update self.character_data['position']
            player_pos = self._find_player_position_in_localmap(self.localmap)
            if not player_pos:
                return
            if not self.character_data:
                self.character_data = {}
            self.character_data['position'] = player_pos
            # Only print player position if it changed
            if player_pos != self.last_player_position:
                self.last_player_position = player_pos
            # Force a render after receiving a new map
            if hasattr(self, 'context') and hasattr(self, 'console'):
                self.render()
        elif command == 'character_data':
            self.character_data = message.get('args')
            if self.character_manager:
                self.character_manager.update_character(self.character_data)
            # Only print player position if it changed
            pos = None
            if self.character_data and 'position' in self.character_data:
                pos = self.character_data['position']
            if pos != self.last_player_position:
                self.last_player_position = pos
            # Reset waiting flag for character data
            self._waiting_for_character_data = False
        # Remove move_result handler, as all updates come through localmap_update
        else:
            print(f"Unknown command: {command}")

    def _find_player_position_in_localmap(self, localmap):
        """Search the localmap for the player creature matching our character name and return its position dict, or None."""
        # localmap can be a list of chunks or a dict with 'chunks'
        if isinstance(localmap, dict):
            chunks = localmap.get('chunks', [])
        elif isinstance(localmap, list):
            chunks = localmap
        else:
            return None
        found_creatures = []
        for chunk in chunks:
            if not isinstance(chunk, dict) or 'tiles' not in chunk:
                continue
            for tile in chunk['tiles']:
                creature = tile.get('creature')
                if creature:
                    found_creatures.append(creature)
                    # Match by character name if available, fallback to is_player if present
                    if self.character_name and creature.get('name') == self.character_name:
                        return tile.get('position')
                    if creature.get('is_player'):
                        return tile.get('position')
        if not found_creatures:
            pass
        return None

    def handle_input(self, event: tcod.event.Event) -> bool:
        """Handle user input based on current game state"""
        if isinstance(event, tcod.event.KeyDown):
            if self.game_state == GameState.LOGIN:
                return self.handle_login_input(event)
            elif self.game_state == GameState.CHARACTER_SELECT:
                return self.handle_character_select_input(event)
            elif self.game_state == GameState.CHARACTER_CREATION:
                return self.handle_character_creation_input(event)
            elif self.game_state == GameState.PLAYING:
                return self.handle_game_input(event)
        
        return True
    
    def handle_login_input(self, event: tcod.event.KeyDown) -> bool:
        """Handle input during login state"""
        if event.sym == tcod.event.KeySym.RETURN:
            if not self.username:
                self.username = "testuser"  # Placeholder
                self.password = "testpass"  # Placeholder
                self.send_command('login', self.password)
            return True
        elif event.sym == tcod.event.KeySym.ESCAPE:
            return False
        return True

    def handle_character_select_input(self, event: tcod.event.KeyDown) -> bool:
        """Handle input during character selection"""
        if event.sym == tcod.event.KeySym.RETURN:
            if self.available_characters:
                char = self.available_characters[0]
                self.character_name = char.get('name', 'Unknown')
                self.character_data = char
                self.send_command('choose_character', self.character_name)
            else:
                self.game_state = GameState.CHARACTER_CREATION
            return True
        elif event.sym == tcod.event.KeySym.C:
            self.game_state = GameState.CHARACTER_CREATION
            return True
        elif event.sym == tcod.event.KeySym.ESCAPE:
            return False
        return True

    def handle_character_creation_input(self, event: tcod.event.KeyDown) -> bool:
        """Handle input during character creation"""
        if event.sym == tcod.event.KeySym.RETURN:
            self.character_name = f"Player_{int(time.time())}"
            self.send_command('completed_character', self.character_name)
            return True
        elif event.sym == tcod.event.KeySym.ESCAPE:
            self.game_state = GameState.CHARACTER_SELECT
            return True
        return True

    def handle_game_input(self, event: tcod.event.KeyDown) -> bool:
        """Handle input during gameplay"""
        key_to_dir = {
            tcod.event.KeySym.UP: 'north',
            tcod.event.KeySym.KP_8: 'north',
            tcod.event.KeySym.DOWN: 'south',
            tcod.event.KeySym.KP_2: 'south',
            tcod.event.KeySym.LEFT: 'west',
            tcod.event.KeySym.KP_4: 'west',
            tcod.event.KeySym.RIGHT: 'east',
            tcod.event.KeySym.KP_6: 'east',
            tcod.event.KeySym.KP_7: 'northwest',
            tcod.event.KeySym.KP_9: 'northeast',
            tcod.event.KeySym.KP_1: 'southwest',
            tcod.event.KeySym.KP_3: 'southeast',
        }
        if event.sym in key_to_dir:
            direction = key_to_dir[event.sym]
            # Always send direction as a list for protocol compliance
            self.send_command('move', [direction])
            return True
        elif event.sym == tcod.event.KeySym.L:
            print("[DEBUG] Look command")
            self.send_command('look')
        elif event.sym == tcod.event.KeySym.C:
            # Only send 'character' command if not already waiting for a response
            if not hasattr(self, '_waiting_for_character_data') or not self._waiting_for_character_data:
                self._waiting_for_character_data = True
                self.send_command('character')
        elif event.sym == tcod.event.KeySym.R:
            # print("[DEBUG] Help command")
            self.send_command('help')
        elif event.sym == tcod.event.KeySym.ESCAPE:
            return False
        return True
    
    def render(self):
        """Render the current game state"""
        self.console.clear()
        
        if self.game_state == GameState.LOGIN:
            self.ui_manager.render_login_screen(self.console)
        elif self.game_state == GameState.CHARACTER_SELECT:
            self.ui_manager.render_character_select(self.console, self.available_characters)
        elif self.game_state == GameState.CHARACTER_CREATION:
            self.ui_manager.render_character_creation(self.console)
        elif self.game_state == GameState.PLAYING:
            self.render_game()
        # Present the console using the context
        self.context.present(self.console)
    
    def render_game(self):
        """Render the main game interface"""
        if self.localmap:
            # Render map
            map_area = (0, 0, 80, 30)
            # Pass both list and dict to map_renderer, which will handle both
            self.map_renderer.render(self.console, self.localmap, map_area, self.character_data)
            # Remove debug print here (player position now handled in handle_server_message)
            # Render UI panels
            self.ui_manager.render_info_panel(self.console, (81, 0, 39, 15), self.character_data)
            self.ui_manager.render_messages_panel(self.console, (81, 16, 39, 14))
            self.ui_manager.render_status_bar(self.console, (0, 31, 120, 9))
    
    def run(self):
        """Main game loop"""
        if not self.setup_console():
            return
        if not self.connect_to_server():
            return
        try:
            while True:
                # Process all server messages as soon as possible
                self.process_messages()
                # Handle all input events (non-blocking)
                for event in tcod.event.get():
                    if isinstance(event, tcod.event.Quit):
                        raise SystemExit()
                    elif not self.handle_input(event):
                        raise SystemExit()
                # Always render (even if no input)
                self.render()
                time.sleep(0.01)  # Small sleep to avoid busy loop
        except SystemExit:
            pass
        finally:
            self.disconnect_from_server()


def main():
    parser = argparse.ArgumentParser(description="Cataclysm: Looming Darkness Client")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=6317, help="Server port")
    args = parser.parse_args()
    
    client = CataclysmClient(args.host, args.port)
    client.run()


if __name__ == "__main__":
    main()
