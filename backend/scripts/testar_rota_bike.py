
import networkx as nx
import osmnx as ox

from app.algorithms.astar import calcular_astar


CAMINHO_MAPA = "data/marica_bike_experimental.graphml"


def main():
    print("Moove Marica - Teste experimental de bicicleta")

    grafo = ox.load_graphml(CAMINHO_MAPA)

    componentes = sorted(
        nx.strongly_connected_components(grafo),
        key=len,
        reverse=True,
    )

    maior_componente = componentes[0]

    subgrafo = grafo.subgraph(maior_componente).copy()

    nos = list(subgrafo.nodes)

    origem = nos[0]

    # Escolhe um destino distante da origem em linha reta.
    dados_origem = subgrafo.nodes[origem]

    destino = max(
        nos,
        key=lambda no: ox.distance.great_circle(
            dados_origem["y"],
            dados_origem["x"],
            subgrafo.nodes[no]["y"],
            subgrafo.nodes[no]["x"],
        ),
    )

    print("Origem:", origem)
    print("Destino:", destino)

    caminho, distancia_m = calcular_astar(
        subgrafo,
        origem,
        destino,
    )

    print("\nROTA ENCONTRADA!")
    print("Nos no caminho:", len(caminho))
    print("Distancia:", round(distancia_m / 1000, 2), "km")

    velocidade_kmh = 15
    tempo_min = (distancia_m / 1000) / velocidade_kmh * 60

    print("Tempo estimado:", round(tempo_min, 1), "min")
    print("\nATENCAO: rota experimental, nao validada para uso real.")


if __name__ == "__main__":
    main()
