
import os
from functools import lru_cache
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2

import networkx as nx
import osmnx as ox

from app.algorithms.astar import calcular_astar


# ============================================================
# CAMINHOS DOS ARQUIVOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

# Mantém o mapa de caminhada configurável.
GRAPH_PATH = DATA_DIR / os.getenv(
    "MOOVE_GRAPH_FILE",
    "marica_walk.graphml",
)

# Novo mapa ampliado de bicicletas.
BIKE_GRAPH_PATH = DATA_DIR / "marica_bike_ampliado.graphml"


# ============================================================
# CONFIGURAÇÕES DAS ROTAS
# ============================================================

# Distância máxima permitida entre o ponto escolhido
# pelo usuário e a rua mais próxima do mapa.
DISTANCIA_MAXIMA_REDE_M = 200

# Velocidades médias utilizadas para estimar o tempo.
VELOCIDADES_KMH = {
    "caminhada": 5.0,
    "bicicleta": 15.0,
}


# ============================================================
# CARREGAMENTO DOS GRAFOS
# ============================================================

@lru_cache(maxsize=2)
def carregar_grafo(modalidade="caminhada"):

    if modalidade == "caminhada":
        caminho = GRAPH_PATH

    elif modalidade == "bicicleta":
        caminho = BIKE_GRAPH_PATH

    else:
        raise ValueError(
            "Modalidade de transporte inválida."
        )

    if not caminho.exists():
        raise FileNotFoundError(
            f"Mapa da modalidade '{modalidade}' não encontrado: "
            f"{caminho.name}"
        )

    # --------------------------------------------------------
    # MAPA DE BICICLETAS
    # --------------------------------------------------------

    if modalidade == "bicicleta":

        # Carrega o grafo ampliado gerado com NetworkX.
        grafo = nx.read_graphml(caminho)

        # Informa ao OSMnx que as coordenadas dos nós
        # estão em latitude/longitude (WGS84).
        # Isso evita o erro KeyError: 'crs'.
        grafo.graph["crs"] = "EPSG:4326"

        # O algoritmo A* do projeto utiliza MultiDiGraph.
        grafo = nx.MultiDiGraph(grafo)

        return grafo

    # --------------------------------------------------------
    # MAPA DE CAMINHADA
    # --------------------------------------------------------

    # Mantém o carregamento original da caminhada.
    return ox.load_graphml(caminho)


# ============================================================
# DISTÂNCIA GEOGRÁFICA ENTRE COORDENADAS
# ============================================================

def distancia_geografica_m(lat1, lng1, lat2, lng2):

    raio_terra = 6371000

    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(delta_lng / 2) ** 2
    )

    return 2 * raio_terra * atan2(
        sqrt(a),
        sqrt(1 - a),
    )


# ============================================================
# VALIDAÇÃO DE COBERTURA DO MAPA
# ============================================================

def validar_distancia_rede(
    grafo,
    no,
    lat,
    lng,
    nome,
):

    dados = grafo.nodes[no]

    distancia = distancia_geografica_m(
        lat,
        lng,
        float(dados["y"]),
        float(dados["x"]),
    )

    if distancia > DISTANCIA_MAXIMA_REDE_M:
        raise ValueError(
            f"A {nome.lower()} está fora da cobertura atual "
            f"do mapa de ruas. Distância até a rede: "
            f"{distancia:.0f} metros. "
            f"Escolha outro ponto ou aguarde a ampliação do mapa."
        )


# ============================================================
# CÁLCULO DE ROTAS COM A*
# ============================================================

def calcular_rota(
    origem_lat,
    origem_lng,
    destino_lat,
    destino_lng,
    modalidade="caminhada",
):

    # Verifica se a modalidade é suportada.
    if modalidade not in VELOCIDADES_KMH:
        raise ValueError(
            "Modalidade de transporte inválida."
        )

    # Carrega o mapa correspondente à modalidade.
    grafo = carregar_grafo(modalidade)

    # --------------------------------------------------------
    # ENCONTRAR NÓS MAIS PRÓXIMOS
    # --------------------------------------------------------

    no_origem = ox.distance.nearest_nodes(
        grafo,
        X=origem_lng,
        Y=origem_lat,
    )

    no_destino = ox.distance.nearest_nodes(
        grafo,
        X=destino_lng,
        Y=destino_lat,
    )
    if modalidade == "bicicleta":
        no_origem = str(no_origem)
        no_destino = str(no_destino)
    # --------------------------------------------------------
    # VALIDAR COBERTURA
    # --------------------------------------------------------

    validar_distancia_rede(
        grafo,
        no_origem,
        origem_lat,
        origem_lng,
        "Origem",
    )

    validar_distancia_rede(
        grafo,
        no_destino,
        destino_lat,
        destino_lng,
        "Destino",
    )

    # --------------------------------------------------------
    # CALCULAR CAMINHO COM A*
    # --------------------------------------------------------

    caminho, distancia_m = calcular_astar(
        grafo,
        no_origem,
        no_destino,
    )

    # --------------------------------------------------------
    # CONVERTER CAMINHO PARA COORDENADAS
    # --------------------------------------------------------

    coordenadas = [
        [
            float(grafo.nodes[no]["y"]),
            float(grafo.nodes[no]["x"]),
        ]
        for no in caminho
    ]

    # --------------------------------------------------------
    # ESTIMAR TEMPO DE DESLOCAMENTO
    # --------------------------------------------------------

    velocidade_kmh = VELOCIDADES_KMH[modalidade]

    tempo_min = (
        (distancia_m / 1000)
        / velocidade_kmh
        * 60
    )

    # --------------------------------------------------------
    # RETORNAR RESULTADO
    # --------------------------------------------------------

    return {
        "algoritmo": "A*",
        "modalidade": modalidade,
        "distancia_m": round(distancia_m, 2),
        "tempo_min": round(tempo_min, 1),
        "coordenadas": coordenadas,
        "experimental": modalidade == "bicicleta",
    }
