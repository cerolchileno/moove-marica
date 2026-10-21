
from pathlib import Path

import networkx as nx
import osmnx as ox


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

MAPA_ORIGINAL = DATA_DIR / "marica_walk.graphml"
MAPA_REGIONAL = DATA_DIR / "marica_walk_cordeirinho.graphml"
MAPA_INTEGRADO = DATA_DIR / "marica_walk_integrado.graphml"


def main():
    print("Moove Marica - Integração experimental")
    print("------------------------------------")

    if MAPA_INTEGRADO.exists():
        print("O mapa integrado já existe.")
        print("Nenhum arquivo foi substituído.")
        return

    original = ox.load_graphml(MAPA_ORIGINAL)
    regional = ox.load_graphml(MAPA_REGIONAL)

    # Ambos os mapas são redes direcionadas com múltiplas arestas.
    if not (
        isinstance(original, nx.MultiDiGraph)
        and isinstance(regional, nx.MultiDiGraph)
    ):
        raise TypeError("Os mapas precisam ser MultiDiGraph.")

    # Preserva a estrutura e os atributos do mapa original.
    integrado = original.copy()

    # Adiciona somente nós que ainda não existem.
    for no, dados in regional.nodes(data=True):
        if no not in integrado:
            integrado.add_node(no, **dados)

    # Adiciona arestas regionais sem sobrescrever as existentes.
    arestas_adicionadas = 0
    arestas_ja_existentes = 0
    conflitos = 0

    for origem, destino, chave, dados in regional.edges(
        keys=True,
        data=True,
    ):
        if integrado.has_edge(origem, destino, chave):
            existente = integrado.edges[origem, destino, chave]

            if dict(existente) != dict(dados):
                conflitos += 1

            arestas_ja_existentes += 1
            continue

        integrado.add_edge(
            origem,
            destino,
            key=chave,
            **dados,
        )
        arestas_adicionadas += 1

    print(f"Nós integrados: {integrado.number_of_nodes()}")
    print(f"Arestas integradas: {integrado.number_of_edges()}")
    print(f"Arestas adicionadas: {arestas_adicionadas}")
    print(f"Arestas já existentes: {arestas_ja_existentes}")
    print(f"Arestas com atributos diferentes: {conflitos}")

    componentes_fracos = nx.number_weakly_connected_components(
        integrado
    )

    print(f"Componentes fracamente conectados: {componentes_fracos}")

    ox.save_graphml(
        integrado,
        filepath=MAPA_INTEGRADO,
    )

    print("\nMapa experimental salvo com sucesso!")
    print(MAPA_INTEGRADO)
    print(
        "\nATENÇÃO: O mapa principal não foi alterado. "
        "Ainda precisamos validar a integração."
    )


if __name__ == "__main__":
    main()
