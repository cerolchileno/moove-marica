
import heapq
import math
from itertools import count


def distancia_geografica(lat1, lon1, lat2, lon2):
    """
    Calcula a distância entre coordenadas geográficas
    usando a fórmula de Haversine.

    Retorna o resultado em metros.
    """
    raio_terra = 6_371_000

    latitude1 = math.radians(lat1)
    latitude2 = math.radians(lat2)

    delta_latitude = math.radians(lat2 - lat1)
    delta_longitude = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_latitude / 2) ** 2
        + math.cos(latitude1)
        * math.cos(latitude2)
        * math.sin(delta_longitude / 2) ** 2
    )

    return (
        2 * raio_terra
        * math.asin(min(1.0, math.sqrt(a)))
    )


def calcular_astar(grafo, origem, destino):
    """
    Encontra o caminho de menor distância no grafo
    usando o algoritmo A*.

    Parâmetros:
        grafo: NetworkX MultiDiGraph
        origem: identificador do nó inicial
        destino: identificador do nó final

    Retorna:
        (caminho, distancia_total)
    """

    def heuristica(no):
        atual = grafo.nodes[no]
        final = grafo.nodes[destino]

        return distancia_geografica(
            atual["y"],
            atual["x"],
            final["y"],
            final["x"],
        )

    contador = count()

    fila = [
        (heuristica(origem), next(contador), origem)
    ]

    custos = {origem: 0.0}
    anteriores = {}

    while fila:
        prioridade, _, atual = heapq.heappop(fila)

        # Descarta entradas antigas da fila.
        if prioridade > custos.get(atual, float("inf")) + heuristica(atual) + 1e-9:
            continue

        if atual == destino:
            caminho = [atual]

            while atual in anteriores:
                atual = anteriores[atual]
                caminho.append(atual)

            caminho.reverse()

            return caminho, custos[destino]

        for vizinho, arestas in grafo[atual].items():
            menor_distancia = min(
                float(dados["length"])
                for dados in arestas.values()
            )

            novo_custo = (
                custos[atual] + menor_distancia
            )

            if novo_custo < custos.get(
                vizinho, float("inf")
            ):
                custos[vizinho] = novo_custo
                anteriores[vizinho] = atual

                prioridade = (
                    novo_custo + heuristica(vizinho)
                )

                heapq.heappush(
                    fila,
                    (
                        prioridade,
                        next(contador),
                        vizinho,
                    ),
                )

    raise ValueError(
        "Não foi possível encontrar um caminho entre os pontos."
    )
