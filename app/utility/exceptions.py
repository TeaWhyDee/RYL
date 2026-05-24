class RYLException(Exception):
    """
    Base class for RYL exceptions
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class RYLBadUsername(RYLException):
    pass


class RYLBadPassword(RYLException):
    pass


class RYLAlreadyExists(RYLException):
    pass


class RYLNotFound(RYLException):
    pass


class RYLInternalError(RYLException):
    pass
