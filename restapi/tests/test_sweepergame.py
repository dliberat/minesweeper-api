import unittest

from restapi import const
from restapi.exceptions import InvalidMoveException, GameOverException
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

    def test_set_flag_ok(self):
        gm = SweeperGame.from_tile_arr([
            [1, 8, 0, 0, 0, 0],
            [8, 8, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 8, 8],
            [0, 0, 0, 0, 8, 1],
            [0, 0, 0, 0, 8, 8],
        ])

        clone = gm.set_flag(0, 0)
        self.assertNotEqual(gm, clone)
        self.assertTrue(Tile.is_flag(clone.tiles[0][0]))

        clone2 = clone.set_flag(5, 1)
        self.assertNotEqual(clone, clone2)
        self.assertFalse(Tile.is_flag(clone.tiles[5][1]))
        self.assertTrue(Tile.is_flag(clone2.tiles[5][1]))

    def test_unset_flag_ok(self):
        gm = SweeperGame.from_tile_arr([
            [1, 8, 0, 0, 0, 0],
            [8, 8, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 8, 8],
            [0, 0, 0, 0, 8, 1],
            [0, 0, 0, 0, 8, 8],
        ])

        clone = gm.set_flag(0, 0)
        self.assertNotEqual(gm, clone)
        self.assertTrue(Tile.is_flag(clone.tiles[0][0]))

        clone2 = clone.set_flag(0, 0)
        self.assertNotEqual(clone, clone2)
        self.assertFalse(Tile.is_flag(clone2.tiles[0][0]))


    def test_set_flag_bad_coords(self):
        """Raise exception if the tile is outside of the array bounds.
        """
        gm = SweeperGame.from_tile_arr([
            [1, 8, 0, 0, 0, 0],
            [8, 8, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 8, 8],
            [0, 0, 0, 0, 8, 1],
            [0, 0, 0, 0, 8, 8],
        ])

        self.assertRaises(InvalidMoveException, gm.set_flag, -1, 0)
        self.assertRaises(InvalidMoveException, gm.set_flag, 0, -1)
        self.assertRaises(InvalidMoveException, gm.set_flag, 8, 0)
        self.assertRaises(InvalidMoveException, gm.set_flag, 3, 100)

    def test_set_flag_visible(self):
        """Raise exception if attempting to set flag on a visible tile
        """
        gm = SweeperGame.from_tile_arr([
            [1, 10, 0, 0, 0, 0],
            [8, 8, 0, 0, 0, 0],
            [0, 0, 0, 2, 0, 0],
            [0, 0, 0, 0, 8, 8],
            [0, 0, 0, 0, 8, 1],
            [0, 0, 0, 0, 8, 8],
        ])

        self.assertRaises(InvalidMoveException, gm.set_flag, 0, 1)
        self.assertRaises(InvalidMoveException, gm.set_flag, 2, 3)

    def test_set_flag_game_over(self):
        """Raise exception if attempting to modify a finished game"""
        gm = SweeperGame.from_tile_arr([
            [3, 8, 0, 0, 0, 0],
            [8, 8, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 8, 8],
            [0, 0, 0, 0, 8, 1],
            [0, 0, 0, 0, 8, 8],
        ])
        self.assertRaises(GameOverException, gm.set_flag, 0, 3)

        gm = SweeperGame.from_tile_arr([
            [1, 10, 2, 2, 2, 2],
            [10, 10, 2, 2, 2, 2],
            [2, 2, 2, 2, 2, 2],
            [2, 2, 2, 2, 10, 10],
            [2, 2, 2, 2, 10, 1],
            [2, 2, 2, 2, 10, 10],
        ])
        self.assertRaises(GameOverException, gm.set_flag, 0, 3)

    def test_reveal_tile_bad_coords(self):
        """Raise exception if the tile is outside of the array bounds.
        """
        gm = SweeperGame.from_tile_arr([
            [1, 8, 0, 0, 0, 0],
            [8, 8, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 8, 8],
            [0, 0, 0, 0, 8, 1],
            [0, 0, 0, 0, 8, 8],
        ])

        self.assertRaises(InvalidMoveException, gm.reveal_tile, -1, 0)
        self.assertRaises(InvalidMoveException, gm.reveal_tile, 0, -1)
        self.assertRaises(InvalidMoveException, gm.reveal_tile, 8, 0)
        self.assertRaises(InvalidMoveException, gm.reveal_tile, 3, 100)

    def test_reveal_tile_visible(self):
        """Raise exception if the tile is already revealed"""
        gm = SweeperGame.from_tile_arr([
            [1, 10, 0, 0, 0, 0],
            [8, 8, 0, 0, 0, 0],
            [0, 0, 0, 2, 0, 0],
            [0, 0, 0, 0, 8, 8],
            [0, 0, 0, 0, 8, 1],
            [0, 0, 0, 0, 8, 8],
        ])

        self.assertRaises(InvalidMoveException, gm.reveal_tile, 0, 1)
        self.assertRaises(InvalidMoveException, gm.reveal_tile, 2, 3)

    def test_reveal_tile_user_lost(self):
        """Case where the user reveals a tile with a mine.

        a) Game status should be updated to USER LOST
        b) The revealed tile should be revealed
        c) All other tiles should be unaffected
        """
        gm = SweeperGame.from_tile_arr([
            [1, 10, 0, 0, 0, 0],
            [8, 8, 0, 0, 0, 0],
            [0, 0, 0, 2, 0, 0],
            [0, 0, 0, 0, 8, 8],
            [0, 0, 0, 0, 8, 1],
            [0, 0, 0, 0, 8, 8],
        ])

        clone = gm.reveal_tile(0, 0)
        self.assertNotEqual(gm, clone)
        self.assertEqual(GameStatus.USER_LOST, clone.status)

        for i, row in enumerate(gm.tiles):
            for j, _ in enumerate(row):
                if i == 0 and j == 0:
                    self.assertFalse(Tile.is_visible(gm.tiles[i][j]))
                    self.assertTrue(Tile.is_visible(clone.tiles[i][j]))

                else:

                    self.assertEqual(gm.tiles[i][j], clone.tiles[i][j])


    def test_reveal_tile_game_over(self):
        """Raise exception if attempting to modify a finished game"""
        gm = SweeperGame.from_tile_arr([
            [3, 8, 0, 0, 0, 0],
            [8, 8, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 8, 8],
            [0, 0, 0, 0, 8, 1],
            [0, 0, 0, 0, 8, 8],
        ])
        self.assertRaises(GameOverException, gm.reveal_tile, 0, 3)

        gm = SweeperGame.from_tile_arr([
            [1, 10, 2, 2, 2, 2],
            [10, 10, 2, 2, 2, 2],
            [2, 2, 2, 2, 2, 2],
            [2, 2, 2, 2, 10, 10],
            [2, 2, 2, 2, 10, 1],
            [2, 2, 2, 2, 10, 10],
        ])
        self.assertRaises(GameOverException, gm.reveal_tile, 0, 3)

    def test_reveal_tile_user_won(self):
        gm = SweeperGame.from_tile_arr([
            [1, 10, 2, 2, 2, 2],
            [10, 10, 2, 2, 2, 2],
            [2, 2, 2, 2, 2, 2],
            [2, 2, 2, 2, 10, 10],
            [2, 2, 2, 2, 10, 1],
            [2, 2, 2, 2, 10, 8],
        ])

        clone = gm.reveal_tile(5, 5)
        self.assertNotEqual(gm, clone)
        self.assertEqual(GameStatus.USER_WON, clone.status)

    def test_reveal_tile_no_recursion(self):
        gm = SweeperGame.from_tile_arr([
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [8, 8, 8, 8, 8, 8],
            [8, 1, 8, 8, 1, 8],
            [8, 8, 8, 8, 8, 8],
            [0, 0, 0, 0, 0, 0],
        ])
        clone = gm.reveal_tile(2, 1)

        for i, row in enumerate(gm.tiles):
            for j, _ in enumerate(row):
                if i == 2 and j == 1:
                    self.assertEqual(10, clone.tiles[i][j])
                    self.assertEqual(8, gm.tiles[i][j])
                else:
                    self.assertEqual(gm.tiles[i][j], clone.tiles[i][j])

    def test_reveal_tile_recursive(self):
        gm = SweeperGame.from_tile_arr([
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [8, 8, 8, 8, 8, 8],
            [8, 1, 8, 8, 1, 8],
            [8, 8, 8, 8, 8, 8],
            [0, 0, 0, 0, 0, 0],
        ])
        clone = gm.reveal_tile(0, 0)
        expected = [
            [2, 2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2, 2],
            [10, 10, 10, 10, 10, 10],
            [8, 1, 8, 8, 1, 8],
            [8, 8, 8, 8, 8, 8],
            [0, 0, 0, 0, 0, 0],
        ]
        for i, row in enumerate(clone.tiles):
            self.assertListEqual(expected[i], row)


    def test_get_neighbors_to_reveal_has_adjacent_mine(self):
        gm = SweeperGame.from_tile_arr([
            [1, 16, 0, 0, 0, 0],
            [1, 16, 8, 8, 8, 0],
            [8, 8, 8, 1, 8, 0],
            [0, 0, 8, 8, 8, 0],
            [0, 0, 0, 8, 8, 8],
            [0, 0, 0, 8, 1, 8],
        ])

        for r, c in [(0,1), (1,1), (1,3), (3,2), (5,5)]:
            res = gm.get_neighbors_to_reveal(r, c)
            self.assertListEqual([], res)

    def test_get_neighbors_to_reveal_no_adjacent_mine(self):
        gm = SweeperGame.from_tile_arr([
            [1, 16, 0, 0, 0, 0],
            [1, 16, 8, 8, 8, 0],
            [8, 8, 8, 1, 8, 0],
            [0, 0, 8, 8, 8, 0],
            [0, 0, 0, 8, 8, 8],
            [0, 0, 0, 8, 1, 8],
        ])

        res = gm.get_neighbors_to_reveal(4, 1)
        expected = [
            (3,0), (3,1), (3,2),
            (4,0), (4,2),
            (5,0), (5,1), (5,2)
        ]
        self.assertListEqual(sorted(expected), sorted(res))

    def test_get_neighbors_to_reveal_array_bounds(self):
        gm = SweeperGame.from_tile_arr([
            [1, 16, 0, 0, 0, 0],
            [1, 16, 8, 8, 8, 0],
            [8, 8, 8, 1, 8, 0],
            [0, 0, 8, 8, 8, 0],
            [0, 0, 0, 8, 8, 8],
            [0, 0, 0, 8, 1, 8],
        ])

        res = gm.get_neighbors_to_reveal(0, 5)
        expected = [(0,4), (1,4), (1,5)]
        self.assertListEqual(sorted(expected), sorted(res))

        res = gm.get_neighbors_to_reveal(5, 2)
        expected = [(5,1), (5,3), (4,1), (4,2), (4,3)]
        self.assertListEqual(sorted(expected), sorted(res))
