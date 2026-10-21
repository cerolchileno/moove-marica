
from pathlib import Path

import osmnx as ox


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def main():
    print("Moove Marica - Comparação de grafos")
    print("----------------------------------")

    original = ox.load_graphml(
        DATA_DIR / "marica_walk.graphml"
    )

    regional = ox.load_graphml(
        DATA_DIR / "marica_walk_cordeirinho.graphml"
    )

    nos_original = set(original.nodes)
    nos_regional = set(regional.nodes)

    nos_comuns = nos_original & nos_regional
    nos_novos = nos_regional - nos_original

    print(f"Nós do mapa original: {len(nos_original)}")
    print(f"Nós do mapa regional: {len(nos_regional)}")
    print(f"Nós compartilhados: {len(nos_comuns)}")
    print(f"Nós novos: {len(nos_novos)}")

    if nos_comuns:
        print("\nExistem nós compartilhados entre os mapas.")
        print("Podemos investigar a integração das redes.")
    else:
        print("\nNão foram encontrados nós compartilhados.")
        print("Será necessário investigar a conexão entre as redes.")

    print("\nComparação concluída!")


if __name__ == "__main__":
    main()
