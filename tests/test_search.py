import unittest

from pokedex import generation_of, parse_dex_number, search_pokemon


def mon(pid, name, *types):
    return {"id": pid, "name": name, "types": list(types), "image": None}


POKEMON = [
    mon(4, "파이리", "불꽃"),
    mon(5, "리자드", "불꽃"),
    mon(6, "리자몽", "불꽃", "비행"),
    mon(7, "꼬부기", "물"),
    mon(25, "피카츄", "전기"),
    mon(125, "에레브", "전기"),
    mon(130, "갸라도스", "물", "비행"),
    mon(155, "브케인", "불꽃"),
    mon(250, "칠색조", "불꽃", "비행"),
]


def ids(result):
    return [p["id"] for p in result]


class ParseDexNumberTest(unittest.TestCase):
    """Text typed in the search box -> dex number, or None if it isn't a number."""

    def test_number_formats(self):
        for text in ("25", "025", "No.25", "no.25", "NO.025", "#25", " 25 "):
            self.assertEqual(parse_dex_number(text), 25, text)

    def test_not_a_number(self):
        for text in ("", "피카", "25a", "No.", None):
            self.assertIsNone(parse_dex_number(text), text)


class GenerationOfTest(unittest.TestCase):
    """Dex number -> generation (1 = 관동 ... 9 = 팔데아), None if outside."""

    def test_generations(self):
        self.assertEqual(generation_of(1), 1)
        self.assertEqual(generation_of(151), 1)
        self.assertEqual(generation_of(152), 2)
        self.assertEqual(generation_of(1025), 9)

    def test_outside(self):
        self.assertIsNone(generation_of(0))
        self.assertIsNone(generation_of(1026))


class SearchPokemonTest(unittest.TestCase):
    def test_name_partial_match(self):
        self.assertEqual(ids(search_pokemon(POKEMON, query="리자")), [5, 6])

    def test_unknown_name_finds_nothing(self):
        self.assertEqual(search_pokemon(POKEMON, query="없는포켓몬"), [])

    def test_number_finds_exactly_that_number(self):
        for text in ("25", "025", "No.25"):
            self.assertEqual(ids(search_pokemon(POKEMON, query=text)), [25], text)

    def test_generation_and_type(self):
        result = ids(search_pokemon(POKEMON, generations=[1], types=["불꽃"]))
        self.assertEqual(result, [4, 5, 6])
        self.assertNotIn(155, result)

    def test_several_generations_are_or(self):
        result = ids(search_pokemon(POKEMON, generations=[1, 2], types=["불꽃"]))
        self.assertEqual(result, [4, 5, 6, 155, 250])

    def test_two_types_must_both_match(self):
        result = ids(search_pokemon(POKEMON, types=["물", "비행"]))
        self.assertEqual(result, [130])
        self.assertNotIn(7, result)

    def test_query_and_filters_combine(self):
        self.assertEqual(ids(search_pokemon(POKEMON, query="리자", types=["비행"])), [6])

    def test_empty_search_keeps_everything(self):
        self.assertEqual(search_pokemon(POKEMON), POKEMON)
        self.assertEqual(search_pokemon(POKEMON, query="  ", generations=[], types=[]), POKEMON)


if __name__ == "__main__":
    unittest.main()
