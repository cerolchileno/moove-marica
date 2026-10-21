
from pathlib import Path

import osmnx as ox
import networkx as nx

BASE_DIR = Path(__file__).resolve().parents[1]

GRAPH_PATH = BASE_DIR / "data" / "marica_walk.graphml"


def main():
    if not GRAPH_PATH.exists():
        print("ERRO: Arquivo do mapa não encontrado.")
        return

    print("Moove Marica - Diagnóstico da rede de ruas")
    print("-----------------------------------------")

    graph = ox.load_graphml(GRAPH_PATH)

    print(f"Nós: {graph.number_of_nodes()}")
    print(f"Arestas: {graph.number_of_edges()}")

    latitudes = [
        dados["y"]
        for _, dados in graph.nodes(data=True)
    ]

    longitudes = [
        dados["x"]
        for _, dados in graph.nodes(data=True)
    ]

    print("\nLimites aproximados da rede:")
    print(f"Latitude mínima: {min(latitudes):.6f}")
    print(f"Latitude máxima: {max(latitudes):.6f}")
    print(f"Longitude mínima: {min(longitudes):.6f}")
    print(f"Longitude máxima: {max(longitudes):.6f}")

    componentes = list(
        nx.weakly_connected_components(graph)
    )

    print(f"\nComponentes conectados: {len(componentes)}")

    maior_componente = max(
        componentes,
        key=len,
    )

    percentual = (
        len(maior_componente)
        / graph.number_of_nodes()
        * 100
    )

    print(
        f"Nós no maior componente: "
        f"{len(maior_componente)} ({percentual:.1f}%)"
    )

    print("\nDiagnóstico concluído!")


if __name__ == "__main__":
    main()
