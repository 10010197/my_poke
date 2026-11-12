import unittest

from pokedex import UNKNOWN_TYPE_COLOR, badge_text_color, type_color


class TypeColorTest(unittest.TestCase):
    """Type name -> badge color, values from the color chart in issue #9 ("보통" column)."""

    def test_fire(self):
        self.assertEqual(type_color("불꽃"), "#E62829")

    def test_water(self):
        self.assertEqual(type_color("물"), "#2980EF")

    def test_grass(self):
        self.assertEqual(type_color("풀"), "#3FA129")

    def test_electric(self):
        self.assertEqual(type_color("전기"), "#FAC000")

    def test_unknown_type_is_gray(self):
        self.assertEqual(type_color("없는속성"), UNKNOWN_TYPE_COLOR)
        self.assertEqual(UNKNOWN_TYPE_COLOR, "#9A9A9A")

    def test_grass_and_poison_differ(self):
        self.assertNotEqual(type_color("풀"), type_color("독"))


class BadgeTextColorTest(unittest.TestCase):
    """Text color that reads best on a given badge background."""

    def test_dark_background_gets_white_text(self):
        self.assertEqual(badge_text_color("#704170"), "#FFFFFF")  # 고스트

    def test_light_background_gets_black_text(self):
        self.assertEqual(badge_text_color("#FAC000"), "#000000")  # 전기

    def test_white_and_black_extremes(self):
        self.assertEqual(badge_text_color("#000000"), "#FFFFFF")
        self.assertEqual(badge_text_color("#FFFFFF"), "#000000")


if __name__ == "__main__":
    unittest.main()
