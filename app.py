import base64
import html
from pathlib import Path

import requests
import streamlit as st

from pokedex import badge_text_color, type_color

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
query Gen1Pokedex {
  pokemonspecies(where: {id: {_gte: 1, _lte: 151}}, order_by: {id: asc}) {
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
def fetch_pokemon():
    res = requests.post(GRAPHQL_URL, json={"query": QUERY}, timeout=30)
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

/* Cream badges on a cream card: add a gray outline so they stay visible */
.clay-badge--outlined {
  border: 1px solid #9a9a9a;
  padding: 3px 11px;
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
    badge_class = "clay-badge clay-badge--outlined" if bg == CREAM else "clay-badge"
    badges = "".join(
        f'<span class="{badge_class}" '
        f'style="background:{type_color(t)}; color:{badge_text_color(type_color(t))};">'
        f"{html.escape(t)}</span>"
        for t in p["types"]
    )
    return (
        f'<div class="clay-card" style="background:{bg}; color:{fg};">'
        f"{image}"
        f'<div class="clay-no" style="color:{muted};">NO.{p["id"]:03d}</div>'
        f'<div class="clay-name">{html.escape(p["name"])}</div>'
        f'<div class="clay-badges">{badges}</div>'
        "</div>"
    )


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


st.set_page_config(page_title="포켓몬 도감", layout="wide")

pokemon_list = fetch_pokemon()

cards = "".join(render_card(i, p) for i, p in enumerate(pokemon_list))
st.html(
    STYLE
    + hover_style()
    + render_title()
    + f'<div class="dex-grid">{cards}</div>'
    + '<p class="dex-credit">데이터: PokeAPI</p>'
)
