import unittest

from restapi.sweepergame import Tile

class TileTest(unittest.TestCase):

    def test_is_mine(self):
        self.assertFalse(Tile.is_mine(int('000000', 2)))
        self.assertFalse(Tile.is_mine(int('000010', 2)))
        self.assertFalse(Tile.is_mine(int('000100', 2)))
        self.assertFalse(Tile.is_mine(int('001010', 2)))
        self.assertTrue(Tile.is_mine(int('000001', 2)))
        self.assertTrue(Tile.is_mine(int('000011', 2)))
        self.assertTrue(Tile.is_mine(int('000101', 2)))
        self.assertTrue(Tile.is_mine(int('001001', 2)))
        self.assertTrue(Tile.is_mine(int('010011', 2)))

    def test_set_mine(self):
        t = int('000000', 2)
        t = Tile.set_mine(t)
        self.assertTrue(Tile.is_mine(t))

        t = int('011010', 2)
        t = Tile.set_mine(t)
        self.assertTrue(Tile.is_mine(t))

    def test_is_visible(self):
        self.assertFalse(Tile.is_visible(int('000000', 2)))
        self.assertFalse(Tile.is_visible(int('000001', 2)))
        self.assertFalse(Tile.is_visible(int('010001', 2)))
        self.assertFalse(Tile.is_visible(int('011101', 2)))
        self.assertTrue(Tile.is_visible(int('000010', 2)))
        self.assertTrue(Tile.is_visible(int('000011', 2)))
        self.assertTrue(Tile.is_visible(int('010011', 2)))
        self.assertTrue(Tile.is_visible(int('011111', 2)))

    def test_set_visible(self):
        t = int('000000', 2)
        t = Tile.set_visible(t)
        self.assertTrue(Tile.is_visible(t))

        t = int('001000', 2)
        t = Tile.set_visible(t)
        self.assertTrue(Tile.is_visible(t))

    def test_is_flag(self):
        self.assertFalse(Tile.is_flag(int('000000', 2)))
        self.assertFalse(Tile.is_flag(int('000001', 2)))
        self.assertFalse(Tile.is_flag(int('010001', 2)))
        self.assertFalse(Tile.is_flag(int('011001', 2)))
        self.assertTrue(Tile.is_flag(int('000100', 2)))
        self.assertTrue(Tile.is_flag(int('000111', 2)))
        self.assertTrue(Tile.is_flag(int('010101', 2)))
        self.assertTrue(Tile.is_flag(int('011111', 2)))

    def test_set_flag(self):
        t = int('000000', 2)
        t = Tile.set_flag(t)
        self.assertTrue(Tile.is_flag(t))

        t = int('000001', 2)
        t = Tile.set_flag(t)
        self.assertTrue(Tile.is_flag(t))

    def test_unset_flag(self):
        t = int('000100', 2)
        t = Tile.unset_flag(t)
        self.assertFalse(Tile.is_flag(t))
        self.assertFalse(Tile.is_mine(t))
        self.assertEqual(0, Tile.count_neighbors(t))

        t = int('010101', 2)
        t = Tile.unset_flag(t)
        self.assertFalse(Tile.is_flag(t))
        self.assertTrue(Tile.is_mine(t))
        self.assertEqual(2, Tile.count_neighbors(t))



    def test_count_neighbors(self):
        t = int('001000', 2)
        self.assertEqual(1, Tile.count_neighbors(t))

        t = int('010000', 2)
        self.assertEqual(2, Tile.count_neighbors(t))

        t = int('011000', 2)
        self.assertEqual(3, Tile.count_neighbors(t))

        t = int('100000', 2)
        self.assertEqual(4, Tile.count_neighbors(t))

        t = int('001001', 2)
        self.assertEqual(1, Tile.count_neighbors(t))

        t = int('101101', 2)
        self.assertEqual(5, Tile.count_neighbors(t))

    def test_add_neighbor(self):

        for seed in ['000000', '000001', '000101']:
            t = int(seed, 2)
            t = Tile.add_neighbor(t)
            self.assertEqual(1, Tile.count_neighbors(t))

            t = Tile.add_neighbor(t)
            self.assertEqual(2, Tile.count_neighbors(t))

            t = Tile.add_neighbor(t)
            self.assertEqual(3, Tile.count_neighbors(t))

            t = Tile.add_neighbor(t)
            self.assertEqual(4, Tile.count_neighbors(t))
