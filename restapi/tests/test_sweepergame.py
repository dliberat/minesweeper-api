import unittest

from restapi import const
from restapi.sweepergame import SweeperGame, Tile, GameStatus

class TestSweeperGame(unittest.TestCase):

    def test_new_game_dimensions(self):
        """Check that the game has the correct number of
        rows, columns, and mines"""
        dims = [
            (6, 6, 6),
            (8, 6, 2),
            (10, 12, 19),
            (14, 14, 78),
            (20, 20, 99),
        ]
        for r, c, m in dims:
            game = SweeperGame(r, c, m)

            # First, check the properties
            self.assertEqual(r, game.num_rows)
            self.assertEqual(c, game.num_cols)
            self.assertEqual(m, game.num_mines)

            # Then check that the game board
            # actually conforms for those specs.
            # Correct number of rows
            self.assertEqual(r, len(game.tiles))

            # Correct number of columns
            for row in game.tiles:
                self.assertEqual(c, len(row))

            # Correct number of mines
            mines = 0
            for row in game.tiles:
                for val in row:
                    if Tile.is_mine(val):
                        mines += 1
            self.assertEqual(m, mines)

    def test_new_game_all_tiles_hidden(self):
        game = SweeperGame(10, 10, 30)
        for row in game.tiles:
            for val in row:
                self.failIf(Tile.is_visible(val))

    def test_new_game_no_flags(self):
        game = SweeperGame(10, 10, 30)
        for row in game.tiles:
            for val in row:
                self.failIf(Tile.is_flag(val))

    def test_new_game_status(self):
        game = SweeperGame(20, 20, 20)
        self.assertEqual(GameStatus.IN_PROGRESS, game.status)

    def neighbor_count(self, tiles, r, c):
        neighbors = 0

        # three tiles above
        if r > 0:
            rr = r-1
            if Tile.is_mine(tiles[rr][c]):
                neighbors += 1
            if c > 0 and Tile.is_mine(tiles[rr][c-1]):
                neighbors += 1
            if c+1 < len(tiles[rr]) and Tile.is_mine(tiles[rr][c+1]):
                neighbors += 1

        # left and right
        if c > 0 and Tile.is_mine(tiles[r][c-1]):
            neighbors += 1
        if c+1 < len(tiles[r-1]) and Tile.is_mine(tiles[r][c+1]):
            neighbors += 1

        # three tiles below
        if r+1 < len(tiles):
            rr = r+1
            if Tile.is_mine(tiles[rr][c]):
                neighbors += 1
            if c > 0 and Tile.is_mine(tiles[rr][c-1]):
                neighbors += 1
            if c+1 < len(tiles[rr]) and Tile.is_mine(tiles[rr][c+1]):
                neighbors += 1

        return neighbors

    def test_neighbor_count(self):
        dims = [
            (6, 6, 6),
            (8, 6, 2),
            (10, 12, 19),
            (14, 14, 78),
            (20, 20, 99),
        ]
        for r, c, m in dims:
            game = SweeperGame(r, c, m)

            for i, row in enumerate(game.tiles):
                for j, tile in enumerate(row):
                    expected = Tile.count_neighbors(tile)
                    actual = self.neighbor_count(game.tiles, i, j)
                    self.assertEqual(expected, actual)

    def test_check_status_in_progress(self):
        gm = SweeperGame(6, 6, 6)
        status = gm.check_status()
        self.assertEqual(GameStatus.IN_PROGRESS, status)

        gm = SweeperGame.from_tile_arr([
            [8, 8, 10, 2, 2, 2],
            [8, 1, 10, 2, 2, 2],
            [8, 8, 10, 2, 2, 2],
            [0, 0, 0, 10, 10, 10],
            [0, 0, 0, 8, 1, 8],
            [0, 0, 0, 8, 8, 8],
        ])
        status = gm.check_status()
        self.assertEqual(GameStatus.IN_PROGRESS, status)

    def test_check_status_user_lost(self):

        # user clicked the bomb at (4, 4)
        gm = SweeperGame.from_tile_arr([
            [8, 8, 10, 2, 2, 2],
            [8, 1, 10, 2, 2, 2],
            [8, 8, 10, 2, 2, 2],
            [0, 0, 0, 10, 10, 10],
            [0, 0, 0, 8, 3, 8],
            [0, 0, 0, 8, 8, 8],
        ])
        status = gm.check_status()
        self.assertEqual(GameStatus.USER_LOST, status)


        # user clicked the bomb at (0, 0)
        gm = SweeperGame.from_tile_arr([
            [3, 8, 0, 0, 0, 0],
            [8, 8, 0, 0, 0, 0],
            [0, 0, 0, 0, 8, 8],
            [0, 0, 0, 0, 8, 1],
            [0, 0, 0, 0, 8, 8],
            [0, 0, 0, 0, 0, 0],
        ])
        status = gm.check_status()
        self.assertEqual(GameStatus.USER_LOST, status)


    def test_check_status_user_won(self):

        gm = SweeperGame.from_tile_arr([
            [1, 10, 2, 2, 2, 2],
            [10, 10, 2, 2, 2, 2],
            [2, 2, 2, 2, 10, 10],
            [2, 2, 2, 2, 10, 5],
            [2, 2, 2, 2, 10, 10],
            [2, 2, 2, 2, 2, 2],
        ])
        status = gm.check_status()
        self.assertEqual(GameStatus.USER_WON, status)
