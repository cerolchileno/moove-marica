
import json

import pytest

from app.services import planejador_onibus


def escrever_json(caminho, dados):
    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho.write_text(
        json.dumps(
            dados,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


@pytest.fixture
def dados_teste(tmp_path, monkeypatch):
    arquivo_pontos = tmp_path / "pontos.geojson"
    arquivo_linhas = tmp_path / "linhas.json"

    pontos = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-42.8186, -22.9194],
                },
                "properties": {
                    "id": "teste-1",
                    "nome": "Parada A",
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-42.8140, -22.9200],
                },
                "properties": {
                    "id": "teste-2",
                    "nome": "Parada B",
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-42.8090, -22.9210],
                },
                "properties": {
                    "id": "teste-3",
                    "nome": "Parada C",
                },
            },
        ],
    }

    linhas = {
        "versao": 1,
        "fonte": "dados_sinteticos_de_teste",
        "linhas": [
            {
                "codigo": "E01",
                "sentido": "ida",
                "paradas": [
                    "teste-1",
                    "teste-2",
                    "teste-3",
                ],
                "validado": True,
            },
            {
                "codigo": "E01",
                "sentido": "volta",
                "paradas": [
                    "teste-3",
                    "teste-2",
                    "teste-1",
                ],
                "validado": True,
            },
        ],
    }

    escrever_json(arquivo_pontos, pontos)
    escrever_json(arquivo_linhas, linhas)

    monkeypatch.setattr(
        planejador_onibus,
        "ARQUIVO_PONTOS",
        arquivo_pontos,
    )

    monkeypatch.setattr(
        planejador_onibus,
        "ARQUIVO_LINHAS",
        arquivo_linhas,
    )

    return {
        "pontos": pontos,
        "linhas": linhas,
    }


def test_haversine_mesmo_ponto():
    distancia = planejador_onibus.haversine(
        -22.9194,
        -42.8186,
        -22.9194,
        -42.8186,
    )

    assert distancia == pytest.approx(0)


def test_rota_ida(dados_teste):
    resultado = planejador_onibus.calcular_opcoes(
        origem_lat=-22.9194,
        origem_lng=-42.8186,
        destino_lat=-22.9210,
        destino_lng=-42.8090,
        codigo_linha="E01",
    )

    assert resultado["total_opcoes"] > 0
    assert resultado["melhor_opcao"] is not None
    assert resultado["melhor_opcao"]["codigo"] == "E01"

    assert (
        resultado["melhor_opcao"]["sentido"]
        == "ida"
    )


def test_rota_volta(dados_teste):
    resultado = planejador_onibus.calcular_opcoes(
        origem_lat=-22.9210,
        origem_lng=-42.8090,
        destino_lat=-22.9194,
        destino_lng=-42.8186,
        codigo_linha="E01",
    )

    assert resultado["total_opcoes"] > 0
    assert (
        resultado["melhor_opcao"]["sentido"]
        == "volta"
    )


def test_sem_linhas_validadas(
    tmp_path,
    monkeypatch,
    dados_teste,
):
    arquivo_linhas = tmp_path / "linhas_vazias.json"

    escrever_json(
        arquivo_linhas,
        {
            "versao": 1,
            "linhas": [],
        },
    )

    monkeypatch.setattr(
        planejador_onibus,
        "ARQUIVO_LINHAS",
        arquivo_linhas,
    )

    resultado = planejador_onibus.calcular_opcoes(
        origem_lat=-22.9194,
        origem_lng=-42.8186,
        destino_lat=-22.9210,
        destino_lng=-42.8090,
        codigo_linha="E01",
    )

    assert resultado["status"] == "sem_rota_validada"
    assert resultado["total_opcoes"] == 0
    assert resultado["melhor_opcao"] is None


def test_linha_inexistente(dados_teste):
    resultado = planejador_onibus.calcular_opcoes(
        origem_lat=-22.9194,
        origem_lng=-42.8186,
        destino_lat=-22.9210,
        destino_lng=-42.8090,
        codigo_linha="E99",
    )

    assert resultado["total_opcoes"] == 0
    assert resultado["melhor_opcao"] is None


def test_ignorar_linha_nao_validada(
    tmp_path,
    monkeypatch,
    dados_teste,
):
    arquivo_linhas = tmp_path / "nao_validada.json"

    escrever_json(
        arquivo_linhas,
        {
            "linhas": [
                {
                    "codigo": "E01",
                    "sentido": "ida",
                    "paradas": [
                        "teste-1",
                        "teste-2",
                    ],
                    "validado": False,
                }
            ]
        },
    )

    monkeypatch.setattr(
        planejador_onibus,
        "ARQUIVO_LINHAS",
        arquivo_linhas,
    )

    resultado = planejador_onibus.calcular_opcoes(
        origem_lat=-22.9194,
        origem_lng=-42.8186,
        destino_lat=-22.9210,
        destino_lng=-42.8090,
        codigo_linha="E01",
    )

    assert resultado["total_opcoes"] == 0


def test_coordenadas_da_rota(dados_teste):
    resultado = planejador_onibus.calcular_opcoes(
        origem_lat=-22.9194,
        origem_lng=-42.8186,
        destino_lat=-22.9210,
        destino_lng=-42.8090,
        codigo_linha="E01",
    )

    opcao = resultado["melhor_opcao"]

    assert opcao is not None
    assert len(opcao["coordenadas"]) >= 2

    for coordenada in opcao["coordenadas"]:
        assert len(coordenada) == 2
        assert isinstance(coordenada[0], float)
        assert isinstance(coordenada[1], float)
