
from pathlib import Path

import osmnx as ox
import networkx as nx

from app.algorithms.astar import calcular_astar


BASE_DIR = Path(__file__).resolve().parents[1]
GRAPH_PATH = BASE_DIR / "data" / "marica_walk_integrado.graphml"
ORIGEM = (-22.93657, -42.74935)
DESTINO = (-22.95589, -42.75467)


def main():
    print("Moove Marica - Teste de rota regional")
    print("------------------------------------")

    grafo = ox.load_graphml(GRAPH_PATH)

    print(f"Nós: {grafo.number_of_nodes()}")
    print(f"Arestas: {grafo.number_of_edges()}")

    origem_no = ox.distance.nearest_nodes(
        grafo,
        X=ORIGEM[1],
        Y=ORIGEM[0],
    )

    destino_no = ox.distance.nearest_nodes(
        grafo,
        X=DESTINO[1],
        Y=DESTINO[0],
    )

    print(f"\nNó de origem: {origem_no}")
    print(f"Nó de destino: {destino_no}")

    if not nx.has_path(grafo, origem_no, destino_no):
        print("\nNão existe caminho dirigido entre os pontos.")
        return

    print("\nCalculando rota com nosso algoritmo A*...")

    caminho, distancia_m = calcular_astar(
        grafo,
        origem_no,
        destino_no,
    )

    tempo_min = (distancia_m / 1000) / 5 * 60

    print("\nRESULTADO:")
    print(f"Nós no caminho: {len(caminho)}")
    print(f"Distância: {distancia_m / 1000:.2f} km")
    print(f"Tempo estimado: {tempo_min:.1f} minutos")

    print("\nTeste concluído!")


if __name__ == "__main__":
    main()
