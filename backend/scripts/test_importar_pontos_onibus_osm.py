
import importlib.util
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "importar_pontos_onibus_osm.py"
)

spec = importlib.util.spec_from_file_location(
    "importar_pontos_onibus_osm",
    SCRIPT,
)
modulo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modulo)


def criar_pontos():
    return gpd.GeoDataFrame(
        {
            "name": ["Ponto A", "Ponto B"],
            "ref": ["A", "B"],
            "highway": ["bus_stop", "bus_stop"],
        },
        geometry=[
            Point(-42.80, -22.92),
            Point(-42.81, -22.93),
        ],
        index=gpd.pd.MultiIndex.from_tuples(
            [("node", 100), ("node", 101)]
        ),
        crs="EPSG:4326",
    )


def test_tags_consultam_apenas_bus_stop():
    assert modulo.TAGS == {
        "highway": "bus_stop"
    }


def test_gerar_geojson():
    dados = modulo.gerar_geojson(
        criar_pontos()
    )

    assert dados["type"] == "FeatureCollection"
    assert len(dados["features"]) == 2

    primeiro = dados["features"][0]

    assert primeiro["properties"]["id"] == "node/100"
    assert primeiro["properties"]["nome"] == "Ponto A"
    assert primeiro["properties"]["status"] == (
        "candidato_nao_validado"
    )
    assert primeiro["geometry"]["coordinates"] == [
        -42.80,
        -22.92,
    ]


def test_remover_duplicados():
    pontos = criar_pontos()

    duplicado = pontos.iloc[[0]]
    pontos = gpd.pd.concat(
        [pontos, duplicado]
    )

    dados = modulo.gerar_geojson(pontos)

    assert len(dados["features"]) == 2


def test_troca_automatica_servidor(monkeypatch):
    chamadas = []

    monkeypatch.setattr(
        modulo,
        "SERVIDORES",
        ["https://servidor1/api", "https://servidor2/api"],
    )
    monkeypatch.setattr(
        modulo.time,
        "sleep",
        lambda segundos: None,
    )

    def consulta():
        chamadas.append(
            modulo.ox.settings.overpass_url
        )

        if len(chamadas) == 1:
            raise ConnectionError(
                "Servidor indisponivel"
            )

        return criar_pontos()

    resultado = modulo.consultar_com_servidores(
        consulta,
        "Teste de troca",
    )

    assert len(chamadas) == 2
    assert len(resultado) == 2
    assert chamadas[1] == "https://servidor2/api"


def test_nao_substituir_arquivo_se_consulta_falhar(
    monkeypatch,
    tmp_path,
):
    arquivo = tmp_path / "pontos.geojson"
    arquivo.write_text(
        "arquivo anterior",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        modulo,
        "SAIDA",
        arquivo,
    )

    monkeypatch.setattr(
        modulo,
        "consultar_municipio",
        lambda: (_ for _ in ()).throw(
            RuntimeError("Falha")
        ),
    )

    monkeypatch.setattr(
        modulo,
        "consultar_em_partes",
        lambda: (_ for _ in ()).throw(
            RuntimeError("Falha")
        ),
    )

    with pytest.raises(RuntimeError):
        modulo.importar()

    assert arquivo.read_text(
        encoding="utf-8"
    ) == "arquivo anterior"
