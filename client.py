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
import sys
from typing import Optional, List, Dict, Any, Tuple


# Use absolute imports for client modules
from src.client.ui_manager import UIManager
from src.client.map_renderer import MapRenderer
from src.client.character_manager import CharacterManager

from src.mastermind._mm_client import MastermindClientTCP
from src.command import Command
from src.passhash import hashPassword as hashpass

# --- Begin modular client classes integration ---

# GameState enum (from client_ui.py)
from enum import Enum
class GameState(Enum):
    LOGIN = "login"
    CHARACTER_SELECT = "character_select"
    CHARACTER_CREATION = "character_creation"
    PLAYING = "playing"

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
        self.input_username = ""
        self.input_password = ""
        self.active_login_field = "username"  # or "password"
        self.character_name = ""
        self.game_state = GameState.LOGIN
        self.available_characters = []
        self.localmap = None
        self.character_data = None
        
        # Character creation state
        self.creation_name = ""
        self.creation_gender = "male"
        self.creation_professions = []  # List of loaded professions
        self.creation_profession_index = 0
        self.creation_stats = {
            'strength': 8,
            'dexterity': 8,
            'intelligence': 8,
            'perception': 8,
            'constitution': 8
        }
        
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
        
        # Active field for character creation
        self.creation_active_field = 'name'
        
        self.motd_lines = []
        self.load_professions()
        # Load MOTD ASCII art for main menu
        try:
            import src.client.ui_manager as ui_manager
            self.motd_lines = ui_manager.UIManager.get_motd_lines(self)
        except Exception:
            self.motd_lines = []

    def load_professions(self):
        """Load all professions from data/json/professions/ directory."""
        import glob
        import json
        self.creation_professions = []
        prof_dir = os.path.join(os.path.dirname(__file__), 'data', 'json', 'professions')
        if not os.path.exists(prof_dir):
            prof_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'json', 'professions'))
        for file in glob.glob(os.path.join(prof_dir, '*.json')):
            with open(file, encoding='utf-8') as f:
                data = json.load(f)
                for prof in data:
                    self.creation_professions.append(prof)
        if not self.creation_professions:
            self.creation_professions.append({'ident': 'survivor', 'name': 'Survivor', 'description': 'Default profession.'})
        self.creation_profession_index = 0

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
            in_game_commands = {
                'move', 'look', 'character', 'recipe', 'help', 'take', 'craft', 'work', 'bash', 'transfer'
            }
            if command in in_game_commands:
                ident = self.character_name
            else:
                ident = self.username  # Always use self.username for account-level commands
            if command == 'login':
                if not self.input_username or not self.input_password:
                    print("Username or password is empty. Not sending login command.")
                    return
                # Ensure both are strings
                username = str(self.input_username)
                password = str(self.input_password)
                args = [username, password]
                ident = username
            # If using hashpass anywhere, ensure password is a string
            if command == 'some_command_that_hashes':
                # Example usage:
                # hashed = hashpass(str(password), salt)
                pass
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
                self.username = self.input_username  # Set username after successful login
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
            # Auto-select just created character if needed
            if hasattr(self, '_just_created_character') and self._just_created_character:
                for char in self.available_characters:
                    if char.get('name') == self.character_name:
                        self.character_data = char
                        self.send_command('choose_character', self.character_name)
                        break
                self._just_created_character = False
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
        # Mouse support for all menus
        if isinstance(event, tcod.event.MouseButtonDown):
            mx, my = event.tile
            if self.game_state == GameState.LOGIN:
                button_areas = {}
                self.ui_manager.render_login_screen(self.console, self.input_username, self.input_password, self.active_login_field, self.motd_lines, button_areas)
                hit = self.ui_manager.get_button_hit(mx, my, button_areas)
                if hit == 'login':
                    if self.input_username and self.input_password:
                        self.send_command('login', [self.input_username, self.input_password])
                    return True
            elif self.game_state == GameState.CHARACTER_SELECT:
                button_areas = {}
                self.ui_manager.render_character_select(self.console, self.available_characters, button_areas)
                hit = self.ui_manager.get_button_hit(mx, my, button_areas)
                if hit == 'select' and self.available_characters:
                    char = self.available_characters[0]
                    self.character_name = char.get('name', 'Unknown')
                    self.character_data = char
                    self.send_command('choose_character', self.character_name)
                    return True
                elif hit == 'create':
                    self.game_state = GameState.CHARACTER_CREATION
                    return True
            elif self.game_state == GameState.CHARACTER_CREATION:
                button_areas = {}
                self.ui_manager.render_character_creation(
                    self.console,
                    name=self.creation_name,
                    gender=self.creation_gender,
                    professions=self.creation_professions,
                    profession_index=self.creation_profession_index,
                    stats=self.creation_stats,
                    active_field=self.creation_active_field,
                    active_button=self.creation_active_field if self.creation_active_field in ['ok', 'cancel'] else 'ok',
                    button_areas=button_areas
                )
                hit = self.ui_manager.get_button_hit(mx, my, button_areas)
                if hit == 'ok':
                    char_data = {
                        'name': self.creation_name or f"Player_{int(time.time())}",
                        'gender': self.creation_gender,
                        'profession': self.creation_professions[self.creation_profession_index]['ident'] if self.creation_professions else 'survivor',
                        **self.creation_stats
                    }
                    self.character_name = char_data['name']  # Set character_name BEFORE sending command
                    self._just_created_character = True  # Track that we just created a character
                    # Server expects only the character name. Sending full data may cause a server-side error.
                    self.send_command('completed_character', char_data['name'])
                    return True
                elif hit == 'cancel':
                    self.game_state = GameState.CHARACTER_SELECT
                    return True
                elif hit == 'back':  # New Back button handling
                    self.game_state = GameState.CHARACTER_SELECT
                    return True
        # ...existing code for keyboard...
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
        import string
        if event.sym == tcod.event.KeySym.TAB:
            fields = ["username", "password", "login_btn"]
            try:
                idx = fields.index(self.active_login_field)
                self.active_login_field = fields[(idx + 1) % len(fields)]
            except ValueError:
                self.active_login_field = fields[0]
            return True
        elif event.sym == tcod.event.KeySym.RETURN:
            if self.active_login_field == 'login_btn' or (self.input_username and self.input_password):
                self.send_command('login', [self.input_username, self.input_password])
            return True
        elif event.sym == tcod.event.KeySym.BACKSPACE:
            if self.active_login_field == "username":
                self.input_username = self.input_username[:-1]
            else:
                self.input_password = self.input_password[:-1]
            return True
        elif event.sym == tcod.event.KeySym.ESCAPE:
            return False
        # Accept printable characters
        if event.sym >= 32 and event.sym <= 126:
            char = chr(event.sym)
            if self.active_login_field == "username":
                self.input_username += char
            else:
                self.input_password += char
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
        fields = ['name', 'gender', 'profession', 'strength', 'dexterity', 'intelligence', 'perception', 'constitution', 'ok', 'cancel']
        if self.creation_active_field not in fields:
            self.creation_active_field = 'name'
        
        if event.sym in (tcod.event.KeySym.TAB, tcod.event.KeySym.DOWN):
            try:
                idx = fields.index(self.creation_active_field)
                self.creation_active_field = fields[(idx + 1) % len(fields)]
            except ValueError:
                self.creation_active_field = fields[0]
            return True
        elif event.sym == tcod.event.KeySym.UP:
            try:
                idx = fields.index(self.creation_active_field)
                self.creation_active_field = fields[(idx - 1 + len(fields)) % len(fields)]
            except ValueError:
                self.creation_active_field = fields[0]
            return True
        elif event.sym == tcod.event.KeySym.LEFT:
            if self.creation_active_field == 'gender':
                self.creation_gender = 'male' if self.creation_gender == 'female' else 'female'
            elif self.creation_active_field == 'profession':
                self.creation_profession_index = (self.creation_profession_index - 1) % len(self.creation_professions)
            elif self.creation_active_field in self.creation_stats:
                self.creation_stats[self.creation_active_field] = max(1, self.creation_stats[self.creation_active_field] - 1)
            elif self.creation_active_field == 'ok':
                self.creation_active_field = 'cancel'
            elif self.creation_active_field == 'cancel':
                self.creation_active_field = 'ok'
            return True
        elif event.sym == tcod.event.KeySym.RIGHT:
            if self.creation_active_field == 'gender':
                self.creation_gender = 'female' if self.creation_gender == 'male' else 'male'
            elif self.creation_active_field == 'profession':
                self.creation_profession_index = (self.creation_profession_index + 1) % len(self.creation_professions)
            elif self.creation_active_field in self.creation_stats:
                self.creation_stats[self.creation_active_field] = min(20, self.creation_stats[self.creation_active_field] + 1)
            elif self.creation_active_field == 'ok':
                self.creation_active_field = 'cancel'
            elif self.creation_active_field == 'cancel':
                self.creation_active_field = 'ok'
            return True
        elif event.sym == tcod.event.KeySym.BACKSPACE:
            if self.creation_active_field == 'name':
                self.creation_name = self.creation_name[:-1]
            return True
        elif event.sym == tcod.event.KeySym.RETURN:
            if self.creation_active_field == 'ok':
                char_data = {
                    'name': self.creation_name or f"Player_{int(time.time())}",
                    'gender': self.creation_gender,
                    'profession': self.creation_professions[self.creation_profession_index]['ident'] if self.creation_professions else 'survivor',
                    **self.creation_stats
                }
                self.character_name = char_data['name']  # Set character_name BEFORE sending command
                self._just_created_character = True  # Track that we just created a character
                # Server expects only the character name. Sending full data may cause a server-side error.
                self.send_command('completed_character', char_data['name'])
                return True
            elif self.creation_active_field == 'cancel':
                self.game_state = GameState.CHARACTER_SELECT
                return True
        elif event.sym == tcod.event.KeySym.ESCAPE:
            self.game_state = GameState.CHARACTER_SELECT
            return True
        # Accept printable characters for name
        if self.creation_active_field == 'name' and event.sym >= 32 and event.sym <= 126:
            self.creation_name += chr(event.sym)
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
            button_areas = {}
            self.ui_manager.render_login_screen(self.console, self.input_username, self.input_password, self.active_login_field, self.motd_lines, button_areas)
        elif self.game_state == GameState.CHARACTER_SELECT:
            button_areas = {}
            self.ui_manager.render_character_select(self.console, self.available_characters, button_areas)
        elif self.game_state == GameState.CHARACTER_CREATION:
            button_areas = {}
            self.ui_manager.render_character_creation(
                self.console,
                name=self.creation_name,
                gender=self.creation_gender,
                professions=self.creation_professions,
                profession_index=self.creation_profession_index,
                stats=self.creation_stats,
                active_field=self.creation_active_field,
                active_button=self.creation_active_field if self.creation_active_field in ['ok', 'cancel'] else 'ok',
                button_areas=button_areas
            )
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
                    self.context.convert_event(event)
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
