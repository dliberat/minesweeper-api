
class InvalidMoveException(Exception):
    """Raised when trying to make an invalid move.
    """
    pass

class GameOverException(Exception):
    """Raised when trying to make a move on a finished game.
    """
    pass