
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import osmium
except ImportError:
    print(
        "Biblioteca osmium nao instalada.\n"
        "Execute: python -m pip install osmium"
    )
    sys.exit(1)


BACKEND = Path(__file__).resolve().parents[1]
PROJETO = BACKEND.parent

PASTA_SAIDA = BACKEND / "data" / "onibus"
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

ARQUIVO_SAIDA = (
    PASTA_SAIDA
    / "pontos_onibus_candidatos.geojson"
)

# Apenas candidatos dentro de uma caixa aproximada
# da regiao de Marica.
# Esses limites NAO sao a fronteira municipal oficial.
LAT_MIN = -23.10
LAT_MAX = -22.65
LON_MIN = -43.05
LON_MAX = -42.45


def localizar_pbf():
    print("Procurando arquivos OSM locais...")

    arquivos = []

    # Busca nos locais mais provaveis primeiro.
    pastas = [
        BACKEND / "data",
        PROJETO / "data",
        PROJETO,
    ]

    vistos = set()

    for pasta in pastas:
        if not pasta.exists():
            continue

        for arquivo in pasta.rglob("*.osm.pbf"):
            caminho = arquivo.resolve()

            if caminho not in vistos:
                vistos.add(caminho)
                arquivos.append(caminho)

    if not arquivos:
        return None

    print("\nArquivos encontrados:")

    for numero, arquivo in enumerate(
        arquivos, start=1
    ):
        tamanho = arquivo.stat().st_size / (1024 * 1024)

        print(
            f"{numero}. {arquivo} "
            f"({tamanho:.1f} MB)"
        )

    # Prefere arquivo cujo nome mencione Marica.
    for arquivo in arquivos:
        if "marica" in arquivo.name.lower():
            return arquivo

    # Caso contrario, escolhe o primeiro.
    return arquivos[0]


class ExtratorPontos(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()

        self.pontos = []
        self.identificadores = set()

        self.total_visitado = 0
        self.total_bus_stop = 0

    def node(self, node):
        self.total_visitado += 1

        if node.tags.get("highway") != "bus_stop":
            return

        self.total_bus_stop += 1

        if not node.location.valid():
            return

        latitude = float(node.location.lat)
        longitude = float(node.location.lon)

        if not (
            LAT_MIN <= latitude <= LAT_MAX
            and LON_MIN <= longitude <= LON_MAX
        ):
            return

        identificador = f"node/{node.id}"

        if identificador in self.identificadores:
            return

        self.identificadores.add(identificador)

        self.pontos.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    longitude,
                    latitude,
                ],
            },
            "properties": {
                "id": identificador,
                "nome": node.tags.get("name"),
                "referencia": node.tags.get("ref"),
                "highway": "bus_stop",
                "public_transport": node.tags.get(
                    "public_transport"
                ),
                "shelter": node.tags.get("shelter"),
                "bench": node.tags.get("bench"),
                "fonte": "OpenStreetMap local",
                "status": "candidato_nao_validado",
                "linha_ept": None,
            },
        })


def importar():
    print("=" * 60)
    print("MOOVE MARICA")
    print("IMPORTADOR OFFLINE DE PONTOS DE ONIBUS")
    print("=" * 60)

    arquivo_pbf = localizar_pbf()

    if arquivo_pbf is None:
        print("\nERRO: Nenhum arquivo .osm.pbf encontrado.")
        print(
            "Coloque o extrato OSM em "
            "backend/data/ e execute novamente."
        )
        return 1

    print("\nArquivo selecionado:")
    print(arquivo_pbf)

    print("\nExtraindo pontos de onibus...")
    print("Nenhuma conexao com Overpass sera utilizada.")

    extrator = ExtratorPontos()

    try:
        extrator.apply_file(
            str(arquivo_pbf),
            locations=True,
        )
    except Exception as erro:
        print(
            "\nErro ao ler o arquivo OSM:",
            erro,
        )
        return 1

    print("\nNos OSM analisados:", extrator.total_visitado)
    print(
        "Pontos bus_stop no extrato:",
        extrator.total_bus_stop,
    )
    print(
        "Candidatos na regiao:",
        len(extrator.pontos),
    )

    if not extrator.pontos:
        print(
            "\nNenhum ponto encontrado. "
            "Verifique a cobertura do extrato."
        )
        return 1

    resultado = {
        "type": "FeatureCollection",
        "metadata": {
            "municipio_referencia": "Marica",
            "fonte": "OpenStreetMap",
            "arquivo_origem": arquivo_pbf.name,
            "extraido_em_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "observacao": (
                "Pontos candidatos extraidos de uma "
                "caixa geografica aproximada. "
                "Nao sao paradas oficiais confirmadas "
                "da EPT e podem incluir pontos "
                "fora de Marica."
            ),
        },
        "features": extrator.pontos,
    }

    temporario = ARQUIVO_SAIDA.with_name(
        ARQUIVO_SAIDA.name + ".tmp"
    )

    try:
        temporario.write_text(
            json.dumps(
                resultado,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        temporario.replace(ARQUIVO_SAIDA)

    except OSError as erro:
        print("\nErro ao salvar:", erro)
        return 1

    print("\n" + "=" * 60)
    print("IMPORTACAO CONCLUIDA")
    print("=" * 60)
    print("Pontos encontrados:", len(extrator.pontos))
    print("Arquivo gerado:", ARQUIVO_SAIDA)

    return 0


if __name__ == "__main__":
    sys.exit(importar())
