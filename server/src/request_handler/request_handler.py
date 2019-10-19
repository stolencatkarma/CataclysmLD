import json

from src.blueprint import Blueprint
from src.position import Position
from src.request_handler.action.action_handler import ActionHandler
from src.request_handler.state.character_request_handler import CharacterRequestHandler
from src.request_handler.state.choose_character_handler import ChooseCharacterHandler
from src.request_handler.state.command_response import CommandResponse
from src.request_handler.state.completed_character_handler import CompletedCharacterHandler
from src.request_handler.state.localmap_update_handler import LocalmapUpdateHandler
from src.request_handler.state.login_manager import LoginManager


class RequestHandler:
    def __init__(self, logger, managers, state_callback):
        self.logger = logger
        self.state_callback = state_callback

        self.command_handlers = {
            "request_login": LoginManager(),
            "request_character_list": CharacterRequestHandler(),
            "request_completed_character": CompletedCharacterHandler(managers.profession_manager, managers.item_manager, self.logger),
            "request_choose_character": ChooseCharacterHandler(),
            "request_localmap_update": LocalmapUpdateHandler()
        }
        self.action_handler = ActionHandler(self.logger, managers.recipe_manager)

    def handle_request(self, command, world_state, connection_object):
        command_name = command.command_name
        if command_name in self.command_handlers:
            command_handler = self.command_handlers[command_name]
            response = command_handler.handle_request(command, world_state)
            self.state_callback(connection_object, json.dumps(response.__dict__))

            if isinstance(command_handler, LoginManager) and response.status == CommandResponse.RESPONSE_FAILURE:
                connection_object.terminate()
            return

        if self.action_handler.can_handle(command_name):
            # all the commands that are actions need to be put into the command_queue then we will loop through the queue each turn and process the actions.
            self.action_handler.handle_request(command, world_state)
