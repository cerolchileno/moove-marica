
import json
import re
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "onibus"

ENTRADA = DATA_DIR / "itinerarios_ept.json"
SAIDA = DATA_DIR / "rede_onibus_preparada.json"
RELATORIO = DATA_DIR / "relatorio_rede_onibus.json"


def limpar(texto):
    return re.sub(r"\s+", " ", texto).strip()


def separar_trechos(texto):
    """
    Segmentação textual preliminar.

    Não representa paradas reais e não deve
    ser utilizada como geometria de ônibus.
    """
    partes = re.split(
        r"\s*(?:→|➜|;)\s*",
        texto,
    )

    return [
        limpar(parte)
        for parte in partes
        if limpar(parte)
    ]


def preparar():
    if not ENTRADA.exists():
        raise FileNotFoundError(
            "Execute primeiro importar_itinerarios_ept.py"
        )

    dados = json.loads(
        ENTRADA.read_text(encoding="utf-8")
    )

    linhas = dados.get("linhas", [])

    rede = []
    revisao = []
    codigos = Counter()

    for indice, linha in enumerate(linhas, start=1):
        codigo = linha.get("codigo", "")
        codigos[codigo] += 1

        itinerarios = linha.get("itinerarios", [])

        if not itinerarios:
            revisao.append({
                "codigo": codigo,
                "nome": linha.get("nome", ""),
                "motivo": "Sem percurso estruturado",
                "texto_original": linha.get(
                    "texto_original", ""
                ),
            })
            continue

        for numero, itinerario in enumerate(
            itinerarios, start=1
        ):
            texto = itinerario.get(
                "percurso_textual", ""
            )

            trechos = separar_trechos(texto)

            registro = {
                "id": (
                    f"{codigo}_{indice}_{numero}"
                ),
                "codigo": codigo,
                "nome": linha.get("nome", ""),
                "sentido": itinerario.get(
                    "sentido", "indefinido"
                ),
                "percurso_textual": texto,
                "trechos_textuais": trechos,
                "geometria": None,
                "paradas": [],
                "validado": False,
                "fonte": linha.get(
                    "fonte", dados.get("fonte", "")
                ),
            }

            rede.append(registro)

    resultado = {
        "sistema": "Vermelhinhos",
        "municipio": "Maricá",
        "tipo": "rede_textual_preliminar",
        "itinerarios": rede,
    }

    resumo = {
        "registros_origem": len(linhas),
        "codigos_unicos": len(codigos),
        "itinerarios_preparados": len(rede),
        "registros_para_revisao": len(revisao),
        "revisao": revisao,
    }

    SAIDA.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    RELATORIO.write_text(
        json.dumps(
            resumo,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 55)
    print("MOOVE MARICA - REDE DE ONIBUS")
    print("=" * 55)

    print("Registros originais:", len(linhas))
    print("Codigos unicos:", len(codigos))
    print("Itinerarios preparados:", len(rede))
    print("Registros para revisao:", len(revisao))

    print("\nArquivos criados:")
    print(SAIDA)
    print(RELATORIO)

    if revisao:
        print("\nLinhas para revisao:")
        for item in revisao:
            print(
                "-",
                item["codigo"],
                item["motivo"],
            )


if __name__ == "__main__":
    preparar()
