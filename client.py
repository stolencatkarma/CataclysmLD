#!/usr/bin/env python3

import os
import time
import argparse
import tcod
import tcod.event
import tcod.console

# Modular client components
from src.client.ui_manager import UIManager
from src.client.map_renderer import MapRenderer
from src.client.character_manager import CharacterManager
from src.client.network_manager import NetworkManager
from src.client.input_handler import InputHandler, GameState
from src.client.message_handler import MessageHandler
from src.client.game_state_manager import GameStateManager
from src.item import ItemManager


class CataclysmClient:
    """Main client orchestrator - delegates to modular components."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 6317):
        # Core managers
        self.network_manager = NetworkManager(host, port)
        self.state_manager = GameStateManager()
        self.input_handler = InputHandler(self)
        self.message_handler = MessageHandler(self)
        
        # UI components
        self.ui_manager = None
        self.map_renderer = None
        self.character_manager = None
        self.item_manager = None
        
        # Console setup
        self.console_width = 120
        self.console_height = 40
        self.console = None
        self.context = None
        
        # Current game state
        self.game_state = GameState.LOGIN
        
        # MOTD for login screen
        self.motd_lines = []
        try:
            import src.client.ui_manager as ui_manager
            self.motd_lines = ui_manager.UIManager.get_motd_lines(self)
        except Exception:
            self.motd_lines = []
    
    # Proxy properties to state_manager for backward compatibility
    @property
    def username(self):
        return self.state_manager.username
    
    @username.setter
    def username(self, value):
        self.state_manager.username = value
    
    @property
    def input_username(self):
        return self.state_manager.input_username
    
    @input_username.setter
    def input_username(self, value):
        self.state_manager.input_username = value
    
    @property
    def input_password(self):
        return self.state_manager.input_password
    
    @input_password.setter
    def input_password(self, value):
        self.state_manager.input_password = value
    
    @property
    def active_login_field(self):
        return self.state_manager.active_login_field
    
    @active_login_field.setter
    def active_login_field(self, value):
        self.state_manager.active_login_field = value
    
    @property
    def character_name(self):
        return self.state_manager.character_name
    
    @character_name.setter
    def character_name(self, value):
        self.state_manager.character_name = value
    
    @property
    def available_characters(self):
        return self.state_manager.available_characters
    
    @available_characters.setter
    def available_characters(self, value):
        self.state_manager.available_characters = value
    
    @property
    def character_data(self):
        return self.state_manager.character_data
    
    @character_data.setter
    def character_data(self, value):
        self.state_manager.character_data = value
    
    @property
    def localmap(self):
        return self.state_manager.localmap
    
    @localmap.setter
    def localmap(self, value):
        self.state_manager.localmap = value
    
    @property
    def last_player_position(self):
        return self.state_manager.last_player_position
    
    @last_player_position.setter
    def last_player_position(self, value):
        self.state_manager.last_player_position = value
    
    @property
    def attack_mode(self):
        return self.state_manager.attack_mode
    
    @attack_mode.setter
    def attack_mode(self, value):
        self.state_manager.attack_mode = value
    
    @property
    def creation_name(self):
        return self.state_manager.creation_name
    
    @creation_name.setter
    def creation_name(self, value):
        self.state_manager.creation_name = value
    
    @property
    def creation_gender(self):
        return self.state_manager.creation_gender
    
    @creation_gender.setter
    def creation_gender(self, value):
        self.state_manager.creation_gender = value
    
    @property
    def creation_professions(self):
        return self.state_manager.creation_professions
    
    @property
    def creation_profession_index(self):
        return self.state_manager.creation_profession_index
    
    @creation_profession_index.setter
    def creation_profession_index(self, value):
        self.state_manager.creation_profession_index = value
    
    @property
    def creation_stats(self):
        return self.state_manager.creation_stats
    
    @property
    def creation_active_field(self):
        return self.state_manager.creation_active_field
    
    @creation_active_field.setter
    def creation_active_field(self, value):
        self.state_manager.creation_active_field = value
    
    @property
    def _waiting_for_character_data(self):
        return self.state_manager._waiting_for_character_data
    
    @_waiting_for_character_data.setter
    def _waiting_for_character_data(self, value):
        self.state_manager._waiting_for_character_data = value
    
    @property
    def _just_created_character(self):
        return self.state_manager._just_created_character
    
    @_just_created_character.setter
    def _just_created_character(self, value):
        self.state_manager._just_created_character = value

    def setup_console(self):
        """Initialize the tcod console."""
        try:
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
            
            try:
                self.item_manager = ItemManager()
            except Exception as e:
                print(f"Warning: Failed to load items: {e}")
            
            self.character_manager = CharacterManager()
            return True
        except Exception as e:
            print(f"Failed to initialize console: {e}")
            return False
    
    def connect_to_server(self) -> bool:
        """Connect to the game server."""
        return self.network_manager.connect()
    
    def disconnect_from_server(self):
        """Disconnect from the game server."""
        self.network_manager.disconnect()
    
    def send_command(self, command: str, args=None):
        """Send a command to the server."""
        in_game_commands = {
            'move', 'look', 'character', 'recipe', 'help', 'take', 
            'craft', 'work', 'bash', 'transfer', 'attack', 'spawn'
        }
        
        if command in in_game_commands:
            ident = self.character_name
        else:
            ident = self.username
        
        if command == 'login':
            if not self.input_username or not self.input_password:
                print("Username or password is empty. Not sending login command.")
                return
            username = str(self.input_username)
            password = str(self.input_password)
            args = [username, password]
            ident = username
        
        self.network_manager.send_command(command, args, ident)
    
    def create_character(self):
        """Create a new character with current creation data."""
        char_data = self.state_manager.get_character_creation_data()
        self.character_name = char_data['name']
        self._just_created_character = True
        self.send_command('completed_character', char_data['name'])
    
    def process_messages(self):
        """Process all pending server messages."""
        messages = self.network_manager.process_messages()
        for message in messages:
            self.message_handler.handle_message(message)
    
    def handle_input(self, event: tcod.event.Event) -> bool:
        """Handle user input."""
        return self.input_handler.handle_input(event)
    
    def render(self):
        """Render the current game state."""
        self.console.clear()
        
        if self.game_state == GameState.LOGIN:
            button_areas = {}
            self.ui_manager.render_login_screen(
                self.console, self.input_username, self.input_password, 
                self.active_login_field, self.motd_lines, button_areas
            )
        elif self.game_state == GameState.CHARACTER_SELECT:
            button_areas = {}
            self.ui_manager.render_character_select(
                self.console, self.available_characters, button_areas
            )
        elif self.game_state == GameState.INVENTORY:
            self.ui_manager.render_inventory(
                self.console, self.character_manager.inventory, self.item_manager
            )
        elif self.game_state == GameState.CHARACTER_INFO:
            self.ui_manager.render_character_info_screen(
                self.console, self.character_data
            )
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
        
        self.context.present(self.console)
    
    def render_game(self):
        """Render the main game interface."""
        if self.localmap:
            map_area = (0, 0, 80, 30)
            self.map_renderer.render(
                self.console, self.localmap, map_area, self.character_data
            )
            
            if self.character_data and 'position' in self.character_data:
                pos = self.character_data['position']
                self.console.print(81, 2, f"Pos: {pos['x']},{pos['y']}", fg=(255, 255, 255))
            
            self.ui_manager.render_info_panel(
                self.console, (81, 0, 39, 15), self.character_data
            )
            self.ui_manager.render_messages_panel(
                self.console, (81, 16, 39, 14)
            )
            self.ui_manager.render_status_bar(
                self.console, (0, 31, 120, 9)
            )
    
    def run(self):
        """Main game loop."""
        if not self.setup_console():
            return
        if not self.connect_to_server():
            return
        
        try:
            while True:
                self.process_messages()
                
                for event in tcod.event.get():
                    self.context.convert_event(event)
                    if isinstance(event, tcod.event.Quit):
                        raise SystemExit()
                    elif not self.handle_input(event):
                        raise SystemExit()
                
                self.render()
                time.sleep(0.01)
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
