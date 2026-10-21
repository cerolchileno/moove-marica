import json
import math
from pathlib import Path


BASE = Path(__file__).resolve().parents[2]
PASTA = BASE / "data" / "onibus"

ARQUIVO_PONTOS = (
    PASTA / "pontos_onibus_candidatos.geojson"
)

ARQUIVO_LINHAS = (
    PASTA / "paradas_linhas_validadas.json"
)

RAIO_BUSCA_M = 1500
VELOCIDADE_CAMINHADA_M_MIN = 75
VELOCIDADE_ONIBUS_M_MIN = 300


def haversine(lat1, lng1, lat2, lng2):
    raio = 6371000

    a1 = math.radians(lat1)
    a2 = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(a1)
        * math.cos(a2)
        * math.sin(dlng / 2) ** 2
    )

    return 2 * raio * math.atan2(
        math.sqrt(a),
        math.sqrt(max(0, 1 - a)),
    )


def carregar_json(caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {caminho}"
        )

    return json.loads(
        caminho.read_text(encoding="utf-8")
    )


def carregar_pontos():
    dados = carregar_json(ARQUIVO_PONTOS)

    resultado = {}

    for feature in dados.get("features", []):
        geometria = feature.get("geometry") or {}
        propriedades = feature.get("properties") or {}

        if geometria.get("type") != "Point":
            continue

        coordenadas = geometria.get("coordinates") or []

        if len(coordenadas) < 2:
            continue

        lng, lat = coordenadas[:2]
        identificador = propriedades.get("id")

        if identificador is None:
            continue

        try:
            lat = float(lat)
            lng = float(lng)
        except (ValueError, TypeError):
            continue

        if not (
            -90 <= lat <= 90
            and -180 <= lng <= 180
        ):
            continue

        resultado[str(identificador)] = {
            "id": str(identificador),
            "nome": propriedades.get("nome")
                or "Ponto sem nome",
            "lat": lat,
            "lng": lng,
        }

    return resultado


def normalizar_paradas(registro, pontos):
    ids = registro.get("paradas", [])

    if not isinstance(ids, list):
        return []

    resultado = []

    for identificador in ids:
        ponto = pontos.get(str(identificador))

        if ponto:
            resultado.append(ponto)

    return resultado


def calcular_opcoes(
    origem_lat,
    origem_lng,
    destino_lat,
    destino_lng,
    codigo_linha=None,
):
    pontos = carregar_pontos()

    configuracao = carregar_json(ARQUIVO_LINHAS)
    linhas = configuracao.get("linhas", [])

    opcoes = []
    registros_considerados = 0

    for registro in linhas:
        codigo = str(
            registro.get("codigo", "")
        ).upper()

        if codigo_linha and codigo != codigo_linha.upper():
            continue

        if registro.get("validado") is not True:
            continue

        paradas = normalizar_paradas(
            registro,
            pontos,
        )

        if len(paradas) < 2:
            continue

        registros_considerados += 1

        distancias_origem = [
            haversine(
                origem_lat,
                origem_lng,
                parada["lat"],
                parada["lng"],
            )
            for parada in paradas
        ]

        distancias_destino = [
            haversine(
                destino_lat,
                destino_lng,
                parada["lat"],
                parada["lng"],
            )
            for parada in paradas
        ]

        # Comprimento aproximado entre paradas
        # consecutivas na sequencia validada.
        segmentos = []

        for indice in range(len(paradas) - 1):
            a = paradas[indice]
            b = paradas[indice + 1]

            segmentos.append(
                haversine(
                    a["lat"],
                    a["lng"],
                    b["lat"],
                    b["lng"],
                )
            )

        acumuladas = [0.0]

        for distancia in segmentos:
            acumuladas.append(
                acumuladas[-1] + distancia
            )

        for i, distancia_embarque in enumerate(
            distancias_origem
        ):
            if distancia_embarque > RAIO_BUSCA_M:
                continue

            for j in range(i + 1, len(paradas)):
                distancia_desembarque = (
                    distancias_destino[j]
                )

                if distancia_desembarque > RAIO_BUSCA_M:
                    continue

                distancia_onibus = (
                    acumuladas[j] - acumuladas[i]
                )

                tempo_caminhada = (
                    distancia_embarque
                    + distancia_desembarque
                ) / VELOCIDADE_CAMINHADA_M_MIN

                tempo_onibus = (
                    distancia_onibus
                    / VELOCIDADE_ONIBUS_M_MIN
                )

                tempo_estimado = (
                    tempo_caminhada + tempo_onibus
                )

                opcoes.append({
                    "codigo": codigo,
                    "sentido": registro.get("sentido"),
                    "embarque": paradas[i],
                    "desembarque": paradas[j],
                    "paradas_intermediarias": (
                        paradas[i + 1:j]
                    ),
                    "distancia_caminhada_reta_m": round(
                        distancia_embarque
                        + distancia_desembarque,
                        1,
                    ),
                    "distancia_onibus_aproximada_m": round(
                        distancia_onibus,
                        1,
                    ),
                    "tempo_estimado_sem_espera_min": round(
                        tempo_estimado,
                        1,
                    ),
                    "coordenadas": [
                        [p["lat"], p["lng"]]
                        for p in paradas[i:j + 1]
                    ],
                    "experimental": True,
                })

    opcoes.sort(
        key=lambda item: (
            item["tempo_estimado_sem_espera_min"],
            item["distancia_caminhada_reta_m"],
        )
    )

    return {
        "modalidade": "onibus",
        "status": (
            "opcoes_experimentais"
            if opcoes
            else "sem_rota_validada"
        ),
        "rota_confirmada": False,
        "registros_de_linhas_validadas": (
            registros_considerados
        ),
        "total_opcoes": len(opcoes),
        "melhor_opcao": (
            opcoes[0] if opcoes else None
        ),
        "opcoes": opcoes[:10],
        "criterio": (
            "Menor tempo estimado sem espera, "
            "usando distancias em linha reta."
        ),
        "aviso": (
            "Nao representa horarios reais nem "
            "garante o trajeto viario. "
            "Apenas registros marcados como "
            "validados sao utilizados."
        ),
    }