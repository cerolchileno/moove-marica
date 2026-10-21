
from functools import lru_cache
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Região aproximada do município de Maricá.
# A busca continua sendo validada pelo nome do município.
VIEWBOX = "-42.98,-22.82,-42.65,-23.10"


@lru_cache(maxsize=200)
def buscar_enderecos(termo: str):
    termo = termo.strip()

    if len(termo) < 3:
        return []

    parametros = {
        "q": f"{termo}, Maricá, Rio de Janeiro, Brasil",
        "format": "jsonv2",
        "limit": 5,
        "addressdetails": 1,
        "countrycodes": "br",
    }

    url = f"{NOMINATIM_URL}?{urlencode(parametros)}"

    requisicao = Request(
        url,
        headers={
            "User-Agent": "MooveMaricaHackathon/0.1 (prototipo educacional)",
            "Accept": "application/json",
        },
    )

    with urlopen(requisicao, timeout=10) as resposta:
        dados = json.load(resposta)

    resultados = []

    for item in dados:
        endereco = item.get("address", {})

        cidade = (
            endereco.get("city")
            or endereco.get("town")
            or endereco.get("municipality")
        )

        if cidade and cidade.lower() not in ("maricá", "marica"):
            continue

        resultados.append({
            "nome": item["display_name"],
            "lat": float(item["lat"]),
            "lng": float(item["lon"]),
        })

    return resultados
