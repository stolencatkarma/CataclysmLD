from src.request_handler.state.command_handler import CommandHandler


class ChooseCharacterHandler(CommandHandler):
    def __init__(self):
        super().__init__()

    def handle_request(self, command, world_state):
        response = super().handle_request(command, world_state)
        character = world_state.characters[command.args] = world_state.worldmap.get_character(command.args)
        success = self.can_choose_character(character)
        response.args['character'] = character
        return response.set_response_success(success)

    def can_choose_character(self, character):
        # TODO: validate that this character belongs to the user making the request, and any other validation you can think of.
        return character is not None
