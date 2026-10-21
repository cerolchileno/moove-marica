
from pathlib import Path

import osmium


BASE_DIR = Path(__file__).resolve().parents[1]

ARQUIVO_ORIGEM = BASE_DIR / "data" / "sudeste-261020.osm.pbf"

ARQUIVO_DESTINO = (
    BASE_DIR / "data" / "extracoes" / "marica_ampliado.osm.pbf"
)

# Área aproximada de Maricá e arredores
LAT_MIN = -23.02
LAT_MAX = -22.75
LON_MIN = -42.99
LON_MAX = -42.55


def dentro_da_area(lat, lon):
    return (
        LAT_MIN <= lat <= LAT_MAX
        and LON_MIN <= lon <= LON_MAX
    )


class SelecionadorRuas(osmium.SimpleHandler):
    def __init__(self, escritor):
        super().__init__()
        self.escritor = escritor
        self.total_ruas = 0
        self.ruas_selecionadas = 0

    def way(self, rua):
        if "highway" not in rua.tags:
            return

        self.total_ruas += 1

        # Com locations=True, os nós da rua
        # possuem coordenadas disponíveis.
        for no in rua.nodes:
            if not no.location.valid():
                continue

            if dentro_da_area(no.lat, no.lon):
                self.escritor.add_way(rua)
                self.ruas_selecionadas += 1
                break


def main():
    if not ARQUIVO_ORIGEM.exists():
        print("ERRO: arquivo PBF original não encontrado.")
        return

    ARQUIVO_DESTINO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if ARQUIVO_DESTINO.exists():
        print("A extração já existe.")
        print("Nenhum arquivo foi sobrescrito.")
        return

    print("Iniciando seleção das ruas de Maricá...")
    print("O processamento pode levar alguns minutos.")

    with osmium.BackReferenceWriter(
        str(ARQUIVO_DESTINO),
        str(ARQUIVO_ORIGEM),
        overwrite=False,
        remove_tags=False,
    ) as escritor:

        selecionador = SelecionadorRuas(escritor)

        selecionador.apply_file(
            str(ARQUIVO_ORIGEM),
            locations=True,
        )

        print(
            "Ruas analisadas:",
            selecionador.total_ruas,
        )
        print(
            "Ruas selecionadas:",
            selecionador.ruas_selecionadas,
        )

    print("Extração concluída!")
    print("Arquivo:", ARQUIVO_DESTINO)
    print(
        "Tamanho:",
        round(
            ARQUIVO_DESTINO.stat().st_size / (1024**2),
            2,
        ),
        "MiB",
    )


if __name__ == "__main__":
    main()
