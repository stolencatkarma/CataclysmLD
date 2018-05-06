class MastermindError(Exception):
    def __init__(self,error_message):
        self._mm_error_message = error_message
        Exception.__init__(self)
    def __str__(self):
        return repr(self._mm_error_message)
class MastermindErrorClient(MastermindError):
    def __init__(self,error_message): MastermindError.__init__(self,error_message)
class MastermindErrorServer(MastermindError):
    def __init__(self,error_message): MastermindError.__init__(self,error_message)
class MastermindErrorSocket(MastermindError):
    def __init__(self,error_message): MastermindError.__init__(self,error_message)

class MastermindWarning(object):
    def __init__(self,error_message):
        print(error_message)
class MastermindWarningClient(MastermindWarning):
    def __init__(self,error_message): MastermindWarning.__init__(self,error_message)
class MastermindWarningServer(MastermindWarning):
    def __init__(self,error_message): MastermindWarning.__init__(self,error_message)
