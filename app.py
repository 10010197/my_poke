import base64
import html
from pathlib import Path

import requests
import streamlit as st

from pokedex import (
    REGIONS,
    badge_text_color,
    evolution_stages,
    last_level_up_moves,
    radar_points,
    region_of,
    region_range,
    stats_to_radar,
    type_color,
)

GRAPHQL_URL = "https://graphql.pokeapi.co/v1beta2"
LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"
TITLE_TEXT = "포켓몬 도감"

# Card image hover effect. Switch between the two options from issue #15:
#   "grayscale": image is gray, turns to color on hover
#   "opacity":   image is at 0.3 opacity, turns to 1.0 on hover
HOVER_STYLE = "opacity"
HOVER_EFFECTS = {
    "grayscale": ("filter: grayscale(1);", "filter: grayscale(0);"),
    "opacity": ("opacity: 0.3;", "opacity: 1;"),
}

QUERY = """
query RegionPokedex($first: Int!, $last: Int!) {
  pokemonspecies(where: {id: {_gte: $first, _lte: $last}}, order_by: {id: asc}) {
    id
    name
    pokemonspeciesnames(where: {language: {name: {_eq: "ko"}}}) { name }
    pokemons(where: {is_default: {_eq: true}}) {
      pokemontypes(order_by: {slot: asc}) {
        type {
          name
          typenames(where: {language: {name: {_eq: "ko"}}}) { name }
        }
      }
      pokemonsprites { sprites }
    }
  }
}
"""


@st.cache_data(ttl=60 * 60 * 24)
def fetch_pokemon(first, last):
    """Species with national dex numbers first..last (inclusive), cached per range."""
    res = requests.post(
        GRAPHQL_URL,
        json={"query": QUERY, "variables": {"first": first, "last": last}},
        timeout=30,
    )
    res.raise_for_status()
    body = res.json()
    if "errors" in body:
        raise RuntimeError(body["errors"])

    result = []
    for species in body["data"]["pokemonspecies"]:
        names = species["pokemonspeciesnames"]
        pokemon = species["pokemons"][0]

        types = []
        for t in pokemon["pokemontypes"]:
            type_names = t["type"]["typenames"]
            types.append(type_names[0]["name"] if type_names else t["type"]["name"])

        sprites = pokemon["pokemonsprites"][0]["sprites"] if pokemon["pokemonsprites"] else {}
        image = (
            sprites.get("other", {}).get("official-artwork", {}).get("front_default")
            or sprites.get("front_default")
        )

        result.append(
            {
                "id": species["id"],
                "name": names[0]["name"] if names else species["name"],
                "types": types,
                "image": image,
            }
        )
    return result


# Detail dialog data (issue #10): loaded only for the Pokemon that was clicked.
DETAIL_QUERY = """
query PokemonDetail($id: Int!) {
  pokemon(where: {id: {_eq: $id}}) {
    pokemonstats { base_stat stat { name } }
    pokemonmoves(where: {movelearnmethod: {name: {_eq: "level-up"}}}) {
      level
      order
      versiongroup { order }
      move {
        name
        movenames(where: {language: {name: {_eq: "ko"}}}) { name }
        type {
          name
          typenames(where: {language: {name: {_eq: "ko"}}}) { name }
        }
      }
    }
    pokemonspecy {
      evolutionchain {
        pokemonspecies(order_by: {id: asc}) {
          id
          name
          evolves_from_species_id
          pokemonspeciesnames(where: {language: {name: {_eq: "ko"}}}) { name }
          pokemons(where: {is_default: {_eq: true}}) { pokemonsprites { sprites } }
        }
      }
    }
  }
}
"""


def _ko_name(names, fallback):
    return names[0]["name"] if names else fallback


def _artwork(sprites):
    return (
        sprites.get("other", {}).get("official-artwork", {}).get("front_default")
        or sprites.get("front_default")
    )


@st.cache_data(ttl=60 * 60 * 24)
def fetch_detail(pokemon_id):
    res = requests.post(
        GRAPHQL_URL,
        json={"query": DETAIL_QUERY, "variables": {"id": pokemon_id}},
        timeout=30,
    )
    res.raise_for_status()
    body = res.json()
    if "errors" in body:
        raise RuntimeError(body["errors"])
    pokemon = body["data"]["pokemon"][0]

    stats = [{"stat": s["stat"]["name"], "value": s["base_stat"]} for s in pokemon["pokemonstats"]]

    moves = [
        {
            "name": _ko_name(m["move"]["movenames"], m["move"]["name"]),
            "type": _ko_name(m["move"]["type"]["typenames"], m["move"]["type"]["name"]),
            "level": m["level"],
            "order": m["order"],
            # Version group ids are not in release order (blue-japan is 29),
            # so use the version group's "order" field to find the newest game.
            "version_group": m["versiongroup"]["order"],
        }
        for m in pokemon["pokemonmoves"]
    ]

    chain = []
    for s in pokemon["pokemonspecy"]["evolutionchain"]["pokemonspecies"]:
        forms = s["pokemons"]
        sprites_rows = forms[0]["pokemonsprites"] if forms else []
        chain.append(
            {
                "id": s["id"],
                "name": _ko_name(s["pokemonspeciesnames"], s["name"]),
                "evolves_from": s["evolves_from_species_id"],
                "image": _artwork(sprites_rows[0]["sprites"]) if sprites_rows else None,
            }
        )

    return {
        "stats": stats,
        "moves": last_level_up_moves(moves),
        "evolution": evolution_stages(chain),
    }


CREAM = "#f5f0e0"  # surface-card; also the badge background

# Clay feature-card palette, cycled card by card: (background, text, muted text)
CARD_COLORS = [
    ("#ff4d8b", "#ffffff", "rgba(255,255,255,0.8)"),  # brand-pink
    ("#1a3a3a", "#ffffff", "rgba(255,255,255,0.7)"),  # brand-teal
    ("#b8a4ed", "#0a0a0a", "#3a3a3a"),  # brand-lavender
    ("#ffb084", "#0a0a0a", "#3a3a3a"),  # brand-peach
    ("#e8b94a", "#0a0a0a", "#3a3a3a"),  # brand-ochre
    (CREAM, "#0a0a0a", "#6a6a6a"),  # surface-card (cream)
]

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

.stApp {
  background: #fffaf0;
  color: #3a3a3a;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.block-container {
  max-width: 1280px;
  padding-top: 96px;
  padding-left: 24px;
  padding-right: 24px;
}

.dex-title {
  font-family: inherit;
  font-size: 40px;
  font-weight: 500;
  line-height: 1.1;
  letter-spacing: -1px;
  color: #0a0a0a;
  margin: 0 0 32px;
}

.dex-logo {
  text-align: center;
  margin: 0 0 32px;
}

/* Scale down on narrow screens instead of cropping. The font styles apply to
   the alt text, so a broken image still reads as the title. */
.dex-logo img {
  display: inline-block;
  width: 360px;
  max-width: 100%;
  height: auto;
  font-size: 40px;
  font-weight: 500;
  letter-spacing: -1px;
  color: #0a0a0a;
}

.dex-grid {
  display: grid;
  grid-template-columns: repeat(8, minmax(0, 1fr));
  gap: 16px;
}

.clay-card {
  border-radius: 24px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.clay-card img {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: contain;
  display: block;
}

.clay-no {
  font-size: 12px;
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: 1.5px;
}

.clay-name {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  word-break: keep-all;
}

.clay-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.clay-badge {
  background: #f5f0e0;
  color: #0a0a0a;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.4;
  padding: 4px 12px;
  border-radius: 9999px;
}

/* Region divider between two regions' grids: hairline, name, hairline. */
.dex-region {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 48px 0 24px;
  font-size: 20px;
  font-weight: 600;
  line-height: 1.3;
  letter-spacing: -0.2px;
  color: #0a0a0a;
}

.dex-region::before,
.dex-region::after {
  content: "";
  flex: 1;
  height: 1px;
  background: #e5e5e5;
}

/* "다음 지역 불러오기" button: primary CTA from DESIGN.md. */
.st-key-load_next_region {
  align-self: center;
  margin-top: 32px;
}

.stButton button {
  background: #0a0a0a;
  color: #ffffff;
  border: none;
  border-radius: 12px;
  height: 44px;
  padding: 12px 20px;
  font-family: inherit;
  font-size: 14px;
  font-weight: 600;
}

.stButton button:hover,
.stButton button:focus,
.stButton button:active {
  background: #1f1f1f;
  color: #ffffff;
}

.dex-credit {
  margin: 32px 0 0;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.4;
  color: #6a6a6a;
  text-align: center;
}
</style>
"""


def render_card(index, p):
    bg, fg, muted = CARD_COLORS[index % len(CARD_COLORS)]
    image = (
        f'<img src="{html.escape(p["image"])}" alt="{html.escape(p["name"])}" loading="lazy">'
        if p["image"]
        else ""
    )
    badges = "".join(
        '<span class="clay-badge" '
        f'style="background:{type_color(t)}; color:{badge_text_color(type_color(t))};">'
        f"{html.escape(t)}</span>"
        for t in p["types"]
    )
    # A plain link: st.html strips JavaScript, so the click is passed to Python
    # through the ?pokemon=<id> query parameter, which opens the detail dialog.
    return (
        f'<a class="clay-link" href="?pokemon={p["id"]}" target="_self">'
        f'<div class="clay-card" style="background:{bg}; color:{fg};">'
        f"{image}"
        f'<div class="clay-no" style="color:{muted};">NO.{p["id"]:03d}</div>'
        f'<div class="clay-name">{html.escape(p["name"])}</div>'
        f'<div class="clay-badges">{badges}</div>'
        "</div>"
        "</a>"
    )


DETAIL_STYLE = """
<style>
.clay-link, .clay-link:hover, .clay-link:visited {
  display: block;
  color: inherit;
  text-decoration: none;
}
.clay-link .clay-card { height: 100%; box-sizing: border-box; }
.dex-grid > .clay-link { min-width: 0; }

.detail { font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #3a3a3a; }
.detail-head { display: flex; gap: 24px; align-items: center; flex-wrap: wrap; }
.detail-hero { background: #f5f0e0; border-radius: 24px; padding: 16px; width: 240px; max-width: 100%; box-sizing: border-box; }
.detail-hero img { width: 100%; aspect-ratio: 1 / 1; object-fit: contain; display: block; }
.detail-no { font-size: 12px; font-weight: 600; letter-spacing: 1.5px; color: #6a6a6a; }
.detail-name { font-size: 32px; font-weight: 500; letter-spacing: -0.5px; line-height: 1.15; color: #0a0a0a; margin: 4px 0 12px; }
.detail-section { margin-top: 32px; }
.detail-label { font-size: 18px; font-weight: 600; line-height: 1.4; color: #0a0a0a; margin: 0 0 12px; }
.detail-radar { display: block; width: 100%; max-width: 360px; height: auto; margin: 0 auto; }
.evo-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.evo-stage { display: flex; flex-wrap: wrap; gap: 8px; max-width: 432px; }
.evo-item { display: flex; flex-direction: column; align-items: center; width: 96px; text-align: center; }
.evo-item img { width: 96px; height: 96px; object-fit: contain; background: #f5f0e0; border-radius: 16px; }
.evo-item span { font-size: 13px; font-weight: 500; margin-top: 4px; word-break: keep-all; }
.evo-item.current img { outline: 3px solid #ff4d8b; }
.evo-item.current span { color: #ff4d8b; font-weight: 600; }
.evo-arrow { font-size: 20px; color: #9a9a9a; }
.move-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.move-item { background: #f5f0e0; border-radius: 16px; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.move-name { font-size: 16px; font-weight: 600; color: #0a0a0a; }
.move-level { font-size: 12px; color: #6a6a6a; }
</style>
"""

RADAR_SIZE = 360
RADAR_RADIUS = 110


def _points_attr(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def render_radar(stats):
    """Six-axis stat chart, drawn as SVG (no chart package needed).

    st.html removes inline <svg> elements, so the SVG is embedded as a
    data-URI <img>, the same way the logo is.
    """
    data = stats_to_radar(stats)
    c = RADAR_SIZE / 2
    count = len(data)
    parts = [
        f'<svg viewBox="0 0 {RADAR_SIZE} {RADAR_SIZE}" width="{RADAR_SIZE}" height="{RADAR_SIZE}" '
        'xmlns="http://www.w3.org/2000/svg" '
        'font-family="Inter, -apple-system, &quot;Segoe UI&quot;, &quot;Malgun Gothic&quot;, sans-serif">'
    ]
    # Background grid: hexagons at 25/50/75/100% and the six spokes.
    for level in (0.25, 0.5, 0.75, 1):
        ring = radar_points([level] * count, RADAR_RADIUS, c, c)
        parts.append(
            f'<polygon points="{_points_attr(ring)}" fill="none" stroke="#e5e5e5" stroke-width="1"/>'
        )
    for x, y in radar_points([1] * count, RADAR_RADIUS, c, c):
        parts.append(
            f'<line x1="{c}" y1="{c}" x2="{x:.1f}" y2="{y:.1f}" stroke="#e5e5e5" stroke-width="1"/>'
        )
    shape = radar_points([d["ratio"] for d in data], RADAR_RADIUS, c, c)
    parts.append(
        f'<polygon points="{_points_attr(shape)}" fill="rgba(255,77,139,0.35)" '
        'stroke="#ff4d8b" stroke-width="2"/>'
    )
    # Axis labels with the value, just outside the outer ring.
    for d, (x, y) in zip(data, radar_points([1.28] * count, RADAR_RADIUS, c, c)):
        parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="middle" '
            'font-size="13" fill="#3a3a3a">'
            f'<tspan font-weight="600">{html.escape(d["label"])}</tspan>'
            f'<tspan x="{x:.1f}" dy="16" fill="#6a6a6a">{d["value"]}</tspan>'
            "</text>"
        )
    parts.append("</svg>")
    svg = base64.b64encode("".join(parts).encode("utf-8")).decode("ascii")
    summary = ", ".join(f'{d["label"]} {d["value"]}' for d in data)
    return (
        f'<img class="detail-radar" src="data:image/svg+xml;base64,{svg}" '
        f'alt="스탯 그래프: {html.escape(summary)}">'
    )


def _badge(type_name):
    bg = type_color(type_name)
    return (
        f'<span class="clay-badge" style="background:{bg}; color:{badge_text_color(bg)};">'
        f"{html.escape(type_name)}</span>"
    )


def render_evolution(stages, current_id):
    columns = []
    for stage in stages:
        items = []
        for s in stage:
            cls = "evo-item current" if s["id"] == current_id else "evo-item"
            img = (
                f'<img src="{html.escape(s["image"])}" alt="{html.escape(s["name"])}" loading="lazy">'
                if s["image"]
                else ""
            )
            items.append(f'<div class="{cls}">{img}<span>{html.escape(s["name"])}</span></div>')
        columns.append(f'<div class="evo-stage">{"".join(items)}</div>')
    return '<div class="evo-row">' + '<span class="evo-arrow">→</span>'.join(columns) + "</div>"


def render_moves(moves):
    if not moves:
        return "<p>레벨업으로 배우는 기술이 없습니다.</p>"
    items = "".join(
        '<div class="move-item">'
        f'<div><div class="move-name">{html.escape(m["name"])}</div>'
        f'<div class="move-level">Lv.{m["level"]}</div></div>'
        f"{_badge(m['type'])}"
        "</div>"
        for m in moves
    )
    return f'<div class="move-list">{items}</div>'


def render_detail(p, detail):
    image = (
        f'<img src="{html.escape(p["image"])}" alt="{html.escape(p["name"])}">' if p["image"] else ""
    )
    badges = "".join(_badge(t) for t in p["types"])
    return (
        DETAIL_STYLE
        + '<div class="detail">'
        + '<div class="detail-head">'
        + f'<div class="detail-hero">{image}</div>'
        + "<div>"
        + f'<div class="detail-no">NO.{p["id"]:03d}</div>'
        + f'<div class="detail-name">{html.escape(p["name"])}</div>'
        + f'<div class="clay-badges">{badges}</div>'
        + "</div></div>"
        + '<div class="detail-section"><p class="detail-label">스탯</p>'
        + render_radar(detail["stats"])
        + "</div>"
        + '<div class="detail-section"><p class="detail-label">진화</p>'
        + render_evolution(detail["evolution"], p["id"])
        + "</div>"
        + '<div class="detail-section"><p class="detail-label">기술</p>'
        + render_moves(detail["moves"])
        + "</div>"
        + "</div>"
    )


def close_detail():
    """Back to the grid: drop the ?pokemon= query parameter."""
    st.query_params.pop("pokemon", None)


@st.dialog("포켓몬 상세", width="large", on_dismiss=close_detail)
def show_detail(p):
    try:
        detail = fetch_detail(p["id"])
    except (requests.RequestException, RuntimeError, KeyError, IndexError):
        st.error("상세 정보를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")
    else:
        st.html(render_detail(p, detail))
    if st.button("닫기", width="stretch"):
        close_detail()
        st.rerun()


def selected_pokemon(pokemon_list):
    """The Pokemon named by ?pokemon=<id>, or None."""
    raw = st.query_params.get("pokemon")
    try:
        wanted = int(raw)
    except (TypeError, ValueError):
        return None
    return next((p for p in pokemon_list if p["id"] == wanted), None)


def hover_style():
    """CSS for the card image hover effect selected by HOVER_STYLE.

    Only applies on devices with a real hover pointer (mouse), so phones and
    tablets always see the full-color, fully opaque image.
    """
    rest, hover = HOVER_EFFECTS[HOVER_STYLE]
    return (
        "<style>"
        "@media (hover: hover) and (pointer: fine) {"
        f".clay-card img {{ {rest} transition: filter 0.25s ease, opacity 0.25s ease; }}"
        f".clay-card:hover img {{ {hover} }}"
        "}"
        "</style>"
    )


def render_title():
    """Logo image from assets/.

    If the file can't be read, the text title is shown instead. If the browser
    can't draw the image, its alt text (styled like the title) shows instead.
    st.html strips onerror handlers, so there is no client-side swap.
    """
    try:
        data = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    except OSError:
        return f'<h1 class="dex-title">{TITLE_TEXT}</h1>'
    return (
        '<div class="dex-logo">'
        f'<img src="data:image/png;base64,{data}" alt="{TITLE_TEXT}">'
        "</div>"
    )


def render_regions(region_names):
    """One card grid per region, with a region-name divider wherever the region changes.

    Card colors keep cycling across regions, so the palette doesn't restart.
    """
    parts = []
    index = 0
    for n, region in enumerate(region_names):
        if n > 0:
            parts.append(f'<div class="dex-region">{html.escape(region)}</div>')
        cards = []
        for p in fetch_pokemon(*region_range(region)):
            cards.append(render_card(index, p))
            index += 1
        parts.append(f'<div class="dex-grid">{"".join(cards)}</div>')
    return "".join(parts)


def load_next_region():
    st.session_state.loaded_regions += 1


def regions_needed_for_selection():
    """How many regions must be loaded to show the Pokemon in ?pokemon=<id> (0 if none).

    Clicking a card is a link that reloads the page, which resets session_state
    to 관동 only; this brings back every region up to the clicked Pokemon.
    """
    try:
        region = region_of(int(st.query_params.get("pokemon")))
    except (TypeError, ValueError):
        return 0
    return REGIONS.index(region) + 1 if region else 0


st.set_page_config(page_title="포켓몬 도감", layout="wide")

# How many regions (from the start of REGIONS) are shown. Starts with 관동 only.
# st.html strips JavaScript, so the page can't detect reaching the bottom by
# itself; a button at the end of the list loads the next region instead.
if "loaded_regions" not in st.session_state:
    st.session_state.loaded_regions = 1
st.session_state.loaded_regions = max(
    st.session_state.loaded_regions, regions_needed_for_selection()
)

loaded = REGIONS[: st.session_state.loaded_regions]

st.html(STYLE + DETAIL_STYLE + hover_style() + render_title() + render_regions(loaded))

if len(loaded) < len(REGIONS):
    next_region = REGIONS[len(loaded)]
    st.button(
        f"다음 지역 불러오기 ({next_region})",
        key="load_next_region",
        on_click=load_next_region,
    )

st.html('<p class="dex-credit">데이터: PokeAPI</p>')

# Every Pokemon currently on the page (all loaded regions; fetch_pokemon is cached).
pokemon_list = [p for region in loaded for p in fetch_pokemon(*region_range(region))]
selected = selected_pokemon(pokemon_list)
if selected is not None:
    show_detail(selected)
