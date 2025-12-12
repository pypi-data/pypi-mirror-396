class ResourceNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ConnectAPIError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UnauthorisedError(Exception):
    def __init__(self, message):
        super().__init__(message)
