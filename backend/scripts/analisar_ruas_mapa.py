
import os
from collections import Counter
from pathlib import Path

import networkx as nx


BASE_DIR = Path(__file__).resolve().parents[1]


ARQUIVO_GRAFO = os.environ.get(
    "MOOVE_GRAPH_FILE",
    "marica_walk_integrado.graphml",
)

CAMINHO = Path(ARQUIVO_GRAFO)

if not CAMINHO.is_absolute():
    candidatos = [
        BASE_DIR / CAMINHO,
        BASE_DIR.parent / CAMINHO,
        BASE_DIR / "data" / CAMINHO,
    ]

    encontrado = next(
        (p for p in candidatos if p.is_file()),
        None,
    )

    if encontrado is not None:
        CAMINHO = encontrado
    else:
        print("\nMapa não encontrado nos locais padrão.")
        print("Arquivos GraphML disponíveis:\n")

        for arquivo in BASE_DIR.parent.rglob("*.graphml"):
            print(arquivo)

        raise FileNotFoundError(
            f"Não foi possível localizar: {ARQUIVO_GRAFO}"
        )

print(f"Mapa selecionado: {CAMINHO}")



def analisar():
    if not CAMINHO.exists():
        raise FileNotFoundError(
            f"Mapa não encontrado: {CAMINHO}"
        )

    print("Carregando mapa...")
    grafo = nx.read_graphml(CAMINHO)

    print("Nós:", grafo.number_of_nodes())
    print("Arestas:", grafo.number_of_edges())

    nomes = Counter()
    sem_nome = 0

    for _, _, dados in grafo.edges(data=True):
        nome = dados.get("name")

        if not nome:
            sem_nome += 1
            continue

        if isinstance(nome, list):
            valores = nome
        else:
            valores = [str(nome)]

        for valor in valores:
            valor = str(valor).strip()

            if valor:
                nomes[valor] += 1

    print("\nArestas sem nome:", sem_nome)
    print("Nomes distintos:", len(nomes))

    print("\n30 nomes mais frequentes:")

    for nome, quantidade in nomes.most_common(30):
        print(f"{quantidade:6} | {nome}")

    print("\nANÁLISE CONCLUÍDA")


if __name__ == "__main__":
    analisar()
