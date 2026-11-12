import requests
import streamlit as st

GRAPHQL_URL = "https://graphql.pokeapi.co/v1beta2"
COLUMNS = 8

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


st.set_page_config(page_title="포켓몬 도감", layout="wide")
st.title("포켓몬 도감")

pokemon_list = fetch_pokemon()

for start in range(0, len(pokemon_list), COLUMNS):
    cols = st.columns(COLUMNS)
    for col, p in zip(cols, pokemon_list[start : start + COLUMNS]):
        with col:
            with st.container(border=True):
                if p["image"]:
                    st.image(p["image"], width="stretch")
                st.caption(f"No.{p['id']:03d}")
                st.markdown(f"**{p['name']}**")
                st.write(" / ".join(p["types"]))
