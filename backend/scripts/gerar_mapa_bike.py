
import json
from collections import Counter
from pathlib import Path

import networkx as nx
import osmnx as ox


BASE_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = Path(ox.settings.cache_folder)
DESTINO = BASE_DIR / "data" / "marica_bike_experimental.graphml"

TIPOS_PERMITIDOS = {
    "residential",
    "living_street",
    "tertiary",
    "secondary",
    "unclassified",
}

ACESSO_BLOQUEADO = {
    "no",
    "private",
    "customers",
}

def carregar_dados():
    nos = {}
    vias = {}

    for arquivo in CACHE_DIR.glob("*.json"):
        with arquivo.open(encoding="utf-8") as f:
            dados = json.load(f)

        if not isinstance(dados, dict):
            continue

        for elemento in dados.get("elements", []):
            tipo = elemento.get("type")
            identificador = elemento.get("id")

            if tipo == "node":
                if "lat" in elemento and "lon" in elemento:
                    nos[identificador] = elemento

            elif tipo == "way":
                if "nodes" in elemento:
                    vias[identificador] = elemento

    return nos, vias


def via_aceita(tags):
    if tags.get("highway") not in TIPOS_PERMITIDOS:
        return False

    for atributo in ("access", "vehicle", "bicycle"):
        if tags.get(atributo) in ACESSO_BLOQUEADO:
            return False

    return True


def main():
    print("Moove Marica - Mapa experimental de bicicletas")
    print("Lendo cache local do OSMnx...")

    nos, vias = carregar_dados()

    print("Nos OSM encontrados:", len(nos))
    print("Vias OSM encontradas:", len(vias))

    grafo = nx.MultiDiGraph()
    grafo.graph["crs"] = "epsg:4326"

    contagem = Counter()

    for via in vias.values():
        tags = via.get("tags", {})

        if not via_aceita(tags):
            continue

        sequencia = via["nodes"]

        if len(sequencia) < 2:
            continue

        sentido = tags.get("oneway", "no")
        bicicleta_contrafluxo = (
            tags.get("oneway:bicycle") == "no"
            or tags.get("cycleway") in {
                "opposite",
                "opposite_lane",
                "opposite_track",
            }
        )

        for origem, destino in zip(sequencia, sequencia[1:]):
            if origem not in nos or destino not in nos:
                continue

            for identificador in (origem, destino):
                if identificador not in grafo:
                    ponto = nos[identificador]
                    grafo.add_node(
                        identificador,
                        x=float(ponto["lon"]),
                        y=float(ponto["lat"]),
                    )

            ponto_a = nos[origem]
            ponto_b = nos[destino]

            distancia = ox.distance.great_circle(
                ponto_a["lat"],
                ponto_a["lon"],
                ponto_b["lat"],
                ponto_b["lon"],
            )

            atributos = {
                "osmid": via["id"],
                "highway": tags["highway"],
                "length": float(distancia),
            }

            if sentido == "-1" and not bicicleta_contrafluxo:
                grafo.add_edge(destino, origem, **atributos)

            elif sentido == "yes" and not bicicleta_contrafluxo:
                grafo.add_edge(origem, destino, **atributos)

            else:
                grafo.add_edge(origem, destino, **atributos)
                grafo.add_edge(destino, origem, **atributos)

            contagem[tags["highway"]] += 1

    if grafo.number_of_edges() == 0:
        print("Nenhuma aresta foi gerada.")
        return

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(grafo, filepath=DESTINO)

    print("\nMapa experimental criado!")
    print("Nos:", grafo.number_of_nodes())
    print("Arestas:", grafo.number_of_edges())
    print("Arquivo:", DESTINO)

    print("\nTipos de via:")
    for tipo, quantidade in contagem.most_common():
        print(f"  {tipo}: {quantidade}")

    print("\nATENCAO: rede experimental, nao validada para navegacao real.")


if __name__ == "__main__":
    main()
