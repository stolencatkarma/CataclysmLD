class CommandResponse:
    RESPONSE_SUCCESS = 'SUCCESS'
    RESPONSE_FAILURE = 'FAILURE'

    def __init__(self):
        self.name = ''
        self.status = ''
        self.args = dict()

    def set_response_success(self, success):
        self.status = CommandResponse.RESPONSE_SUCCESS if success else CommandResponse.RESPONSE_FAILURE
        return self
