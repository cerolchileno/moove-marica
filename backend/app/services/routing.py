
from functools import lru_cache
from pathlib import Path

import osmnx as ox

from app.algorithms.astar import calcular_astar


BASE_DIR = Path(__file__).resolve().parents[2]
GRAPH_PATH = BASE_DIR / "data" / "marica_walk.graphml"


@lru_cache(maxsize=1)
def carregar_grafo():
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(
            "Mapa não encontrado. Execute "
            "scripts/download_map.py primeiro."
        )

    return ox.load_graphml(GRAPH_PATH)


def calcular_rota(origem_lat, origem_lng, destino_lat, destino_lng):
    grafo = carregar_grafo()

    no_origem = ox.distance.nearest_nodes(
        grafo,
        X=origem_lng,
        Y=origem_lat,
    )

    no_destino = ox.distance.nearest_nodes(
        grafo,
        X=destino_lng,
        Y=destino_lat,
    )

    caminho, distancia_m = calcular_astar(
        grafo,
        no_origem,
        no_destino,
    )

    coordenadas = []

    for no in caminho:
        dados = grafo.nodes[no]
        coordenadas.append([
            float(dados["y"]),
            float(dados["x"]),
        ])

    velocidade_kmh = 5.0
    tempo_min = (distancia_m / 1000) / velocidade_kmh * 60

    return {
        "algoritmo": "A*",
        "modalidade": "caminhada",
        "distancia_m": round(distancia_m, 2),
        "tempo_min": round(tempo_min, 1),
        "coordenadas": coordenadas,
    }
