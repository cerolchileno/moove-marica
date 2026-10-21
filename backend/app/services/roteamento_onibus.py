
import json
import math
from pathlib import Path

from app.services.linhas_ept import carregar_linhas


BACKEND = Path(__file__).resolve().parents[2]

ARQUIVO_PONTOS = (
    BACKEND
    / "data"
    / "onibus"
    / "pontos_onibus_candidatos.geojson"
)

RAIO_MAXIMO_METROS = 1500


def distancia_metros(lat1, lon1, lat2, lon2):
    """Distancia aproximada em linha reta (Haversine)."""
    raio_terra = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(delta_lon / 2) ** 2
    )

    return (
        2
        * raio_terra
        * math.atan2(
            math.sqrt(a),
            math.sqrt(max(0, 1 - a)),
        )
    )


def carregar_pontos():
    if not ARQUIVO_PONTOS.exists():
        raise FileNotFoundError(
            "Arquivo de pontos candidatos nao encontrado"
        )

    dados = json.loads(
        ARQUIVO_PONTOS.read_text(encoding="utf-8")
    )

    pontos = []

    for feature in dados.get("features", []):
        geometria = feature.get("geometry") or {}

        if geometria.get("type") != "Point":
            continue

        coordenadas = geometria.get("coordinates", [])

        if len(coordenadas) < 2:
            continue

        lon, lat = coordenadas[:2]

        if not all(
            isinstance(valor, (int, float))
            for valor in (lat, lon)
        ):
            continue

        propriedades = feature.get("properties") or {}

        pontos.append({
            "id": propriedades.get("id"),
            "nome": propriedades.get("nome"),
            "lat": lat,
            "lng": lon,
            "status": "candidato_nao_validado",
        })

    return pontos


def encontrar_pontos_proximos(lat, lng, pontos, limite=5):
    encontrados = []

    for ponto in pontos:
        distancia = distancia_metros(
            lat,
            lng,
            ponto["lat"],
            ponto["lng"],
        )

        if distancia <= RAIO_MAXIMO_METROS:
            encontrados.append({
                **ponto,
                "distancia_reta_m": round(distancia, 1),
            })

    encontrados.sort(
        key=lambda item: item["distancia_reta_m"]
    )

    return encontrados[:limite]


def planejar_onibus(
    origem_lat,
    origem_lng,
    destino_lat,
    destino_lng,
    codigo_linha="E01",
):
    linhas = carregar_linhas()

    linhas_encontradas = [
        linha
        for linha in linhas
        if linha.get("codigo") == codigo_linha
    ]

    if not linhas_encontradas:
        raise ValueError(
            f"Linha {codigo_linha} nao encontrada"
        )

    pontos = carregar_pontos()

    embarques = encontrar_pontos_proximos(
        origem_lat,
        origem_lng,
        pontos,
    )

    desembarques = encontrar_pontos_proximos(
        destino_lat,
        destino_lng,
        pontos,
    )

    return {
        "modalidade": "onibus",
        "linha_consultada": codigo_linha,
        "status": "analise_preliminar",
        "rota_confirmada": False,
        "embarques_candidatos": embarques,
        "desembarques_candidatos": desembarques,
        "itinerarios_disponiveis": [
            {
                "id": linha.get("id"),
                "nome": linha.get("nome"),
                "sentidos": [
                    item.get("sentido")
                    for item in linha.get("itinerarios", [])
                ],
            }
            for linha in linhas_encontradas
        ],
        "aviso": (
            "Os pontos apresentados foram encontrados "
            "por proximidade geografica. Ainda nao ha "
            "confirmacao de que pertencem a esta linha. "
            "As distancias sao em linha reta, nao "
            "percursos de caminhada."
        ),
    }
