class UnexpectedTypeError(Exception):
    pass

class MissingArgument(Exception):
    pass

class ConstantError(Exception):
    def __init__(self, message: str = "Cannot modify a constant") -> None:
        super().__init__(message)