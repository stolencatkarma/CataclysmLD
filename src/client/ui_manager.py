import tcod
import os
from typing import Optional, List, Dict, Any, Tuple

# UIManager implementation moved here from old location.

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
    def render_login_screen(self, console: tcod.console.Console, username: str = '', password: str = '', active_field: str = 'username', motd_lines: list = None, button_areas: dict = None):
        console.clear()
        y = 1
        # Draw MOTD ASCII art if provided
        if motd_lines:
            for i, line in enumerate(motd_lines):
                x = (self.width - len(line)) // 2
                console.print(x, y + i, line, fg=(180, 255, 180))
            y += len(motd_lines) + 1
        title = "CATACLYSM: LOOMING DARKNESS"
        x = (self.width - len(title)) // 2
        console.print(x, y, title, fg=(255, 255, 0))
        y += 2
        instructions = [
            "Enter your username and password to login:",
            "",
            "Tab: Switch field  Enter: Login  ESC: Quit",
            "",
        ]
        for i, instruction in enumerate(instructions):
            x = (self.width - len(instruction)) // 2
            console.print(x, y + i, instruction)
        # Draw input fields
        field_x = (self.width - 30) // 2
        user_label = "Username: "
        pass_label = "Password: "
        user_fg = (255, 255, 255) if active_field == 'username' else (180, 180, 180)
        pass_fg = (255, 255, 255) if active_field == 'password' else (180, 180, 180)
        console.print(field_x, y + len(instructions) + 2, user_label + username, fg=user_fg)
        console.print(field_x, y + len(instructions) + 4, pass_label + ("*" * len(password)), fg=pass_fg)
        # Draw Login button
        btn_y = y + len(instructions) + 7
        btn_x = field_x
        btn_label = "[ Login ]"
        btn_fg = (0, 0, 0) if active_field == 'login_btn' else (255, 255, 255)
        btn_bg = (0, 180, 255) if active_field == 'login_btn' else (0, 60, 120)
        console.print(btn_x, btn_y, btn_label, fg=btn_fg, bg=btn_bg)
        if button_areas is not None:
            button_areas['login'] = (btn_x, btn_y, btn_x + len(btn_label) - 1, btn_y)
    def render_character_select(self, console: tcod.console.Console, characters: List[Dict[str, Any]], button_areas: dict = None):
        console.clear()
        title = "CHARACTER SELECTION"
        x = (self.width - len(title)) // 2
        console.print(x, 3, title, fg=(255, 255, 0))
        btn_y = 25
        if characters:
            console.print(5, 8, "Available Characters:")
            for i, char in enumerate(characters):
                name = char.get('name', 'Unknown')
                profession = char.get('profession', 'Unknown')
                char_info = f"{i+1}. {name} ({profession})"
                console.print(7, 10 + i, char_info)
            console.print(5, 15 + len(characters), "Press ENTER to select first character")
            # Draw Select button
            btn_label = "[ Select ]"
            btn_x = 5
            console.print(btn_x, btn_y, btn_label, fg=(255,255,255), bg=(0,120,255))
            if button_areas is not None:
                button_areas['select'] = (btn_x, btn_y, btn_x + len(btn_label) - 1, btn_y)
        else:
            console.print(5, 8, "No existing characters found.")
        # Draw Create button
        create_label = "[ Create New Character ]"
        create_x = 25
        console.print(create_x, btn_y, create_label, fg=(255,255,255), bg=(0,180,0))
        if button_areas is not None:
            button_areas['create'] = (create_x, btn_y, create_x + len(create_label) - 1, btn_y)
        console.print(5, 22, "Press ESC to quit")
    def render_character_creation(self, console: tcod.console.Console, name: str = '', gender: str = 'male', professions=None, profession_index: int = 0, stats=None, active_field: str = 'name', active_button: str = 'ok', button_areas: dict = None):
        if professions is None:
            professions = []
        if stats is None:
            stats = {'strength': 8, 'dexterity': 8, 'intelligence': 8, 'perception': 8, 'constitution': 8}
        console.clear()
        title = "CHARACTER CREATION"
        x = (self.width - len(title)) // 2
        console.print(x, 3, title, fg=(255, 255, 0))
        start_y = 6
        fields = [
            ('name', f"Name: {name}"),
            ('gender', f"Gender: {gender}"),
            ('profession', f"Profession: {professions[profession_index]['name'] if professions else 'None'}"),
            ('strength', f"Strength: {stats['strength']}",),
            ('dexterity', f"Dexterity: {stats['dexterity']}",),
            ('intelligence', f"Intelligence: {stats['intelligence']}",),
            ('perception', f"Perception: {stats['perception']}",),
            ('constitution', f"Constitution: {stats['constitution']}",),
        ]
        for i, (field, label, *_) in enumerate(fields):
            fg = (255, 255, 255) if field == active_field else (180, 180, 180)
            console.print(10, start_y + i * 2, label, fg=fg)
        # Show profession description
        if professions:
            prof = professions[profession_index]
            desc = prof.get('description', '')
            console.print(40, start_y, f"{prof['name']}: {desc}", fg=(200, 200, 200))
        # OK/Cancel buttons
        btn_y = start_y + len(fields) * 2 + 2
        ok_fg = (0, 0, 0) if active_button == 'ok' else (255, 255, 255)
        ok_bg = (0, 255, 0) if active_button == 'ok' else (0, 100, 0)
        cancel_fg = (0, 0, 0) if active_button == 'cancel' else (255, 255, 255)
        cancel_bg = (255, 0, 0) if active_button == 'cancel' else (100, 0, 0)
        ok_label = "[ OK ]"
        cancel_label = "[ Cancel ]"
        console.print(10, btn_y, ok_label, fg=ok_fg, bg=ok_bg)
        console.print(20, btn_y, cancel_label, fg=cancel_fg, bg=cancel_bg)
        if button_areas is not None:
            button_areas['ok'] = (10, btn_y, 10 + len(ok_label) - 1, btn_y)
            button_areas['cancel'] = (20, btn_y, 20 + len(cancel_label) - 1, btn_y)
        # Instructions
        instructions = [
            "Tab/Up/Down: Move  Left/Right: Change  Enter: Select  ESC: Back"
        ]
        for i, text in enumerate(instructions):
            console.print(10, btn_y + 2 + i, text, fg=(180, 180, 180))

    def render_inventory(self, console: tcod.console.Console, inventory: List[Dict[str, Any]], item_manager=None):
        console.clear()
        width = 60
        height = 40
        x = (self.width - width) // 2
        y = (self.height - height) // 2
        
        console.draw_frame(x, y, width, height, "Inventory", fg=(255, 255, 255), bg=(0, 0, 0))
        
        if not inventory:
            console.print(x + 2, y + 2, "Your inventory is empty.", fg=(180, 180, 180))
        else:
            for i, item in enumerate(inventory):
                if y + 2 + i >= y + height - 1:
                    break
                ident = item.get('ident')
                name = item.get('name', ident) # Fallback to ident
                
                # If we have item_manager, try to get the display name
                if item_manager and ident in item_manager.ITEM_TYPES:
                    name = item_manager.ITEM_TYPES[ident].get('name', name)
                    
                console.print(x + 2, y + 2 + i, f"{chr(ord('a') + i)}) {name}")
                
        console.print(x + 2, y + height - 2, "ESC/I: Close", fg=(255, 255, 0))

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
    def is_point_in_rect(self, px, py, rect):
        x1, y1, x2, y2 = rect
        return x1 <= px <= x2 and y1 <= py <= y2
    def get_motd_lines(self):
        motd_path = os.path.join(os.path.dirname(__file__), '..', '..', 'motd.txt')
        if os.path.exists(motd_path):
            with open(motd_path, encoding='utf-8') as f:
                return [line.rstrip('\n') for line in f.readlines()]
        return []
    def get_button_hit(self, px, py, button_areas):
        for key, rect in button_areas.items():
            if self.is_point_in_rect(px, py, rect):
                return key
        return None
