"""Small, testable helpers for the Pokedex page."""

import math

# Type badge colors, from the color chart in issue #9 ("보통" column).
# Keys are the Korean type names PokeAPI returns.
TYPE_COLORS = {
    "노말": "#9FA19F",
    "불꽃": "#E62829",
    "물": "#2980EF",
    "전기": "#FAC000",
    "풀": "#3FA129",
    "얼음": "#3DCEF3",
    "격투": "#FF8000",
    "독": "#9141CB",
    "땅": "#915121",
    "비행": "#81B9EF",
    "에스퍼": "#EF4179",
    "벌레": "#91A119",
    "바위": "#AFA981",
    "고스트": "#704170",
    "드래곤": "#5060E1",
    "악": "#624D4E",
    "강철": "#60A1B8",
    "페어리": "#EF70EF",
}

UNKNOWN_TYPE_COLOR = "#9A9A9A"

WHITE = "#FFFFFF"
BLACK = "#000000"


def type_color(type_name):
    """Badge background color for a type name; gray for unknown types."""
    return TYPE_COLORS.get(type_name, UNKNOWN_TYPE_COLOR)


def _relative_luminance(hex_color):
    """WCAG 2 relative luminance of a "#RRGGBB" color."""
    value = hex_color.lstrip("#")
    channels = [int(value[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    r, g, b = linear
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def badge_text_color(background):
    """White or black, whichever has the higher contrast ratio on `background`."""
    lum = _relative_luminance(background)
    contrast_with_white = 1.05 / (lum + 0.05)
    contrast_with_black = (lum + 0.05) / 0.05
    return WHITE if contrast_with_white > contrast_with_black else BLACK


# National dex number range (first, last; both inclusive) of each region,
# in the order the page loads them while scrolling down.
REGION_RANGES = {
    "관동": (1, 151),
    "성도": (152, 251),
    "호연": (252, 386),
    "신오": (387, 493),
    "하나": (494, 649),
    "칼로스": (650, 721),
    "알로라": (722, 809),
    "가라르": (810, 905),
    "팔데아": (906, 1025),
}

REGIONS = list(REGION_RANGES)


def region_range(region_name):
    """(first, last) national dex numbers of a region; ValueError if unknown."""
    try:
        return REGION_RANGES[region_name]
    except KeyError:
        raise ValueError(f"알 수 없는 지역: {region_name}") from None


def region_of(pokemon_id):
    """Name of the region whose dex range holds `pokemon_id`, or None."""
    for name, (first, last) in REGION_RANGES.items():
        if first <= pokemon_id <= last:
            return name
    return None


# ---- Detail dialog (issue #10) ----

# Radar chart axes, clockwise from the top: (PokeAPI stat name, Korean label).
STAT_AXES = [
    ("hp", "HP"),
    ("attack", "공격"),
    ("defense", "방어"),
    ("special-attack", "특수공격"),
    ("special-defense", "특수방어"),
    ("speed", "스피드"),
]

MAX_BASE_STAT = 255


def stats_to_radar(stats, max_value=MAX_BASE_STAT):
    """Base stats -> six radar points in STAT_AXES order.

    `stats` is a list of {"stat": <PokeAPI name>, "value": <base stat>}.
    Each point is {"stat", "label", "value", "ratio"}; ratio is value / max_value,
    capped at 1. Missing stats count as 0.
    """
    values = {s["stat"]: s["value"] for s in stats}
    data = []
    for stat, label in STAT_AXES:
        value = values.get(stat, 0)
        data.append(
            {
                "stat": stat,
                "label": label,
                "value": value,
                "ratio": min(value / max_value, 1.0) if max_value else 0,
            }
        )
    return data


def radar_points(ratios, radius, cx, cy):
    """Ratios -> (x, y) polygon corners, first axis straight up, then clockwise."""
    count = len(ratios)
    points = []
    for i, ratio in enumerate(ratios):
        angle = 2 * math.pi * i / count
        points.append(
            (cx + radius * ratio * math.sin(angle), cy - radius * ratio * math.cos(angle))
        )
    return points


def last_level_up_moves(moves, count=4):
    """The `count` moves learned last by leveling up, in level order.

    `moves` is a list of {"name", "type", "level", "order", "version_group"},
    where "version_group" is a number that grows with release order.
    Learnsets differ by game, so only the latest version group is used. A move
    listed more than once counts at its highest level; ties go by "order".
    """
    if not moves:
        return []
    latest = max(m["version_group"] for m in moves)
    best = {}
    for m in moves:
        if m["version_group"] != latest:
            continue
        current = best.get(m["name"])
        if current is None or m["level"] > current["level"]:
            best[m["name"]] = m
    ordered = sorted(best.values(), key=lambda m: (m["level"], m["order"] or 0))
    return [{"name": m["name"], "type": m["type"], "level": m["level"]} for m in ordered[-count:]]


def evolution_stages(species):
    """Species of one evolution chain -> stages, first form first.

    Each species is a dict with "id" and "evolves_from" (id or None). Species in
    the same stage (branches like Eevee's) are sorted by id.
    """
    by_id = {s["id"]: s for s in species}

    def depth(s):
        d = 0
        while s["evolves_from"] in by_id:
            s = by_id[s["evolves_from"]]
            d += 1
        return d

    stages = {}
    for s in sorted(species, key=lambda s: s["id"]):
        stages.setdefault(depth(s), []).append(s)
    return [stages[d] for d in sorted(stages)]
