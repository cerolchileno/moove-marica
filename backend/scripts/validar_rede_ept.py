
import json
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
PASTA = BASE / "data" / "onibus"

ENTRADA = PASTA / "rede_onibus_corrigida.json"
SAIDA = PASTA / "validacao_rede_ept.json"


def validar():
    if not ENTRADA.exists():
        print("Arquivo corrigido nao encontrado.")
        print("Execute corrigir_trechos_ept.py primeiro.")
        return 1

    dados = json.loads(
        ENTRADA.read_text(encoding="utf-8")
    )

    itinerarios = dados.get("itinerarios", [])

    problemas = []
    estatisticas = Counter()
    registros = []

    for item in itinerarios:
        codigo = item.get("codigo", "SEM_CODIGO")
        sentido = item.get("sentido", "desconhecido")
        identificador = item.get("id", "")

        texto = item.get("percurso_textual", "")
        trechos = item.get("trechos_textuais", [])
        vias = item.get("vias_candidatas", [])

        alertas = []

        if not texto.strip():
            alertas.append("Sem percurso textual")

        if not trechos:
            alertas.append("Sem trechos identificados")

        if texto.strip() and len(trechos) == 1:
            alertas.append(
                "Itinerario nao foi dividido em varios trechos"
            )

        if not vias:
            alertas.append("Nenhuma via candidata identificada")

        if alertas:
            problemas.append({
                "id": identificador,
                "codigo": codigo,
                "sentido": sentido,
                "alertas": alertas,
            })

        estatisticas["itinerarios"] += 1
        estatisticas["trechos"] += len(trechos)
        estatisticas["vias"] += len(vias)

        registros.append({
            "id": identificador,
            "codigo": codigo,
            "sentido": sentido,
            "quantidade_trechos": len(trechos),
            "quantidade_vias": len(vias),
            "alertas": alertas,
        })

    resultado = {
        "total_itinerarios": estatisticas["itinerarios"],
        "total_trechos": estatisticas["trechos"],
        "total_vias_candidatas": estatisticas["vias"],
        "itinerarios_com_alertas": len(problemas),
        "problemas": problemas,
        "registros": registros,
    }

    SAIDA.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nVALIDACAO DA REDE EPT")
    print("=" * 50)
    print("Itinerarios:", resultado["total_itinerarios"])
    print("Trechos:", resultado["total_trechos"])
    print("Vias candidatas:", resultado["total_vias_candidatas"])
    print("Itinerarios com alertas:", len(problemas))

    print("\nEXEMPLO E01 IDA")

    e01 = next(
        (
            item for item in itinerarios
            if item.get("codigo") == "E01"
            and item.get("sentido") == "ida"
        ),
        None,
    )

    if e01:
        for numero, trecho in enumerate(
            e01.get("trechos_textuais", []),
            start=1,
        ):
            print(f"{numero}. {trecho}")

    if problemas:
        print("\nPRIMEIROS ALERTAS:")

        for problema in problemas[:10]:
            print(
                problema["codigo"],
                problema["sentido"],
                "->",
                ", ".join(problema["alertas"]),
            )

    print("\nRelatorio:", SAIDA)
    return 0


if __name__ == "__main__":
    raise SystemExit(validar())
