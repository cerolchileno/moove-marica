
from pathlib import Path
import osmnx as ox

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
GRAPH_PATH = DATA_DIR / "marica_walk.graphml"

# Centro aproximado de Maricá
CENTRO_MARICA = (-22.9194, -42.8186)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if GRAPH_PATH.exists():
        print("O mapa já foi baixado.")
        print(f"Arquivo: {GRAPH_PATH}")
        return

    print("Moove Marica - Baixando ruas do OpenStreetMap...")
    print("Aguarde. Isso pode levar alguns minutos.")

    graph = ox.graph_from_point(
        CENTRO_MARICA,
        dist=6000,
        network_type="walk",
        simplify=True,
        retain_all=False,
    )

    ox.save_graphml(graph, filepath=GRAPH_PATH)

    print("\nDownload concluído!")
    print(f"Nós: {graph.number_of_nodes()}")
    print(f"Arestas: {graph.number_of_edges()}")
    print(f"Mapa salvo em: {GRAPH_PATH}")


if __name__ == "__main__":
    main()
