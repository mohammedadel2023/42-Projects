class CommandNotFound(Exception):
    """error message for command not foud problem"""
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InappropriateQuery(Exception):
    """error message for unvalid query"""
    def __init__(self, message: str) -> None:
        super().__init__(message)


class TruthQuestionNotFound(Exception):
    "error when the truth source missing"
    def __init__(self, message: str) -> None:
        super().__init__(message)
