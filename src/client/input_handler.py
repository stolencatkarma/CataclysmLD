"""Input handling for all game states."""

import tcod.event
from enum import Enum


class GameState(Enum):
    LOGIN = "login"
    CHARACTER_SELECT = "character_select"
    CHARACTER_CREATION = "character_creation"
    PLAYING = "playing"
    INVENTORY = "inventory"
    CHARACTER_INFO = "character_info"


class InputHandler:
    """Handles keyboard and mouse input for all game states."""
    
    def __init__(self, game_client):
        self.client = game_client
        
    def handle_input(self, event: tcod.event.Event) -> bool:
        """Route input to appropriate handler based on game state."""
        if isinstance(event, tcod.event.MouseButtonDown):
            return self.handle_mouse_input(event)
        elif isinstance(event, tcod.event.KeyDown):
            state = self.client.game_state
            if state == GameState.LOGIN:
                return self.handle_login_input(event)
            elif state == GameState.CHARACTER_SELECT:
                return self.handle_character_select_input(event)
            elif state == GameState.CHARACTER_CREATION:
                return self.handle_character_creation_input(event)
            elif state == GameState.PLAYING:
                return self.handle_game_input(event)
            elif state == GameState.INVENTORY:
                return self.handle_inventory_input(event)
            elif state == GameState.CHARACTER_INFO:
                return self.handle_character_info_input(event)
        return True
    
    def handle_mouse_input(self, event: tcod.event.MouseButtonDown) -> bool:
        """Handle mouse clicks for all menu states."""
        mx, my = event.tile
        state = self.client.game_state
        
        if state == GameState.LOGIN:
            button_areas = {}
            self.client.ui_manager.render_login_screen(
                self.client.console, 
                self.client.input_username, 
                self.client.input_password, 
                self.client.active_login_field, 
                self.client.motd_lines, 
                button_areas
            )
            hit = self.client.ui_manager.get_button_hit(mx, my, button_areas)
            if hit == 'login':
                if self.client.input_username and self.client.input_password:
                    self.client.send_command('login', [self.client.input_username, self.client.input_password])
                return True
                
        elif state == GameState.CHARACTER_SELECT:
            button_areas = {}
            self.client.ui_manager.render_character_select(
                self.client.console, 
                self.client.available_characters, 
                button_areas
            )
            hit = self.client.ui_manager.get_button_hit(mx, my, button_areas)
            if hit == 'select' and self.client.available_characters:
                char = self.client.available_characters[0]
                self.client.character_name = char.get('name', 'Unknown')
                self.client.character_data = char
                self.client.send_command('choose_character', self.client.character_name)
                return True
            elif hit == 'create':
                self.client.game_state = GameState.CHARACTER_CREATION
                return True
                
        elif state == GameState.CHARACTER_CREATION:
            button_areas = {}
            self.client.ui_manager.render_character_creation(
                self.client.console,
                name=self.client.creation_name,
                gender=self.client.creation_gender,
                professions=self.client.creation_professions,
                profession_index=self.client.creation_profession_index,
                stats=self.client.creation_stats,
                active_field=self.client.creation_active_field,
                active_button=self.client.creation_active_field if self.client.creation_active_field in ['ok', 'cancel'] else 'ok',
                button_areas=button_areas
            )
            hit = self.client.ui_manager.get_button_hit(mx, my, button_areas)
            if hit == 'ok':
                self.client.create_character()
                return True
            elif hit in ('cancel', 'back'):
                self.client.game_state = GameState.CHARACTER_SELECT
                return True
        
        return True
    
    def handle_login_input(self, event: tcod.event.KeyDown) -> bool:
        """Handle keyboard input during login."""
        if event.sym == tcod.event.KeySym.TAB:
            fields = ["username", "password", "login_btn"]
            try:
                idx = fields.index(self.client.active_login_field)
                self.client.active_login_field = fields[(idx + 1) % len(fields)]
            except ValueError:
                self.client.active_login_field = fields[0]
            return True
            
        elif event.sym == tcod.event.KeySym.RETURN:
            if self.client.active_login_field == 'login_btn' or (
                self.client.input_username and self.client.input_password
            ):
                self.client.send_command('login', [self.client.input_username, self.client.input_password])
            return True
            
        elif event.sym == tcod.event.KeySym.BACKSPACE:
            if self.client.active_login_field == "username":
                self.client.input_username = self.client.input_username[:-1]
            else:
                self.client.input_password = self.client.input_password[:-1]
            return True
            
        elif event.sym == tcod.event.KeySym.ESCAPE:
            return False
            
        # Accept printable characters
        if 32 <= event.sym <= 126:
            char = chr(event.sym)
            if self.client.active_login_field == "username":
                self.client.input_username += char
            else:
                self.client.input_password += char
        
        return True
    
    def handle_character_select_input(self, event: tcod.event.KeyDown) -> bool:
        """Handle keyboard input during character selection."""
        if event.sym == tcod.event.KeySym.RETURN:
            if self.client.available_characters:
                char = self.client.available_characters[0]
                self.client.character_name = char.get('name', 'Unknown')
                self.client.character_data = char
                self.client.send_command('choose_character', self.client.character_name)
            else:
                self.client.game_state = GameState.CHARACTER_CREATION
            return True
            
        elif event.sym == tcod.event.KeySym.C:
            self.client.game_state = GameState.CHARACTER_CREATION
            return True
            
        elif event.sym == tcod.event.KeySym.ESCAPE:
            return False
            
        return True
    
    def handle_character_creation_input(self, event: tcod.event.KeyDown) -> bool:
        """Handle keyboard input during character creation."""
        fields = ['name', 'gender', 'profession', 'strength', 'dexterity', 
                  'intelligence', 'perception', 'constitution', 'ok', 'cancel']
        
        if self.client.creation_active_field not in fields:
            self.client.creation_active_field = 'name'
        
        if event.sym in (tcod.event.KeySym.TAB, tcod.event.KeySym.DOWN):
            idx = fields.index(self.client.creation_active_field)
            self.client.creation_active_field = fields[(idx + 1) % len(fields)]
            return True
            
        elif event.sym == tcod.event.KeySym.UP:
            idx = fields.index(self.client.creation_active_field)
            self.client.creation_active_field = fields[(idx - 1 + len(fields)) % len(fields)]
            return True
            
        elif event.sym == tcod.event.KeySym.LEFT:
            self._handle_creation_left()
            return True
            
        elif event.sym == tcod.event.KeySym.RIGHT:
            self._handle_creation_right()
            return True
            
        elif event.sym == tcod.event.KeySym.BACKSPACE:
            if self.client.creation_active_field == 'name':
                self.client.creation_name = self.client.creation_name[:-1]
            return True
            
        elif event.sym == tcod.event.KeySym.RETURN:
            if self.client.creation_active_field == 'ok':
                self.client.create_character()
                return True
            elif self.client.creation_active_field == 'cancel':
                self.client.game_state = GameState.CHARACTER_SELECT
                return True
                
        elif event.sym == tcod.event.KeySym.ESCAPE:
            self.client.game_state = GameState.CHARACTER_SELECT
            return True
            
        # Accept printable characters for name
        if self.client.creation_active_field == 'name' and 32 <= event.sym <= 126:
            self.client.creation_name += chr(event.sym)
            
        return True
    
    def _handle_creation_left(self):
        """Handle left arrow in character creation."""
        field = self.client.creation_active_field
        if field == 'gender':
            self.client.creation_gender = 'male' if self.client.creation_gender == 'female' else 'female'
        elif field == 'profession':
            self.client.creation_profession_index = (
                self.client.creation_profession_index - 1
            ) % len(self.client.creation_professions)
        elif field in self.client.creation_stats:
            self.client.creation_stats[field] = max(1, self.client.creation_stats[field] - 1)
        elif field == 'ok':
            self.client.creation_active_field = 'cancel'
        elif field == 'cancel':
            self.client.creation_active_field = 'ok'
    
    def _handle_creation_right(self):
        """Handle right arrow in character creation."""
        field = self.client.creation_active_field
        if field == 'gender':
            self.client.creation_gender = 'female' if self.client.creation_gender == 'male' else 'male'
        elif field == 'profession':
            self.client.creation_profession_index = (
                self.client.creation_profession_index + 1
            ) % len(self.client.creation_professions)
        elif field in self.client.creation_stats:
            self.client.creation_stats[field] = min(20, self.client.creation_stats[field] + 1)
        elif field == 'ok':
            self.client.creation_active_field = 'cancel'
        elif field == 'cancel':
            self.client.creation_active_field = 'ok'
    
    def handle_inventory_input(self, event: tcod.event.KeyDown) -> bool:
        """Handle keyboard input in inventory screen."""
        if event.sym in (tcod.event.KeySym.ESCAPE, tcod.event.KeySym.I):
            self.client.game_state = GameState.PLAYING
            return True
        return True
    
    def handle_character_info_input(self, event: tcod.event.KeyDown) -> bool:
        """Handle keyboard input in character info screen."""
        if event.sym in (tcod.event.KeySym.ESCAPE, tcod.event.KeySym.C):
            self.client.game_state = GameState.PLAYING
            return True
        return True

    def handle_game_input(self, event: tcod.event.KeyDown) -> bool:
        """Handle keyboard input during gameplay."""
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
            if self.client.attack_mode:
                # Send attack command with direction
                print(f"[DEBUG] Attacking {direction}")
                self.client.send_command('attack', [direction])
                self.client.attack_mode = False  # Exit attack mode after attacking
            else:
                # Always send direction as a list for protocol compliance
                self.client.send_command('move', [direction])
            return True
            
        elif event.sym == tcod.event.KeySym.L:
            print("[DEBUG] Look command")
            self.client.send_command('look')
            return True
            
        elif event.sym == tcod.event.KeySym.C:
            # Switch to local character info screen
            self.client.game_state = GameState.CHARACTER_INFO
            return True
            
        elif event.sym == tcod.event.KeySym.R:
            self.client.send_command('help')
            return True
            
        elif event.sym == tcod.event.KeySym.A:
            print("[DEBUG] Attack mode - choose direction to attack")
            self.client.attack_mode = True
            return True
            
        elif event.sym == tcod.event.KeySym.I:
            self.client.game_state = GameState.INVENTORY
            return True
            
        elif event.sym == tcod.event.KeySym.ESCAPE:
            return False
            
        return True
