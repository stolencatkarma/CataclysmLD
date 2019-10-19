from src.request_handler.state.command_handler import CommandHandler


class LocalmapUpdateHandler(CommandHandler):
    def __init__(self):
        super().__init__()

    def handle_request(self, command, world_state):
        response = super().handle_request(command, world_state)
        character = world_state.characters[command.args] = world_state.worldmap.get_character(command.args)
        world_state.localmaps[command.args] = world_state.worldmap.get_chunks_near_position(
            world_state.characters[command.args]['position']
        )
        response.args['localmap'] = world_state.localmaps[command.args]
        return response.set_response_success(True) if character is not None else response.set_response_success(False)
