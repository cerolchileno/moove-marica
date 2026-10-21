import os
from functools import lru_cache
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2

import osmnx as ox

from app.algorithms.astar import calcular_astar


BASE_DIR = Path(__file__).resolve().parents[2]
GRAPH_PATH = BASE_DIR / "data" / os.getenv(
    "MOOVE_GRAPH_FILE",
    "marica_walk.graphml",
)
# Distância máxima entre o ponto escolhido e a rede de ruas.
# Valor provisório, ajustável após os testes.
DISTANCIA_MAXIMA_REDE_M = 200


@lru_cache(maxsize=1)
def carregar_grafo():
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(
            "Mapa não encontrado. Execute "
            "scripts/download_map.py primeiro."
        )

    return ox.load_graphml(GRAPH_PATH)


def distancia_geografica_m(lat1, lng1, lat2, lng2):
    """Calcula a distância em metros entre duas coordenadas."""
    raio_terra = 6371000

    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(delta_lng / 2) ** 2
    )

    return 2 * raio_terra * atan2(
        sqrt(a),
        sqrt(1 - a),
    )


def validar_distancia_rede(grafo, no, lat, lng, nome):
    dados = grafo.nodes[no]

    distancia = distancia_geografica_m(
        lat,
        lng,
        float(dados["y"]),
        float(dados["x"]),
    )

    if distancia > DISTANCIA_MAXIMA_REDE_M:
        raise ValueError(
            f"A {nome.lower()} está fora da cobertura atual "
            f"do mapa de ruas. Distância até a rede: "
            f"{distancia:.0f} metros. "
            f"Escolha outro ponto ou aguarde a ampliação do mapa."
        )


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

    # Impede rotas calculadas a partir de nós muito distantes.
    validar_distancia_rede(
        grafo,
        no_origem,
        origem_lat,
        origem_lng,
        "Origem",
    )

    validar_distancia_rede(
        grafo,
        no_destino,
        destino_lat,
        destino_lng,
        "Destino",
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
