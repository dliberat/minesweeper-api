from enum import Enum
import random
from copy import deepcopy
from typing import List, Tuple

from restapi import const
from restapi.exceptions import InvalidMoveException, GameOverException


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

    @staticmethod
    def set_flag(t):
        return t | 4

    @staticmethod
    def unset_flag(t):
        return t - 4

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

    def is_valid_tile_coords(self, r: int, c: int) -> bool:
        """Check if the specified coordinates
        are within the `tiles` array bounds."""
        return r >= 0 and c >= 0 and r < self.num_rows and c < self.num_cols

    def set_flag(self, r: int, c: int):
        """User sets or unsets a flag or question mark on a tile.

        Args:
            r - Row index of the tile to modify
            c - Column index of the tile to modify

        Returns:
            A new SweeperGame object with the modified tiles array.

        Raises:
            GameOverException if attempting to modify a finished game.

            InvalidMoveException if the coordinates do not correspond
            to a valid location on the grid, or if they correspond
            to a tile that has already been revealed.
        """
        if not self.status == GameStatus.IN_PROGRESS:
            raise GameOverException()

        if not self.is_valid_tile_coords(r, c):
            raise InvalidMoveException('Invalid coordinates (%d, %d)' % (r,c))

        tile = self.tiles[r][c]

        if Tile.is_visible(tile):
            raise InvalidMoveException('Cannot set flag on visible tile')

        clone = SweeperGame.from_tile_arr(self.tiles)

        if not Tile.is_flag(tile):
            clone.tiles[r][c] = Tile.set_flag(tile)
        else:
            clone.tiles[r][c] = Tile.unset_flag(tile)

        return clone

    def reveal_tile(self, r: int, c: int):
        """User clicks on a tile, revealing its contents.
        When a cell with no adjacent mines is revealed,
        all adjacent squares will be revealed recursively.

        If a tile containing a mine is revealed,
        game status is updated to USER LOST.

        If all non-mine tiles have been revealed after this
        move is applied, game status is updated to USER WON.

        Args:
            r - Row index of the tile to reveal
            c - Column index of the tile to reveal

        Returns:
            A new SweeperGame object containing the modified tile array.

        Raises:
            GameOverException if attempting to modify a finished game.

            InvalidMoveException if the coordinates do not correspond
            to a valid location on the grid, or if the chosen tile
            has already been revealed.
        """
        #
        # Basic idiot-proofing
        #
        if not self.status == GameStatus.IN_PROGRESS:
            raise GameOverException()

        if not self.is_valid_tile_coords(r, c):
            raise InvalidMoveException('Invalid coordinates (%d, %d)' % (r,c))

        tile = self.tiles[r][c]

        if Tile.is_visible(tile):
            raise InvalidMoveException('Cannot reveal visible tile')

        #
        # Now the work begins.
        # There are basically two cases.
        # Either the user clicked on a mine, or they didnt.
        #
        clone = SweeperGame.from_tile_arr(self.tiles)

        #
        # Case 1) User clicked on a mine
        #
        if Tile.is_mine(tile):
            clone.tiles[r][c] = Tile.set_visible(tile)
            clone.status = GameStatus.USER_LOST
            return clone


        #
        # Case 2) User clicked on a non-mine. If the clicked
        # tile doesn't have any neighboring mines, we need to
        # check all of its neighbors to see if any of them
        # can also be revealed.
        #
        queue = [(r, c)]

        while queue:
            current, queue = queue[0], queue[1:]
            current_r, current_c = current

            tile = clone.tiles[current_r][current_c]

            if Tile.is_visible(tile):
                # this tile has already been processed
                continue

            clone.tiles[current_r][current_c] = Tile.set_visible(tile)

            neighbors = clone.get_neighbors_to_reveal(current_r, current_c)
            queue += neighbors

        clone.status = clone.check_status()
        return clone

    def get_neighbors_to_reveal(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Returns a list of adjacent tiles that don't contain mines
        and are not already visible.

        Returns:
            List of tuple, where each tuple is (row_index, col_index).
        """
        neighbors = []

        if Tile.count_neighbors(self.tiles[r][c]) != 0:
            # only tiles without adjacent mines get expanded
            return neighbors

        max_r = len(self.tiles) - 1
        max_c = len(self.tiles[0]) - 1
        for i in range(-1, 2):
            for j in range(-1, 2):

                if i == 0 and j == 0:
                    continue

                # array bounds check
                if r+i < 0 or r+i > max_r or c+j < 0 or c+j > max_c:
                    continue

                # don't re-expand visible tiles after we've already revealed them
                if Tile.is_visible(self.tiles[r+i][c+j]):
                    continue

                neighbors.append((r+i, c+j))

        return neighbors
