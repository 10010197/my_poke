import unittest

from pokedex import REGIONS, next_region


class NextRegionTest(unittest.TestCase):
    """Number of regions already on the page -> the region to load next (None at the end)."""

    def test_after_kanto_comes_johto(self):
        self.assertEqual(next_region(1), "성도")

    def test_order_follows_regions(self):
        for loaded in range(len(REGIONS)):
            self.assertEqual(next_region(loaded), REGIONS[loaded])

    def test_last_region_is_paldea(self):
        self.assertEqual(next_region(len(REGIONS) - 1), "팔데아")

    def test_nothing_after_the_last_region(self):
        self.assertIsNone(next_region(len(REGIONS)))
        self.assertIsNone(next_region(len(REGIONS) + 3))

    def test_negative_count_is_invalid(self):
        with self.assertRaises(ValueError):
            next_region(-1)


if __name__ == "__main__":
    unittest.main()
