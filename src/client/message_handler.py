"""Server message processing."""

import json
from typing import Dict, Any


class MessageHandler:
    """Handles all messages received from the server."""
    
    def __init__(self, game_client):
        self.client = game_client
    
    def handle_message(self, message: Dict[str, Any]):
        """Route message to appropriate handler."""
        if not isinstance(message, dict) or 'command' not in message:
            return
        
        command = message['command']
        # print(f"[MSG] Received: {command}")
        
        handlers = {
            'login': self._handle_login,
            'character_list': self._handle_character_list,
            'enter_game': self._handle_enter_game,
            'localmap_update': self._handle_localmap_update,
            'character_data': self._handle_character_data,
            'character': self._handle_character_data,  # Server might send 'character' instead
        }
        
        handler = handlers.get(command)
        if handler:
            handler(message)
        else:
            print(f"[MSG] Unknown command: {command}, full message: {message}")
    
    def _handle_login(self, message: Dict[str, Any]):
        """Handle login response."""
        if message.get('args') == 'accepted':
            print("Login accepted")
            from src.client.input_handler import GameState
            self.client.username = self.client.input_username
            self.client.game_state = GameState.CHARACTER_SELECT
            self.client.send_command('request_character_list')
    
    def _handle_character_list(self, message: Dict[str, Any]):
        """Handle character list from server."""
        self.client.available_characters = []
        for char_data in message.get('args', []):
            try:
                char_info = json.loads(char_data)
                self.client.available_characters.append(char_info)
            except Exception as e:
                print(f"Failed to parse character: {e}")
        
        print(f"Received {len(self.client.available_characters)} characters")
        
        # Auto-select just created character if needed
        if hasattr(self.client, '_just_created_character') and self.client._just_created_character:
            for char in self.client.available_characters:
                if char.get('name') == self.client.character_name:
                    self.client.character_data = char
                    self.client.send_command('choose_character', self.client.character_name)
                    break
            self.client._just_created_character = False
    
    def _handle_enter_game(self, message: Dict[str, Any]):
        """Handle entering the game world."""
        print("Entering game!")
        from src.client.input_handler import GameState
        self.client.game_state = GameState.PLAYING
        
        if self.client.character_name:
            self.client.send_command('request_localmap')
        else:
            self.client.send_command('character')
    
    def _handle_localmap_update(self, message: Dict[str, Any]):
        """Handle map update from server."""
        self.client.localmap = message.get('args')
        # print(f"[DEBUG] Received localmap update")
        
        # Find player position in the localmap
        player_pos = self._find_player_position_in_localmap(self.client.localmap)
        if not player_pos:
            print(f"Warning: Could not find player position for character {self.client.character_name} in localmap")
            return
        
        if not self.client.character_data:
            self.client.character_data = {}
        
        old_pos = self.client.character_data.get('position')
        self.client.character_data['position'] = player_pos
        
        # Only print if position changed
        if player_pos != self.client.last_player_position:
            print(f"Player moved: {old_pos} -> {player_pos}")
            self.client.last_player_position = player_pos
        
        # Force render after map update
        if hasattr(self.client, 'context') and hasattr(self.client, 'console'):
            self.client.render()
            # print("Forced render after localmap update")
    
    def _handle_character_data(self, message: Dict[str, Any]):
        """Handle character data update."""
        self.client.character_data = message.get('args')
        if self.client.character_manager:
            self.client.character_manager.update_character(self.client.character_data)
        
        # Only print if position changed
        pos = None
        if self.client.character_data and 'position' in self.client.character_data:
            pos = self.client.character_data['position']
        
        if pos != self.client.last_player_position:
            self.client.last_player_position = pos
        
        # Reset waiting flag
        self.client._waiting_for_character_data = False
    
    def _find_player_position_in_localmap(self, localmap):
        """Find player position in localmap data."""
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
                    # Match by character name or is_player flag
                    if self.client.character_name and creature.get('name') == self.client.character_name:
                        return tile.get('position')
                    if creature.get('is_player'):
                        return tile.get('position')
        
        return None
