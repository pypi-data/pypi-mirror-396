import os, asyncio, aiohttp
import pandas as pd

from functools  import lru_cache
from typing     import List, Dict, Any

BASE_URL = "https://pokeapi.co/api/v2/pokemon"

# =========================
#   Carga y consultas CSV
# =========================

@lru_cache(maxsize=4)
def _load_df(csv_path: str = "pokemon_stats.csv") -> pd.DataFrame:
    """Carga el CSV y lo cachea para evitar releerlo todo el rato."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encuentra el fichero: {csv_path}")

    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    return df

def get_grupos_pokemon(csv_path: str = "pokemon_stats.csv") -> List[str]:
    """Devuelve una lista con los nombres de todos los grupos disponibles en el CSV."""
    df = _load_df(csv_path)
    return df["Nombre Grupo"].unique().tolist()

def get_altura_media_grupo(grupo: str, csv_path: str = "pokemon_stats.csv") -> float | None:
    """Devuelve la altura media de un grupo específico. Si no existe, devuelve None."""
    df = _load_df(csv_path)
    fila = df[df["Nombre Grupo"] == grupo]
    if fila.empty:
        return None
    return float(fila["Altura Media"].iloc[0])

def get_peso_medio_grupo(grupo: str, csv_path: str = "pokemon_stats.csv") -> float | None:
    """Devuelve el peso medio de un grupo específico. Si no existe, devuelve None."""
    df = _load_df(csv_path)
    fila = df[df["Nombre Grupo"] == grupo]
    if fila.empty:
        return None
    return float(fila["Peso Medio"].iloc[0])

# ===============================
#   Generación del CSV desde API
# ===============================

async def _get_full_pokemon_details(
    session: aiohttp.ClientSession,
    pokemon_url: str,
    ) -> Dict[str, Any] | None:
    """
    Recupera datos de un Pokémon y sus egg_groups desde la PokeAPI usando su URL.
    """
    try:
        async with session.get(pokemon_url) as resp:
            resp.raise_for_status()
            data = await resp.json()

        species_url = data["species"]["url"]
        async with session.get(species_url) as resp_spec:
            resp_spec.raise_for_status()
            spec_data = await resp_spec.json()

        egg_groups = [g["name"] for g in spec_data.get("egg_groups", [])]

        base_experience = data.get("base_experience")
        if base_experience is None:
            base_experience = 0

        height = data.get("height") or 0
        weight = data.get("weight") or 0

        return {
            "id": data["id"],
            "name": data["name"],
            "base_experience": base_experience,
            "height": height,
            "weight": weight,
            "egg_groups": egg_groups,
        }
    except Exception as e:
        print(f"Error recuperando {pokemon_url}: {e}")
        return None

async def _download_pokemons(limit: int):
    """
    Descarga los datos de Pokémon, ajustando el límite al máximo disponible
    y usando las URLs devueltas por la API (evitando IDs inexistentes).
    """
    if limit <= 0:
        raise ValueError("El parámetro 'limit' debe ser mayor que 0.")

    async with aiohttp.ClientSession() as session:
        # Primero obtenemos el total real de pokémon
        async with session.get(BASE_URL, params={"limit": 1}) as resp:
            resp.raise_for_status()
            data = await resp.json()
            max_count = data.get("count", limit)

        if limit > max_count:
            print(
                f"Límite solicitado ({limit}) mayor que el máximo disponible ({max_count}). "
                f"Se usará {max_count}."
            )
            limit = max_count

        # Ahora pedimos la lista de 'limit' pokémon y usamos sus URLs
        async with session.get(BASE_URL, params={"limit": limit, "offset": 0}) as resp_list:
            resp_list.raise_for_status()
            list_data = await resp_list.json()
            results = list_data.get("results", [])

        tasks = [
            _get_full_pokemon_details(session, p["url"])
            for p in results
        ]
        return await asyncio.gather(*tasks)

def generar_csv_pokemon_stats(
    csv_path: str = "pokemon_stats.csv",
    limit: int = 100,
    ) -> str:
    """
    Genera un CSV con las estadísticas de altura y peso medios por grupo de Pokémon.

    - Descarga los `limit` primeros Pokémon desde PokeAPI (ajustado al máximo real).
    - Calcula la media de altura y peso por grupo.
    - Guarda el resultado en `csv_path`.
    - Devuelve la ruta del CSV generado.
    """
    raw_data = asyncio.run(_download_pokemons(limit))

    filas: list[dict[str, float | str]] = []
    for p in raw_data:
        if not p:
            continue
        for grupo in p["egg_groups"]:
            filas.append(
                {
                    "Nombre Grupo": grupo,
                    "Altura Media": p["height"],
                    "Peso Medio": p["weight"],
                }
            )

    if not filas:
        raise RuntimeError("No se han podido obtener datos de PokeAPI.")

    df = pd.DataFrame(filas)
    stats_df = (
        df.groupby("Nombre Grupo")[["Altura Media", "Peso Medio"]]
        .mean()
        .reset_index()
    )

    stats_df.to_csv(csv_path, index=False)
    print(f"CSV generado en: {csv_path}")
    # Limpiamos cache por si volvemos a cargar otro CSV distinto
    _load_df.cache_clear()
    return csv_path
