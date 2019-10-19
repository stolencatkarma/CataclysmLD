import os
from src.request_handler.state.command_handler import CommandHandler


class CharacterRequestHandler(CommandHandler):
    def __init__(self):
        super().__init__()

    def handle_request(self, command, world_state):
        response = super().handle_request(command, world_state)
        try:
            characters = self.get_characters(command)
        except:
            return response.set_response_success(False)

        response.args['characters'] = characters
        return response.set_response_success(True)

    def get_characters(self, command):
        characters = []
        for root, _, files in os.walk(f'./{self.ACCOUNTS_DIRECTORY}/{command.ident}/characters/'):
            for file_data in files:
                if file_data.endswith('.character'):
                    with open(root + file_data, 'r') as data_file:
                        characters.append(data_file.read())
        return characters
