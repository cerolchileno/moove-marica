
import json
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[2]

ARQUIVO_PONTOS = (
    BACKEND
    / "data"
    / "onibus"
    / "pontos_onibus_candidatos.geojson"
)


def carregar_pontos_onibus():
    if not ARQUIVO_PONTOS.exists():
        raise FileNotFoundError(
            "Arquivo de pontos de onibus nao encontrado. "
            "Execute primeiro o importador offline."
        )

    with ARQUIVO_PONTOS.open(
        "r",
        encoding="utf-8",
    ) as arquivo:
        dados = json.load(arquivo)

    if dados.get("type") != "FeatureCollection":
        raise ValueError(
            "Arquivo GeoJSON invalido."
        )

    return dados


def listar_pontos_onibus(limite=1000):
    dados = carregar_pontos_onibus()

    pontos = dados.get("features", [])

    return {
        "total": len(pontos),
        "exibidos": min(len(pontos), limite),
        "type": "FeatureCollection",
        "features": pontos[:limite],
    }
