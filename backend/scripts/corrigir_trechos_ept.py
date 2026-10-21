
import json
import re
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
PASTA = BASE / "data" / "onibus"

ENTRADA = PASTA / "rede_onibus_preparada.json"

SAIDA_REDE = (
    PASTA / "rede_onibus_corrigida.json"
)

SAIDA_RUAS = (
    PASTA / "ruas_itinerarios_ept_corrigidas.json"
)

PREFIXOS_VIA = re.compile(
    r"^(?:"
    r"RUA|R\.|AVENIDA|AV\.|ESTRADA|"
    r"RODOVIA|RJ\s*[- ]?\s*\d+|"
    r"TRAVESSA|ALAMEDA|PRAÇA|"
    r"PRACA|LARGO"
    r")\b",
    re.IGNORECASE,
)


def separar_trechos(texto):
    if not texto:
        return []

    # A EPT utiliza travessoes para separar
    # as ruas e os pontos de referencia.
    #
    # Nao dividimos em hifens simples,
    # pois nomes como SAMPAIO CORREIA-JACONE
    # devem permanecer juntos.

    partes = re.split(
        r"\s+[–—]\s+|\s+[-]\s+",
        texto,
    )

    resultado = []

    for parte in partes:
        parte = re.sub(
            r"\s+",
            " ",
            parte,
        ).strip(" \t\r\n.;")

        if parte:
            resultado.append(parte)

    return resultado


def identificar_vias(trechos):
    vias = []
    referencias = []

    for trecho in trechos:
        if PREFIXOS_VIA.match(trecho):
            vias.append(trecho)
        else:
            referencias.append(trecho)

    return vias, referencias


def corrigir():
    if not ENTRADA.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {ENTRADA}"
        )

    dados = json.loads(
        ENTRADA.read_text(encoding="utf-8")
    )

    itinerarios = dados.get("itinerarios", [])

    rede_corrigida = []
    ruas_corrigidas = []

    total_trechos = 0
    total_vias = 0

    for itinerario in itinerarios:
        texto = itinerario.get(
            "percurso_textual", ""
        )

        trechos = separar_trechos(texto)

        vias, referencias = identificar_vias(
            trechos
        )

        registro = dict(itinerario)

        registro["trechos_textuais"] = trechos
        registro["vias_candidatas"] = vias
        registro["referencias_textuais"] = referencias

        # Nao inventamos geometria ou paradas.
        registro["geometria"] = None
        registro["paradas"] = []
        registro["validado"] = False

        rede_corrigida.append(registro)

        ruas_corrigidas.append({
            "id": itinerario.get("id"),
            "codigo": itinerario.get("codigo"),
            "nome": itinerario.get("nome"),
            "sentido": itinerario.get("sentido"),
            "ruas_candidatas": vias,
            "referencias_textuais": referencias,
            "quantidade_ruas": len(vias),
            "status": "pendente_validacao",
        })

        total_trechos += len(trechos)
        total_vias += len(vias)

    resultado_rede = {
        "sistema": dados.get("sistema"),
        "municipio": dados.get("municipio"),
        "tipo": "rede_textual_corrigida",
        "gerado_em_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "itinerarios": rede_corrigida,
    }

    resultado_ruas = {
        "fonte": str(ENTRADA.name),
        "tipo": "vias_candidatas_extraidas",
        "itinerarios": ruas_corrigidas,
    }

    SAIDA_REDE.write_text(
        json.dumps(
            resultado_rede,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    SAIDA_RUAS.write_text(
        json.dumps(
            resultado_ruas,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nCORRECAO CONCLUIDA")
    print("=" * 50)
    print("Itinerarios:", len(rede_corrigida))
    print("Trechos identificados:", total_trechos)
    print("Vias candidatas:", total_vias)

    print("\nEXEMPLO - E01 IDA")

    exemplo = next(
        (
            item
            for item in rede_corrigida
            if item.get("codigo") == "E01"
            and item.get("sentido") == "ida"
        ),
        None,
    )

    if exemplo:
        for numero, trecho in enumerate(
            exemplo["trechos_textuais"],
            start=1,
        ):
            print(f"{numero}. {trecho}")

    print("\nArquivos gerados:")
    print(SAIDA_REDE)
    print(SAIDA_RUAS)


if __name__ == "__main__":
    corrigir()
