import os
from src.request_handler.state.passhash import makeSalt, hashPassword
from src.request_handler.state.command_handler import CommandHandler


class LoginManager(CommandHandler):
    SALT_FILENAME = 'SALT'
    HASHED_PASSWORD_FILENAME = 'HASHED_PASSWORD'

    def __init__(self):
        super().__init__()

    def handle_request(self, command, world_state):
        response = super().handle_request(command, world_state)
        username = command.ident
        password = command.args

        os.makedirs(self.ACCOUNTS_DIRECTORY, exist_ok=True)
        path = f'./{self.ACCOUNTS_DIRECTORY}/{username}'

        if not os.path.isdir(path):
            return self.create_user(path, password, response)
        try:
            with open(f'{path}/{self.SALT_FILENAME}', 'r') as salt:
                with open(f'{path}/{self.HASHED_PASSWORD_FILENAME}', 'r') as hashed_password:
                    # read the password hashed
                    incoming_hash = hashPassword(password, salt.read())
                    true_hash = hashed_password.read()
                    if incoming_hash == true_hash:
                        print(f'password accepted for {username}')
                        return response.set_response_success(True)
                    else:
                        print(f'password not accepted for {username}')
                        return response.set_response_success(False)
        except OSError:
            print(f'Could not find login information for user: {username}')
            return response.set_response_success(False)

    def create_user(self, path, password, response):
        try:
            os.mkdir(path)
        except OSError:
            print(f'Creation of the directory {path} failed')
            return response.set_response_success(False)
        print(f'Successfully created the directory {path}')

        salt = makeSalt()
        with open(f'{path}/{self.SALT_FILENAME}', 'w') as f:
            # write the password salt
            f.write(str(salt))

        with open(f'{path}/{self.HASHED_PASSWORD_FILENAME}', 'w') as f:
            # write the password hashed
            f.write(str(hashPassword(password, salt)))

        return response.set_response_success(True)
