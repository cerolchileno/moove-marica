
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "onibus"

DATA_DIR.mkdir(parents=True, exist_ok=True)

URL_EPT = (
    "https://www.eptmarica.rj.gov.br/"
    "index.php/vermelhinhos/itinerarios"
)

SAIDA = DATA_DIR / "itinerarios_ept.json"
RELATORIO = DATA_DIR / "relatorio_importacao_ept.json"

PADRAO_LINHA = re.compile(
    r"^\s*(E\d{2,3}[A-Z]?)\s*[-–—]\s*(.+)$",
    re.IGNORECASE,
)

PADRAO_SENTIDO = re.compile(
    r"\b(IDA|VOLTA)\s*:",
    re.IGNORECASE,
)


def limpar(texto):
    return re.sub(r"\s+", " ", texto).strip()


def obter_blocos(html):
    soup = BeautifulSoup(html, "html.parser")

    for elemento in soup(
        ["script", "style", "nav", "footer", "header"]
    ):
        elemento.decompose()

    principal = (
        soup.select_one("main")
        or soup.select_one("article")
        or soup.body
        or soup
    )

    linhas_texto = [
        limpar(texto)
        for texto in principal.get_text(
            separator="\n"
        ).splitlines()
        if limpar(texto)
    ]

    blocos = []
    atual = None

    for texto in linhas_texto:
        encontrado = PADRAO_LINHA.match(texto)

        if encontrado:
            if atual:
                blocos.append(atual)

            atual = {
                "codigo": encontrado.group(1).upper(),
                "nome": encontrado.group(2),
                "linhas_texto": [],
            }

        elif atual:
            atual["linhas_texto"].append(texto)

    if atual:
        blocos.append(atual)

    return blocos


def identificar_itinerarios(nome, texto):
    marcadores = list(
        PADRAO_SENTIDO.finditer(texto)
    )

    itinerarios = []

    if marcadores:
        for indice, marcador in enumerate(marcadores):
            inicio = marcador.end()

            fim = (
                marcadores[indice + 1].start()
                if indice + 1 < len(marcadores)
                else len(texto)
            )

            percurso = limpar(texto[inicio:fim])

            if percurso:
                itinerarios.append({
                    "sentido": marcador.group(1).lower(),
                    "percurso_textual": percurso,
                    "validado": False,
                })

        return itinerarios, "sentidos_identificados"

    if re.search(
        r"\bCIRCULAR\b",
        nome + " " + texto,
        re.IGNORECASE,
    ):
        return [{
            "sentido": "circular",
            "percurso_textual": texto,
            "validado": False,
        }], "circular_identificado"

    return [], "revisao_manual"


def importar():
    print("Consultando a EPT...")

    resposta = requests.get(
        URL_EPT,
        headers={
            "User-Agent": "MooveMarica/1.0"
        },
        timeout=40,
    )

    resposta.raise_for_status()

    blocos = obter_blocos(resposta.text)

    if not blocos:
        raise ValueError(
            "Nenhuma linha encontrada na página."
        )

    linhas = []
    avisos = []

    contagem = Counter(
        bloco["codigo"] for bloco in blocos
    )

    for indice, bloco in enumerate(blocos, start=1):
        texto_original = "\n".join(
            bloco["linhas_texto"]
        )

        itinerarios, status = identificar_itinerarios(
            bloco["nome"],
            limpar(texto_original),
        )

        codigo = bloco["codigo"]

        if not itinerarios:
            avisos.append(
                f"{codigo}: itinerário sem sentido identificado"
            )

        linhas.append({
            "id_registro": f"{codigo}_{indice}",
            "codigo": codigo,
            "nome": bloco["nome"],
            "itinerarios": itinerarios,
            "texto_original": texto_original,
            "status_extracao": status,
            "fonte": URL_EPT,
        })

    for codigo, quantidade in contagem.items():
        if quantidade > 1:
            avisos.append(
                f"{codigo}: {quantidade} registros "
                "com o mesmo código"
            )

    resultado = {
        "sistema": "Vermelhinhos",
        "municipio": "Maricá",
        "operadora": "EPT",
        "fonte": URL_EPT,
        "extraido_em": datetime.now(
            timezone.utc
        ).isoformat(),
        "linhas": linhas,
    }

    relatorio = {
        "registros": len(linhas),
        "codigos_unicos": len(contagem),
        "itinerarios": sum(
            len(item["itinerarios"])
            for item in linhas
        ),
        "avisos": avisos,
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
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nIMPORTACAO CONCLUIDA")
    print("Registros:", relatorio["registros"])
    print("Codigos:", relatorio["codigos_unicos"])
    print("Itinerarios:", relatorio["itinerarios"])
    print("Avisos:", len(avisos))

    for aviso in avisos:
        print("-", aviso)


if __name__ == "__main__":
    importar()
