
from pathlib import Path

import networkx as nx
import osmnx as ox


BASE_DIR = Path(__file__).resolve().parents[1]
GRAPH_PATH = BASE_DIR / "data" / "marica_walk_integrado.graphml"

ORIGEM = (-22.93657, -42.74935)
DESTINO = (-22.95589, -42.75467)


def main():
    print("Moove Marica - Verificação de componentes")
    print("----------------------------------------")

    grafo = ox.load_graphml(GRAPH_PATH)

    componentes = sorted(
        nx.weakly_connected_components(grafo),
        key=len,
        reverse=True,
    )

    total_nos = grafo.number_of_nodes()

    print(f"Total de componentes: {len(componentes)}")

    for indice, componente in enumerate(componentes, start=1):
        percentual = len(componente) / total_nos * 100

        print(
            f"Componente {indice}: "
            f"{len(componente)} nós "
            f"({percentual:.2f}%)"
        )

    no_origem = ox.distance.nearest_nodes(
        grafo,
        X=ORIGEM[1],
        Y=ORIGEM[0],
    )

    no_destino = ox.distance.nearest_nodes(
        grafo,
        X=DESTINO[1],
        Y=DESTINO[0],
    )

    for indice, componente in enumerate(componentes, start=1):
        if no_origem in componente:
            print(f"\nOrigem no componente: {indice}")

        if no_destino in componente:
            print(f"Destino no componente: {indice}")

    print(
        "\nExiste caminho dirigido da origem ao destino:",
        nx.has_path(grafo, no_origem, no_destino),
    )

    print("\nVerificação concluída!")


if __name__ == "__main__":
    main()
