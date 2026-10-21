
import json
import re
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[2]

ARQUIVO = (
    BACKEND
    / "data"
    / "onibus"
    / "itinerarios_ept.json"
)


def separar_trechos(texto: str) -> list[str]:
    if not texto:
        return []

    # Divide somente separadores com espacos.
    # Preserva hifens dentro dos nomes das vias.
    partes = re.split(
        r"\s+[–—-]\s+",
        texto,
    )

    return [
        re.sub(r"\s+", " ", parte)
        .strip(" \t\r\n.;")
        for parte in partes
        if parte.strip(" \t\r\n.;")
    ]


def carregar_linhas() -> list[dict]:
    if not ARQUIVO.exists():
        raise FileNotFoundError(
            "itinerarios_ept.json nao encontrado"
        )

    dados = json.loads(
        ARQUIVO.read_text(encoding="utf-8")
    )

    linhas = dados.get("linhas")

    if not isinstance(linhas, list):
        raise ValueError(
            "Campo 'linhas' invalido no JSON da EPT"
        )

    resultado = []

    for linha in linhas:
        itinerarios = []

        for itinerario in linha.get("itinerarios", []):
            texto = itinerario.get(
                "percurso_textual", ""
            )

            itinerarios.append({
                "sentido": itinerario.get("sentido"),
                "percurso_textual": texto,
                "trechos": separar_trechos(texto),
                "validado": False,
            })

        resultado.append({
            "id": linha.get("id_registro"),
            "codigo": linha.get("codigo"),
            "nome": linha.get("nome"),
            "itinerarios": itinerarios,
            "status": "itinerario_textual",
        })

    return resultado


def listar_linhas(codigo: str | None = None):
    linhas = carregar_linhas()

    if codigo:
        linhas = [
            linha for linha in linhas
            if str(linha.get("codigo", "")).upper()
            == codigo.upper()
        ]

    return {
        "total": len(linhas),
        "linhas": linhas,
        "aviso": (
            "Itinerarios textuais da EPT. "
            "Paradas e horarios nao validados."
        ),
    }
