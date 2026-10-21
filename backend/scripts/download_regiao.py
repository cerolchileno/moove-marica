
from pathlib import Path

import osmnx as ox


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ARQUIVO_SAIDA = DATA_DIR / "marica_walk_cordeirinho.graphml"

# Centro aproximado entre os pontos testados anteriormente.
CENTRO = (-22.94623, -42.75201)

# Raio inicial de 2.000 metros.
RAIO_METROS = 2000


def main():
    print("Moove Marica - Download regional")
    print("Região: Cordeirinho / Balneário Bambuí")
    print(f"Raio solicitado: {RAIO_METROS} metros")

    if ARQUIVO_SAIDA.exists():
        print("O arquivo regional já existe.")
        print("Nenhum arquivo foi substituído.")
        return

    # Limita o tamanho das consultas ao serviço Overpass.
    ox.settings.timeout = 180

    print("\nConsultando ruas do OpenStreetMap...")

    grafo = ox.graph_from_point(
        center_point=CENTRO,
        dist=RAIO_METROS,
        network_type="walk",
        simplify=True,
        retain_all=True,
    )

    print(f"Nós encontrados: {grafo.number_of_nodes()}")
    print(f"Arestas encontradas: {grafo.number_of_edges()}")

    ox.save_graphml(grafo, filepath=ARQUIVO_SAIDA)

    print("\nDownload concluído!")
    print(f"Arquivo salvo em: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
