from enum import Enum
import random
from copy import deepcopy
from typing import List

from restapi import const


class GameStatus(Enum):
    IN_PROGRESS = 0
    USER_WON = 1
    USER_LOST = 2


class Tile():
    """Tiles are represented with 6 bits.

    +---------------- Number of neighbors containing mines
    |     +---------- Flag state. Flagged (1) or not (0).
    |     | +-------- Visibility state. Open (1) or not (0).
    |     | | +------ Is mine (1) or not (0)
    |     | | |
    0 0 0 0 0 0
    """

    @staticmethod
    def is_mine(t):
        return t%2 == 1

    @staticmethod
    def set_mine(t):
        return t | 1

    @staticmethod
    def is_visible(t):
        return (t >> 1) % 2 == 1

    @staticmethod
    def set_visible(t):
        return t | 2

    @staticmethod
    def is_flag(t):
        return (t >> 2) % 2 == 1

    def set_flag(t):
        return t | 4

    @staticmethod
    def add_neighbor(t):
        return t + (1 << 3)

    @staticmethod
    def count_neighbors(t):
        return t >> 3


class SweeperGame():
    """Represents a game state.
    """

    def __init__(self, num_rows: int,
                       num_cols: int,
                       num_mines: int,
                       set_mines: bool=True):
        """
        Args:
            num_rows - Number of rows
            num_cols - Number of columns
            num_mines - Number of mines
            set_mines - If true, `num_mines` will be placed
                on the grid in random locations.
                Set this to False and modify the `tiles`
                property to create a grid manually
        """
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_mines = num_mines
        self.status = GameStatus.IN_PROGRESS
        self.tiles = [[0]*num_cols for _ in range(num_rows)]

        if set_mines:
            self.set_mines()

    @staticmethod
    def from_tile_arr(tiles: List[List[int]]):
        """Creates a SweeperGame instance from the provided
        game state.
        """

        num_rows = len(tiles)
        num_cols = len(tiles[0])
        num_mines = 0
        for row in tiles:
            for tile in row:
                if Tile.is_mine(tile):
                    num_mines += 1
        gm = SweeperGame(num_rows, num_cols, num_mines, set_mines=False)
        gm.tiles = deepcopy(tiles)
        gm.status = gm.check_status()
        return gm

    def set_mines(self):
        """Place mines in random locations on the grid.
        """
        remaining = self.num_mines

        while remaining > 0:
            r = random.randint(0, self.num_rows-1)
            c = random.randint(0, self.num_cols-1)

            tile = self.tiles[r][c]
            if not Tile.is_mine(tile):
                self.tiles[r][c] = Tile.set_mine(tile)
                self.increment_neighbors(r, c)
                remaining -= 1

    def increment_neighbors(self, r: int, c: int):
        """Add 1 to the neighbor count of all 9 cells
        surrounding the specified location.

        Args:
            r - Row of the center cell
            c - column of the center cell
        """
        max_r = len(self.tiles) - 1
        max_c = len(self.tiles[0]) - 1

        for i in range(-1, 2):
            for j in range(-1, 2):

                # don't increment neighbors for center tile
                if i == 0 and j == 0:
                    continue

                # array bounds check
                if r+i < 0 or r+i > max_r or c+j < 0 or c+j > max_c:
                    continue

                tile = self.tiles[r+i][c+j]
                self.tiles[r+i][c+j] = Tile.add_neighbor(tile)

    def check_status(self) -> GameStatus:
        """Determine the status of the game

        Returns:
            GameStatus.USER_LOST if the user has revealed a mine.
            GameStatus.USER_WON if the user has revealed all non-mine tiles.
            GameStatus.IN_PROGRESS otherwise.
        """

        user_can_win = True

        for row in self.tiles:
            for tile in row:
                if Tile.is_visible(tile) and Tile.is_mine(tile):
                    return GameStatus.USER_LOST

                if not Tile.is_mine(tile) and not Tile.is_visible(tile):
                    # if there are any non-mine tiles
                    # which are still uncovered, then the user
                    # still has work to do (or they've lost)
                    user_can_win = False

        if user_can_win:
            return GameStatus.USER_WON

        return GameStatus.IN_PROGRESS