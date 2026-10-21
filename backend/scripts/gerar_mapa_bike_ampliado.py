
from pathlib import Path
import math

import networkx as nx
import osmium


BASE_DIR = Path(__file__).resolve().parents[1]

ARQUIVO_PBF = (
    BASE_DIR / "data" / "extracoes"
    / "marica_ampliado.osm.pbf"
)

ARQUIVO_GRAFO = (
    BASE_DIR / "data" / "marica_bike_ampliado.graphml"
)

# Tipos de vias considerados candidatos para bicicleta.
# A inclusão não garante que sejam seguros ou legalmente
# permitidos em todas as circunstâncias.
VIAS_CANDIDATAS = {
    "cycleway",
    "residential",
    "living_street",
    "tertiary",
    "tertiary_link",
    "secondary",
    "secondary_link",
    "unclassified",
    "service",
    "track",
    "path",
}

ACESSO_PROIBIDO = {"no", "private", "customers"}


def distancia_m(lat1, lon1, lat2, lon2):
    raio = 6371000
    a1 = math.radians(lat1)
    a2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(a1) * math.cos(a2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * raio * math.asin(min(1, math.sqrt(a)))


class ConstrutorGrafo(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.grafo = nx.MultiDiGraph()
        self.vias_aceitas = 0
        self.vias_descartadas = 0

    def way(self, via):
        tags = dict(via.tags)
        tipo = tags.get("highway", "")

        if tipo not in VIAS_CANDIDATAS:
            self.vias_descartadas += 1
            return

        # Restrições explícitas para bicicletas.
        if tags.get("bicycle") in ACESSO_PROIBIDO:
            self.vias_descartadas += 1
            return

        # Restrições gerais de acesso.
        if (
            tags.get("access") in ACESSO_PROIBIDO
            and tags.get("bicycle") not in {"yes", "designated"}
        ):
            self.vias_descartadas += 1
            return

        if (
            tags.get("vehicle") in ACESSO_PROIBIDO
            and tags.get("bicycle") not in {"yes", "designated"}
        ):
            self.vias_descartadas += 1
            return

        pontos = []

        for no in via.nodes:
            if not no.location.valid():
                continue

            pontos.append(
                (str(no.ref), float(no.lat), float(no.lon))
            )

        if len(pontos) < 2:
            self.vias_descartadas += 1
            return

        # Oneway para bicicletas pode ser diferente
        # do sentido dos carros.
        sentido_bike = tags.get("oneway:bicycle")
        sentido_geral = tags.get("oneway", "no")

        if sentido_bike in {"yes", "1", "true"}:
            sentido = "direto"
        elif sentido_bike == "-1":
            sentido = "inverso"
        elif sentido_bike in {"no", "0", "false"}:
            sentido = "duplo"
        elif sentido_geral in {"yes", "1", "true"}:
            sentido = "direto"
        elif sentido_geral == "-1":
            sentido = "inverso"
        else:
            sentido = "duplo"

        for identificador, lat, lon in pontos:
            self.grafo.add_node(
                identificador,
                y=lat,
                x=lon,
            )

        for inicio, fim in zip(pontos[:-1], pontos[1:]):
            id_a, lat_a, lon_a = inicio
            id_b, lat_b, lon_b = fim

            comprimento = distancia_m(
                lat_a, lon_a, lat_b, lon_b
            )

            atributos = {
                "length": comprimento,
                "highway": tipo,
                "osmid": str(via.id),
            }

            if sentido in {"direto", "duplo"}:
                self.grafo.add_edge(
                    id_a, id_b, **atributos
                )

            if sentido in {"inverso", "duplo"}:
                self.grafo.add_edge(
                    id_b, id_a, **atributos
                )

        self.vias_aceitas += 1


def main():
    if not ARQUIVO_PBF.exists():
        print("ERRO: PBF extraído não encontrado.")
        return

    if ARQUIVO_GRAFO.exists():
        print("O grafo ampliado já existe.")
        print("Nenhum arquivo foi sobrescrito.")
        return

    print("Construindo grafo de bicicletas...")

    construtor = ConstrutorGrafo()
    construtor.apply_file(
        str(ARQUIVO_PBF),
        locations=True,
    )

    grafo = construtor.grafo

    if grafo.number_of_edges() == 0:
        print("ERRO: nenhuma conexão foi encontrada.")
        return

    print("Vias aceitas:", construtor.vias_aceitas)
    print("Vias descartadas:", construtor.vias_descartadas)
    print("Nós:", grafo.number_of_nodes())
    print("Arestas:", grafo.number_of_edges())

    componentes = list(
        nx.weakly_connected_components(grafo)
    )

    maior = max(len(c) for c in componentes)

    print("Componentes conectados:", len(componentes))
    print("Nós no maior componente:", maior)

    nx.write_graphml(grafo, ARQUIVO_GRAFO)

    print("Grafo salvo em:", ARQUIVO_GRAFO)
    print("Mapa atual preservado.")


if __name__ == "__main__":
    main()
