import unittest

from pokedex import evolution_stages, last_level_up_moves, radar_points, stats_to_radar

PIKACHU_STATS = [
    {"stat": "hp", "value": 35},
    {"stat": "attack", "value": 55},
    {"stat": "defense", "value": 40},
    {"stat": "special-attack", "value": 50},
    {"stat": "special-defense", "value": 50},
    {"stat": "speed", "value": 90},
]


class StatsToRadarTest(unittest.TestCase):
    """Base stats -> data points for the six-axis radar chart."""

    def test_six_axes_in_fixed_order_with_korean_labels(self):
        data = stats_to_radar(PIKACHU_STATS)
        self.assertEqual(
            [d["label"] for d in data],
            ["HP", "공격", "방어", "특수공격", "특수방어", "스피드"],
        )
        self.assertEqual([d["value"] for d in data], [35, 55, 40, 50, 50, 90])

    def test_order_does_not_depend_on_input_order(self):
        data = stats_to_radar(list(reversed(PIKACHU_STATS)))
        self.assertEqual([d["value"] for d in data], [35, 55, 40, 50, 50, 90])

    def test_ratio_is_value_over_max(self):
        data = stats_to_radar(PIKACHU_STATS, max_value=100)
        self.assertAlmostEqual(data[0]["ratio"], 0.35)
        self.assertAlmostEqual(data[5]["ratio"], 0.9)

    def test_ratio_is_capped_at_one(self):
        stats = [{"stat": "hp", "value": 300}]
        self.assertEqual(stats_to_radar(stats, max_value=255)[0]["ratio"], 1.0)

    def test_missing_stat_is_zero(self):
        data = stats_to_radar([{"stat": "hp", "value": 35}])
        self.assertEqual(len(data), 6)
        self.assertEqual(data[1]["value"], 0)
        self.assertEqual(data[1]["ratio"], 0)


class RadarPointsTest(unittest.TestCase):
    """Ratios -> polygon corner coordinates, first axis pointing straight up."""

    def test_full_ratios_make_a_hexagon_on_the_radius(self):
        points = radar_points([1] * 6, radius=100, cx=0, cy=0)
        self.assertEqual(len(points), 6)
        self.assertAlmostEqual(points[0][0], 0)
        self.assertAlmostEqual(points[0][1], -100)  # top
        self.assertAlmostEqual(points[3][0], 0)
        self.assertAlmostEqual(points[3][1], 100)  # bottom
        for x, y in points:
            self.assertAlmostEqual((x * x + y * y) ** 0.5, 100)

    def test_zero_ratio_sits_on_the_center(self):
        points = radar_points([0] * 6, radius=100, cx=50, cy=60)
        for x, y in points:
            self.assertAlmostEqual(x, 50)
            self.assertAlmostEqual(y, 60)

    def test_half_ratio_is_half_way(self):
        points = radar_points([0.5] * 6, radius=100, cx=0, cy=0)
        self.assertAlmostEqual(points[0][1], -50)


def move(name, level, version_group=1, order=None, type_="노말"):
    return {
        "name": name,
        "type": type_,
        "level": level,
        "order": order,
        "version_group": version_group,
    }


class LastLevelUpMovesTest(unittest.TestCase):
    """Level-up move list -> the four moves learned last."""

    def test_picks_four_highest_levels_in_level_order(self):
        moves = [
            move("a", 1),
            move("e", 50),
            move("b", 10),
            move("d", 40),
            move("c", 20),
            move("f", 60),
        ]
        self.assertEqual([m["name"] for m in last_level_up_moves(moves)], ["c", "d", "e", "f"])

    def test_returns_name_type_and_level(self):
        result = last_level_up_moves([move("10만볼트", 26, type_="전기")])
        self.assertEqual(result, [{"name": "10만볼트", "type": "전기", "level": 26}])

    def test_fewer_than_four_returns_all(self):
        moves = [move("a", 1), move("b", 5)]
        self.assertEqual([m["name"] for m in last_level_up_moves(moves)], ["a", "b"])

    def test_empty_list(self):
        self.assertEqual(last_level_up_moves([]), [])

    def test_uses_only_the_latest_version_group(self):
        moves = [
            move("old-high", 99, version_group=1),
            move("new-a", 5, version_group=20),
            move("new-b", 10, version_group=20),
        ]
        self.assertEqual([m["name"] for m in last_level_up_moves(moves)], ["new-a", "new-b"])

    def test_same_move_counted_once_at_its_highest_level(self):
        moves = [move("a", 1), move("b", 10), move("a", 30)]
        self.assertEqual([m["name"] for m in last_level_up_moves(moves)], ["b", "a"])

    def test_same_level_uses_order(self):
        moves = [move("y", 1, order=2), move("x", 1, order=1)]
        self.assertEqual([m["name"] for m in last_level_up_moves(moves)], ["x", "y"])

    def test_count_can_be_changed(self):
        moves = [move("a", 1), move("b", 2), move("c", 3)]
        self.assertEqual([m["name"] for m in last_level_up_moves(moves, count=2)], ["b", "c"])


class EvolutionStagesTest(unittest.TestCase):
    """Species in an evolution chain -> stages from first to last."""

    def test_pikachu_line(self):
        species = [
            {"id": 25, "evolves_from": 172},
            {"id": 26, "evolves_from": 25},
            {"id": 172, "evolves_from": None},
        ]
        stages = evolution_stages(species)
        self.assertEqual([[s["id"] for s in stage] for stage in stages], [[172], [25], [26]])

    def test_branches_share_a_stage(self):
        species = [
            {"id": 133, "evolves_from": None},
            {"id": 136, "evolves_from": 133},
            {"id": 134, "evolves_from": 133},
            {"id": 135, "evolves_from": 133},
        ]
        stages = evolution_stages(species)
        self.assertEqual([[s["id"] for s in stage] for stage in stages], [[133], [134, 135, 136]])

    def test_single_species(self):
        stages = evolution_stages([{"id": 128, "evolves_from": None}])
        self.assertEqual([[s["id"] for s in stage] for stage in stages], [[128]])


if __name__ == "__main__":
    unittest.main()
