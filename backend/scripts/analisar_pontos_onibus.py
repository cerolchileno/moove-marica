
import csv
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PASTA = BASE / "data" / "onibus"

ENTRADA = PASTA / "pontos_onibus_candidatos.geojson"
SAIDA = PASTA / "relatorio_pontos_onibus.csv"


def analisar():
    if not ENTRADA.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {ENTRADA}"
        )

    dados = json.loads(
        ENTRADA.read_text(encoding="utf-8")
    )

    pontos = dados.get("features", [])
    registros = []
    ids = set()
    duplicados = 0

    for ponto in pontos:
        propriedades = ponto.get("properties", {})
        geometria = ponto.get("geometry", {})

        coordenadas = geometria.get("coordinates", [])

        if (
            geometria.get("type") != "Point"
            or len(coordenadas) < 2
        ):
            continue

        identificador = propriedades.get("id")

        if identificador in ids:
            duplicados += 1
            continue

        ids.add(identificador)

        longitude, latitude = coordenadas[:2]

        registros.append({
            "id": identificador,
            "nome": propriedades.get("nome") or "",
            "referencia": propriedades.get("referencia") or "",
            "latitude": latitude,
            "longitude": longitude,
            "status": propriedades.get("status") or "",
        })

    with SAIDA.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as arquivo:
        campos = [
            "id",
            "nome",
            "referencia",
            "latitude",
            "longitude",
            "status",
        ]

        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos,
        )

        escritor.writeheader()
        escritor.writerows(registros)

    com_nome = sum(
        bool(item["nome"]) for item in registros
    )

    com_referencia = sum(
        bool(item["referencia"]) for item in registros
    )

    print("\nRELATORIO DE PONTOS DE ONIBUS")
    print("=" * 45)
    print("Total no GeoJSON:", len(pontos))
    print("Pontos validos e unicos:", len(registros))
    print("Duplicados ignorados:", duplicados)
    print("Pontos com nome:", com_nome)
    print("Pontos com referencia:", com_referencia)
    print("Arquivo CSV:", SAIDA)

    print("\nPrimeiros 10 pontos:")

    for item in registros[:10]:
        print(
            item["id"],
            "|",
            item["nome"] or "Sem nome",
            "|",
            item["latitude"],
            item["longitude"],
        )


if __name__ == "__main__":
    analisar()
