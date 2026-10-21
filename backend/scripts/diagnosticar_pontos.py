
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2

import osmnx as ox

BASE_DIR = Path(__file__).resolve().parents[1]
GRAPH_PATH = BASE_DIR / "data" / "marica_walk_cordeirinho.graphml"

def distancia_metros(lat1, lon1, lat2, lon2):
    raio_terra = 6371000

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    return 2 * raio_terra * atan2(
        sqrt(a),
        sqrt(1 - a),
    )


def verificar_ponto(graph, nome, latitude, longitude):
    no = ox.distance.nearest_nodes(
        graph,
        X=longitude,
        Y=latitude,
    )

    dados = graph.nodes[no]

    distancia = distancia_metros(
        latitude,
        longitude,
        dados["y"],
        dados["x"],
    )

    print(f"\n{nome}")
    print(f"Coordenadas: {latitude}, {longitude}")
    print(f"Nó mais próximo: {no}")
    print(f"Distância até o nó: {distancia:.1f} metros")

    if distancia > 500:
        print("ATENÇÃO: Ponto distante da rede de ruas.")
    else:
        print("Ponto próximo da rede de ruas.")


def main():
    graph = ox.load_graphml(GRAPH_PATH)

    print("Moove Marica - Diagnóstico de pontos")

    print("\nDigite as coordenadas da ORIGEM:")
    lat_origem = float(input("Latitude: ").replace(",", "."))
    lon_origem = float(input("Longitude: ").replace(",", "."))

    print("\nDigite as coordenadas do DESTINO:")
    lat_destino = float(input("Latitude: ").replace(",", "."))
    lon_destino = float(input("Longitude: ").replace(",", "."))

    verificar_ponto(
        graph,
        "ORIGEM",
        lat_origem,
        lon_origem,
    )

    verificar_ponto(
        graph,
        "DESTINO",
        lat_destino,
        lon_destino,
    )


if __name__ == "__main__":
    main()
