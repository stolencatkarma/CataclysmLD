"""Game state and data management."""

import os
import glob
import json
import time


class GameStateManager:
    """Manages game state, character creation, and professions."""
    
    def __init__(self):
        # Login state
        self.username = ""
        self.password = ""
        self.input_username = ""
        self.input_password = ""
        self.active_login_field = "username"
        
        # Character state
        self.character_name = ""
        self.available_characters = []
        self.character_data = None
        
        # Character creation
        self.creation_name = ""
        self.creation_gender = "male"
        self.creation_professions = []
        self.creation_profession_index = 0
        self.creation_stats = {
            'strength': 8,
            'dexterity': 8,
            'intelligence': 8,
            'perception': 8,
            'constitution': 8
        }
        self.creation_active_field = 'name'
        
        # Game world
        self.localmap = None
        self.last_player_position = None
        
        # Combat
        self.attack_mode = False
        
        # Flags
        self._waiting_for_character_data = False
        self._just_created_character = False
        
        # Load professions
        self.load_professions()
    
    def load_professions(self):
        """Load all professions from data/json/professions/ directory."""
        self.creation_professions = []
        prof_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'json', 'professions')
        
        if not os.path.exists(prof_dir):
            prof_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'json', 'professions'))
        
        if os.path.exists(prof_dir):
            for file in glob.glob(os.path.join(prof_dir, '*.json')):
                try:
                    with open(file, encoding='utf-8') as f:
                        data = json.load(f)
                        for prof in data:
                            self.creation_professions.append(prof)
                except Exception as e:
                    print(f"Failed to load profession file {file}: {e}")
        
        if not self.creation_professions:
            self.creation_professions.append({
                'ident': 'survivor',
                'name': 'Survivor',
                'description': 'Default profession.'
            })
        
        self.creation_profession_index = 0
    
    def get_character_creation_data(self) -> dict:
        """Get the current character creation data."""
        return {
            'name': self.creation_name or f"Player_{int(time.time())}",
            'gender': self.creation_gender,
            'profession': self.creation_professions[self.creation_profession_index]['ident'] if self.creation_professions else 'survivor',
            **self.creation_stats
        }
    
    def reset_character_creation(self):
        """Reset character creation to default values."""
        self.creation_name = ""
        self.creation_gender = "male"
        self.creation_profession_index = 0
        self.creation_stats = {
            'strength': 8,
            'dexterity': 8,
            'intelligence': 8,
            'perception': 8,
            'constitution': 8
        }
        self.creation_active_field = 'name'
