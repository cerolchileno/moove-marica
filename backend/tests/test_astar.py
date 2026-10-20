
import networkx as nx
import pytest

from app.algorithms.astar import calcular_astar


def criar_grafo_teste():
    grafo = nx.MultiDiGraph()

    grafo.add_node(1, x=0.000, y=0.0)
    grafo.add_node(2, x=0.001, y=0.0)
    grafo.add_node(3, x=0.002, y=0.0)

    # Caminho de 1 até 3 passando pelo nó 2: 240 m
    grafo.add_edge(1, 2, length=120)
    grafo.add_edge(2, 3, length=120)

    # Caminho direto de 1 até 3: 500 m
    grafo.add_edge(1, 3, length=500)

    return grafo


def test_encontra_caminho_mais_curto():
    grafo = criar_grafo_teste()

    caminho, distancia = calcular_astar(grafo, 1, 3)

    assert caminho == [1, 2, 3]
    assert distancia == 240


def test_origem_igual_destino():
    grafo = criar_grafo_teste()

    caminho, distancia = calcular_astar(grafo, 1, 1)

    assert caminho == [1]
    assert distancia == 0


def test_caminho_inexistente():
    grafo = criar_grafo_teste()
    grafo.add_node(4, x=0.003, y=0.0)

    with pytest.raises(ValueError):
        calcular_astar(grafo, 1, 4)
