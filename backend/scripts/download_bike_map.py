
from pathlib import Path

import osmnx as ox


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

GRAPH_PATH = DATA_DIR / "marica_bike.graphml"

CENTRO_MARICA = (-22.9194, -42.8186)
RAIO_METROS = 500


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if GRAPH_PATH.exists():
        print("O mapa de bicicletas já existe.")
        print(f"Arquivo: {GRAPH_PATH}")
        return

    print("Moove Marica - Rede para bicicletas")
    print(f"Raio solicitado: {RAIO_METROS} metros")
    print("Consultando o OpenStreetMap...")

    ox.settings.timeout = 60
    ox.settings.overpass_url = "https://overpass.kumi.systems/api"
    ox.settings.overpass_rate_limit = False

    grafo = ox.graph_from_point(
        center_point=CENTRO_MARICA,
        dist=RAIO_METROS,
        network_type="bike",
        simplify=True,
        retain_all=True,
    )

    print(f"Nós encontrados: {grafo.number_of_nodes()}")
    print(f"Arestas encontradas: {grafo.number_of_edges()}")

    ox.save_graphml(grafo, filepath=GRAPH_PATH)

    print("Mapa de bicicletas salvo com sucesso!")
    print(f"Arquivo: {GRAPH_PATH}")


if __name__ == "__main__":
    main()
