
from pathlib import Path

import osmnx as ox


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def main():
    print("Moove Marica - Análise de conflitos")
    print("----------------------------------")

    original = ox.load_graphml(
        DATA_DIR / "marica_walk.graphml"
    )

    regional = ox.load_graphml(
        DATA_DIR / "marica_walk_cordeirinho.graphml"
    )

    conflitos = 0

    for origem, destino, chave, dados_regionais in regional.edges(
        keys=True,
        data=True,
    ):
        if not original.has_edge(origem, destino, chave):
            continue

        dados_originais = original.edges[
            origem, destino, chave
        ]

        if dict(dados_originais) == dict(dados_regionais):
            continue

        conflitos += 1

        print(f"\nConflito {conflitos}")
        print(f"Aresta: {origem} -> {destino} (chave {chave})")

        campos = set(dados_originais) | set(dados_regionais)

        for campo in sorted(campos):
            valor_original = dados_originais.get(campo)
            valor_regional = dados_regionais.get(campo)

            if valor_original != valor_regional:
                print(f"  Campo: {campo}")
                print(f"    Original: {valor_original}")
                print(f"    Regional: {valor_regional}")

    print(f"\nTotal de conflitos: {conflitos}")
    print("Análise concluída!")


if __name__ == "__main__":
    main()
