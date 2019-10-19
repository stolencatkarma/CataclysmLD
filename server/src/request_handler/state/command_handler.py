import re
from src.request_handler.state.command_response import CommandResponse


class CommandHandler:
    REQUEST_PREFIX = "request_"
    ACCOUNTS_DIRECTORY = 'accounts'

    def __init__(self):
        self.response_name = ''

    def handle_request(self, command, world_state):
        if not re.match(f"^{self.REQUEST_PREFIX}", command.command_name):
            raise Exception(f"Invalid request prefix in request: {command.command_name}")
        response = CommandResponse()
        response.name = command.command_name[len(self.REQUEST_PREFIX):]
        return response
