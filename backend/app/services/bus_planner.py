
import csv
import heapq
from datetime import datetime, timedelta
from functools import lru_cache
from math import radians, sin, cos, asin, sqrt
from pathlib import Path

from app.services.routing import calcular_rota


BASE_DIR = Path(__file__).resolve().parents[2]
GTFS_DIR = BASE_DIR / "data" / "onibus" / "gtfs"

MAX_CAMINHADA_M = 1000
MAX_BALDEACOES = 1
TEMPO_BALDEACAO_MIN = 5


def distancia_m(lat1, lon1, lat2, lon2):
    raio = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    return 2 * raio * asin(min(1, sqrt(a)))


def ler_csv(nome, obrigatorio=True):
    caminho = GTFS_DIR / nome

    if not caminho.exists():
        if obrigatorio:
            raise FileNotFoundError(
                f"Arquivo GTFS ausente: {nome}. "
                "É necessário importar dados reais da EPT."
            )
        return []

    with caminho.open(
        "r", encoding="utf-8-sig", newline=""
    ) as arquivo:
        return list(csv.DictReader(arquivo))


def minutos_gtfs(valor):
    partes = valor.split(":")
    return (
        int(partes[0]) * 60
        + int(partes[1])
        + int(partes[2]) / 60
    )


@lru_cache(maxsize=1)
def carregar_rede():
    paradas = {}
    for item in ler_csv("stops.txt"):
        paradas[item["stop_id"]] = {
            "id": item["stop_id"],
            "nome": item["stop_name"],
            "lat": float(item["stop_lat"]),
            "lon": float(item["stop_lon"]),
        }

    linhas = {
        item["route_id"]: item
        for item in ler_csv("routes.txt")
    }

    viagens = {
        item["trip_id"]: item
        for item in ler_csv("trips.txt")
    }

    sequencias = {}

    for item in ler_csv("stop_times.txt"):
        trip_id = item["trip_id"]
        sequencias.setdefault(trip_id, []).append(item)

    for itens in sequencias.values():
        itens.sort(key=lambda x: int(x["stop_sequence"]))

    calendario = {
        item["service_id"]: item
        for item in ler_csv("calendar.txt", obrigatorio=False)
    }

    excecoes = ler_csv(
        "calendar_dates.txt", obrigatorio=False
    )

    if not calendario and not excecoes:
        raise ValueError(
            "GTFS sem calendário de operação verificável."
        )

    return paradas, linhas, viagens, sequencias, calendario, excecoes


def servico_ativo(service_id, data, calendario, excecoes):
    data_str = data.strftime("%Y%m%d")
    ativo = False

    registro = calendario.get(service_id)

    if registro:
        dia = data.strftime("%A").lower()

        ativo = (
            registro["start_date"] <= data_str
            <= registro["end_date"]
            and registro.get(dia) == "1"
        )

    for excecao in excecoes:
        if (
            excecao["service_id"] == service_id
            and excecao["date"] == data_str
        ):
            ativo = excecao["exception_type"] == "1"

    return ativo


def paradas_proximas(paradas, lat, lon):
    candidatas = []

    for parada in paradas.values():
        distancia = distancia_m(
            lat, lon, parada["lat"], parada["lon"]
        )

        if distancia <= MAX_CAMINHADA_M:
            candidatas.append((distancia, parada))

    return sorted(candidatas, key=lambda x: x[0])


def trecho_caminhada(lat1, lon1, lat2, lon2):
    try:
        return calcular_rota(
            lat1, lon1, lat2, lon2,
            modalidade="caminhada",
        )
    except (ValueError, KeyError):
        return None


def planejar_onibus(
    origem_lat,
    origem_lng,
    destino_lat,
    destino_lng,
    data_hora=None,
):
    if data_hora is None:
        data_hora = datetime.now()

    (
        paradas,
        linhas,
        viagens,
        sequencias,
        calendario,
        excecoes,
    ) = carregar_rede()

    origens = paradas_proximas(
        paradas, origem_lat, origem_lng
    )
    destinos = paradas_proximas(
        paradas, destino_lat, destino_lng
    )

    if not origens or not destinos:
        raise ValueError(
            "Não existem paradas cadastradas suficientemente "
            "próximas da origem ou do destino."
        )

    acessos = {}
    saidas = {}

    for _, parada in origens[:12]:
        rota = trecho_caminhada(
            origem_lat, origem_lng,
            parada["lat"], parada["lon"],
        )
        if rota:
            acessos[parada["id"]] = rota

    for _, parada in destinos[:12]:
        rota = trecho_caminhada(
            parada["lat"], parada["lon"],
            destino_lat, destino_lng,
        )
        if rota:
            saidas[parada["id"]] = rota

    if not acessos or not saidas:
        raise ValueError(
            "Não foi possível conectar os pontos escolhidos "
            "às paradas pela rede de caminhada."
        )

    data = data_hora.date()
    inicio_min = (
        data_hora.hour * 60
        + data_hora.minute
        + data_hora.second / 60
    )

    # Constrói conexões cronológicas de viagens ativas.
    conexoes = []

    for trip_id, viagem in viagens.items():
        if not servico_ativo(
            viagem["service_id"],
            data,
            calendario,
            excecoes,
        ):
            continue

        sequencia = sequencias.get(trip_id, [])

        for anterior, seguinte in zip(
            sequencia, sequencia[1:]
        ):
            origem_id = anterior["stop_id"]
            destino_id = seguinte["stop_id"]

            if origem_id not in paradas or destino_id not in paradas:
                continue

            partida = minutos_gtfs(
                anterior["departure_time"]
            )
            chegada = minutos_gtfs(
                seguinte["arrival_time"]
            )

            if chegada < partida:
                continue

            conexoes.append({
                "origem": origem_id,
                "destino": destino_id,
                "partida": partida,
                "chegada": chegada,
                "trip_id": trip_id,
                "route_id": viagem["route_id"],
            })

    conexoes.sort(key=lambda x: x["partida"])

    # Estado: parada, viagem atual e quantidade de embarques.
    melhores = {}
    anteriores = {}
    fila = []

    for parada_id, rota in acessos.items():
        chegada = inicio_min + rota["tempo_min"]
        estado = (parada_id, None, 0)
        melhores[estado] = chegada
        anteriores[estado] = (
            None,
            {"tipo": "caminhada", "rota": rota},
        )
        heapq.heappush(fila, (chegada, estado))

    # Índice das conexões por parada.
    por_parada = {}

    for conexao in conexoes:
        por_parada.setdefault(
            conexao["origem"], []
        ).append(conexao)

    melhor_final = None

    while fila:
        tempo, estado = heapq.heappop(fila)

        if tempo > melhores.get(estado, float("inf")):
            continue

        parada_id, viagem_atual, embarques = estado

        if parada_id in saidas and embarques > 0:
            final = tempo + saidas[parada_id]["tempo_min"]

            if (
                melhor_final is None
                or final < melhor_final[0]
            ):
                melhor_final = (
                    final, estado, saidas[parada_id]
                )

        if melhor_final and tempo >= melhor_final[0]:
            continue

        for conexao in por_parada.get(parada_id, []):
            mesma_viagem = (
                viagem_atual == conexao["trip_id"]
            )

            novos_embarques = (
                embarques
                if mesma_viagem
                else embarques + 1
            )

            if novos_embarques > MAX_BALDEACOES + 1:
                continue

            margem = (
                0
                if mesma_viagem or embarques == 0
                else TEMPO_BALDEACAO_MIN
            )

            if conexao["partida"] < tempo + margem:
                continue

            novo_estado = (
                conexao["destino"],
                conexao["trip_id"],
                novos_embarques,
            )

            chegada = conexao["chegada"]

            if chegada < melhores.get(
                novo_estado, float("inf")
            ):
                melhores[novo_estado] = chegada
                anteriores[novo_estado] = (
                    estado,
                    {"tipo": "onibus", **conexao},
                )
                heapq.heappush(
                    fila, (chegada, novo_estado)
                )

    if melhor_final is None:
        raise ValueError(
            "Nenhuma viagem de ônibus encontrada para "
            "a data e o horário informados."
        )

    tempo_final, estado, caminhada_final = melhor_final
    etapas = [{
        "tipo": "caminhada",
        "rota": caminhada_final,
    }]

    while estado is not None:
        anterior, etapa = anteriores[estado]
        etapas.append(etapa)
        estado = anterior

    etapas.reverse()

    # Agrupa conexões consecutivas da mesma viagem.
    agrupadas = []

    for etapa in etapas:
        if (
            etapa["tipo"] == "onibus"
            and agrupadas
            and agrupadas[-1]["tipo"] == "onibus"
            and agrupadas[-1]["trip_id"] == etapa["trip_id"]
        ):
            agrupadas[-1]["destino"] = etapa["destino"]
            agrupadas[-1]["chegada"] = etapa["chegada"]
        else:
            agrupadas.append(dict(etapa))

    for etapa in agrupadas:
        if etapa["tipo"] == "onibus":
            linha = linhas.get(etapa["route_id"], {})
            etapa["linha"] = (
                linha.get("route_short_name")
                or etapa["route_id"]
            )
            etapa["embarque"] = paradas[etapa["origem"]]
            etapa["desembarque"] = paradas[etapa["destino"]]

    return {
        "modalidade": "onibus",
        "tarifa": 0,
        "tempo_total_min": round(
            tempo_final - inicio_min, 1
        ),
        "baldeacoes": max(
            0,
            sum(
                etapa["tipo"] == "onibus"
                for etapa in agrupadas
            ) - 1
        ),
        "etapas": agrupadas,
        "fonte_dados": "GTFS importado",
    }
