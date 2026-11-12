import unittest

from pokedex import REGIONS, region_of, region_range


class RegionRangeTest(unittest.TestCase):
    """Region name -> national dex number range (first, last), both inclusive."""

    def test_kanto(self):
        self.assertEqual(region_range("관동"), (1, 151))

    def test_johto(self):
        self.assertEqual(region_range("성도"), (152, 251))

    def test_hoenn(self):
        self.assertEqual(region_range("호연"), (252, 386))

    def test_unknown_region_raises(self):
        with self.assertRaises(ValueError):
            region_range("없는지역")


class RegionOrderTest(unittest.TestCase):
    """Regions are loaded in this order while scrolling down."""

    def test_starts_with_kanto_then_johto_then_hoenn(self):
        self.assertEqual(REGIONS[:3], ["관동", "성도", "호연"])

    def test_ranges_are_contiguous(self):
        previous_last = 0
        for name in REGIONS:
            first, last = region_range(name)
            self.assertEqual(first, previous_last + 1, name)
            self.assertLessEqual(first, last, name)
            previous_last = last


class RegionOfTest(unittest.TestCase):
    """National dex number -> the region it belongs to (None if outside every region).

    Used to load regions up to a Pokemon opened by ?pokemon=<id>, since opening
    a card reloads the page and forgets how many regions were loaded.
    """

    def test_region_edges(self):
        self.assertEqual(region_of(1), "관동")
        self.assertEqual(region_of(151), "관동")
        self.assertEqual(region_of(152), "성도")
        self.assertEqual(region_of(200), "성도")
        self.assertEqual(region_of(1025), "팔데아")

    def test_outside_every_region_is_none(self):
        self.assertIsNone(region_of(0))
        self.assertIsNone(region_of(-5))
        self.assertIsNone(region_of(1026))


if __name__ == "__main__":
    unittest.main()
