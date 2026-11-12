"""Small, testable helpers for the Pokedex page."""

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
