
import csv
import json
import math
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
PASTA_ONIBUS = BASE / "data" / "onibus"

ARQUIVO_PONTOS = (
    PASTA_ONIBUS / "pontos_onibus_candidatos.geojson"
)

ARQUIVO_ITINERARIOS = (
    PASTA_ONIBUS / "itinerarios_ept.json"
)

ARQUIVO_RELATORIO = (
    PASTA_ONIBUS / "validacao_e01.csv"
)

ARQUIVO_RESUMO = (
    PASTA_ONIBUS / "validacao_e01_resumo.json"
)


def carregar_json(caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    return json.loads(
        caminho.read_text(encoding="utf-8")
    )


def extrair_linha_e01(dados):
    linhas = dados.get("linhas", [])

    return [
        linha
        for linha in linhas
        if str(linha.get("codigo", "")).upper() == "E01"
    ]


def extrair_pontos(dados):
    resultado = []

    for feature in dados.get("features", []):
        geometria = feature.get("geometry") or {}
        propriedades = feature.get("properties") or {}

        if geometria.get("type") != "Point":
            continue

        coordenadas = geometria.get("coordinates") or []

        if len(coordenadas) < 2:
            continue

        lng, lat = coordenadas[:2]

        try:
            lat = float(lat)
            lng = float(lng)
        except (ValueError, TypeError):
            continue

        resultado.append({
            "id": str(propriedades.get("id", "")),
            "nome": propriedades.get("nome") or "",
            "referencia": (
                propriedades.get("referencia") or ""
            ),
            "lat": lat,
            "lng": lng,
            "status": "candidato_nao_validado",
        })

    return resultado


def executar():
    itinerarios = carregar_json(
        ARQUIVO_ITINERARIOS
    )

    geojson = carregar_json(
        ARQUIVO_PONTOS
    )

    linhas_e01 = extrair_linha_e01(itinerarios)
    pontos = extrair_pontos(geojson)

    if not linhas_e01:
        raise ValueError(
            "A linha E01 não foi encontrada."
        )

    PASTA_ONIBUS.mkdir(
        parents=True,
        exist_ok=True,
    )

    with ARQUIVO_RELATORIO.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=[
                "id",
                "nome",
                "referencia",
                "lat",
                "lng",
                "status",
                "pertence_e01",
                "sentido",
                "ordem",
                "observacoes",
            ],
            delimiter=";",
        )

        escritor.writeheader()

        for ponto in pontos:
            escritor.writerow({
                **ponto,
                "pertence_e01": "",
                "sentido": "",
                "ordem": "",
                "observacoes": "",
            })

    resumo = {
        "linha": "E01",
        "itinerarios_encontrados": len(linhas_e01),
        "total_pontos_candidatos": len(pontos),
        "pontos_validados": 0,
        "status": "aguardando_validacao",
        "itinerarios": [
            {
                "nome": linha.get("nome"),
                "ida": linha.get("ida"),
                "volta": linha.get("volta"),
            }
            for linha in linhas_e01
        ],
        "aviso": (
            "Os pontos foram extraídos do OpenStreetMap. "
            "Ainda não existe comprovação de que "
            "pertençam à linha E01."
        ),
    }

    ARQUIVO_RESUMO.write_text(
        json.dumps(
            resumo,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("Preparação da E01 concluída.")
    print(
        "Itinerários encontrados:",
        len(linhas_e01),
    )
    print(
        "Pontos candidatos:",
        len(pontos),
    )
    print("CSV:", ARQUIVO_RELATORIO)
    print("Resumo:", ARQUIVO_RESUMO)


if __name__ == "__main__":
    executar()
