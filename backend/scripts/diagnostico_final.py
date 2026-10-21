
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BACKEND = Path(__file__).resolve().parents[1]
PROJETO = BACKEND.parent
PASTA_ONIBUS = BACKEND / "data" / "onibus"

API = "http://127.0.0.1:8000"


def verificar_arquivo(nome, caminho):
    existe = caminho.is_file()

    print(
        f"{'OK' if existe else 'PENDENTE'} | "
        f"{nome}: {caminho}"
    )

    return existe


def carregar_json(caminho):
    try:
        with caminho.open(
            "r",
            encoding="utf-8-sig",
        ) as arquivo:
            return json.load(arquivo)
    except (OSError, ValueError) as erro:
        print(f"ERRO ao ler {caminho.name}: {erro}")
        return None


def verificar_grafo():
    print("\n=== MAPAS ===")

    caminho_ambiente = os.getenv("MOOVE_GRAPH_FILE")

    candidatos = []

    if caminho_ambiente:
        caminho = Path(caminho_ambiente)

        if not caminho.is_absolute():
            caminho = BACKEND / caminho

        candidatos.append(caminho)

    candidatos.extend(
        [
            BACKEND / "marica_walk_integrado.graphml",
            BACKEND / "data" / "marica_walk_integrado.graphml",
            PROJETO / "marica_walk_integrado.graphml",
        ]
    )

    grafo_caminhada = next(
        (c for c in candidatos if c.is_file()),
        None,
    )

    if grafo_caminhada:
        print(
            "OK | Grafo de caminhada:",
            grafo_caminhada,
        )
    else:
        print(
            "PENDENTE | Grafo de caminhada "
            "não encontrado nos caminhos conhecidos."
        )

    verificar_arquivo(
        "Grafo de bicicleta",
        BACKEND
        / "data"
        / "marica_bike_ampliado.graphml",
    )


def verificar_itinerarios():
    print("\n=== LINHAS DA EPT ===")

    caminho = PASTA_ONIBUS / "itinerarios_ept.json"

    if not verificar_arquivo(
        "Itinerários",
        caminho,
    ):
        return

    dados = carregar_json(caminho)

    if not isinstance(dados, dict):
        return

    linhas = dados.get("linhas", [])

    print("Registros importados:", len(linhas))

    codigos = {
        str(linha.get("codigo", "")).upper()
        for linha in linhas
        if isinstance(linha, dict)
    }

    print("Códigos distintos:", len(codigos))
    print("E01 encontrada:", "E01" in codigos)


def verificar_pontos():
    print("\n=== PONTOS DE ÔNIBUS ===")

    caminho = (
        PASTA_ONIBUS
        / "pontos_onibus_candidatos.geojson"
    )

    if not verificar_arquivo(
        "Pontos candidatos",
        caminho,
    ):
        return

    dados = carregar_json(caminho)

    if not isinstance(dados, dict):
        return

    pontos = dados.get("features", [])

    print("Pontos candidatos:", len(pontos))

    identificadores = set()

    for feature in pontos:
        propriedades = (
            feature.get("properties") or {}
        )

        identificador = propriedades.get("id")

        if identificador is not None:
            identificadores.add(str(identificador))

    print(
        "IDs distintos:",
        len(identificadores),
    )


def verificar_validacao():
    print("\n=== VALIDAÇÃO DAS PARADAS ===")

    caminho = (
        PASTA_ONIBUS
        / "paradas_linhas_validadas.json"
    )

    if not verificar_arquivo(
        "Paradas validadas",
        caminho,
    ):
        return

    dados = carregar_json(caminho)

    if not isinstance(dados, dict):
        return

    linhas = dados.get("linhas", [])

    if not isinstance(linhas, list):
        print("ERRO | Campo 'linhas' inválido.")
        return

    validadas = [
        linha
        for linha in linhas
        if isinstance(linha, dict)
        and linha.get("validado") is True
    ]

    print(
        "Sequências cadastradas:",
        len(linhas),
    )

    print(
        "Sequências marcadas como validadas:",
        len(validadas),
    )

    if not validadas:
        print(
            "PENDENTE | Nenhuma sequência "
            "de paradas foi validada."
        )


def consultar_api(caminho, metodo="GET", dados=None):
    url = API + caminho

    corpo = None

    if dados is not None:
        corpo = json.dumps(dados).encode("utf-8")

    requisicao = Request(
        url,
        data=corpo,
        method=metodo,
        headers={
            "Content-Type": "application/json"
        },
    )

    try:
        with urlopen(
            requisicao,
            timeout=15,
        ) as resposta:
            conteudo = resposta.read()

            if conteudo:
                return (
                    resposta.status,
                    json.loads(conteudo),
                )

            return resposta.status, None

    except HTTPError as erro:
        try:
            conteudo = json.loads(
                erro.read().decode("utf-8")
            )
        except ValueError:
            conteudo = None

        return erro.code, conteudo

    except (URLError, TimeoutError, OSError) as erro:
        print("API indisponível:", erro)
        return None, None


def verificar_api():
    print("\n=== API FASTAPI ===")

    codigo, dados = consultar_api(
        "/openapi.json"
    )

    if codigo != 200:
        print(
            "PENDENTE | Backend não está "
            "respondendo corretamente."
        )
        return

    print("OK | Backend respondendo.")

    caminhos = dados.get("paths", {})

    endpoints = [
        "/api/rotas",
        "/api/onibus/pontos",
        "/api/onibus/linhas",
        "/api/rotas/onibus/planejar",
    ]

    for endpoint in endpoints:
        existe = endpoint in caminhos

        print(
            f"{'OK' if existe else 'PENDENTE'} | "
            f"Endpoint {endpoint}"
        )

    if "/api/rotas/onibus/planejar" in caminhos:
        codigo, resposta = consultar_api(
            "/api/rotas/onibus/planejar",
            metodo="POST",
            dados={
                "origem": {
                    "lat": -22.9194,
                    "lng": -42.8186,
                },
                "destino": {
                    "lat": -22.956,
                    "lng": -42.697,
                },
                "codigo_linha": "E01",
            },
        )

        print(
            "Planejador de ônibus HTTP:",
            codigo,
        )

        if isinstance(resposta, dict):
            print(
                "Status do planejamento:",
                resposta.get("status", "não informado"),
            )

            print(
                "Total de opções:",
                resposta.get("total_opcoes", 0),
            )

            if codigo != 200:
                print(
                    "Detalhe:",
                    resposta.get("detail"),
                )


def verificar_frontend():
    print("\n=== FRONTEND ===")

    arquivos = [
        "src/App.tsx",
        "src/components/MaricaMap.tsx",
        "src/components/PontosOnibus.tsx",
        "src/components/RotaOnibus.tsx",
        "src/components/PlanejadorOnibus.tsx",
        "src/components/LinhasOnibus.tsx",
    ]

    for arquivo in arquivos:
        verificar_arquivo(
            arquivo,
            PROJETO / "frontend" / arquivo,
        )


def executar():
    print("=" * 55)
    print("MOOVE MARICÁ - DIAGNÓSTICO DE INTEGRAÇÃO")
    print("=" * 55)

    print("Python:", sys.version.split()[0])
    print("Backend:", BACKEND)

    verificar_grafo()
    verificar_itinerarios()
    verificar_pontos()
    verificar_validacao()
    verificar_frontend()
    verificar_api()

    print("\n" + "=" * 55)
    print("DIAGNÓSTICO CONCLUÍDO")
    print("=" * 55)

    print(
        "Os itens PENDENTE precisam ser "
        "conferidos antes de considerar "
        "o sistema finalizado."
    )


if __name__ == "__main__":
    executar()
