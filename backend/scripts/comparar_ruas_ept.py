
import ast
import json
import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import networkx as nx


BASE = Path(__file__).resolve().parents[1]
PROJETO = BASE.parent
DADOS = BASE / "data" / "onibus"

ITINERARIOS = DADOS / "rede_onibus_preparada.json"
SAIDA = DADOS / "correspondencias_ruas_ept.json"


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    texto = texto.upper()
    texto = re.sub(r"[^\w\s]", " ", texto)
    return " ".join(texto.split())


def localizar_mapa():
    candidatos = list(PROJETO.rglob("*.graphml"))

    candidatos = [
        p for p in candidatos
        if "bike" not in p.name.lower()
        and "bicicleta" not in p.name.lower()
    ]

    if not candidatos:
        raise FileNotFoundError(
            "Nenhum mapa de caminhada encontrado. "
            "Confira onde está o arquivo GraphML."
        )

    preferidos = [
        p for p in candidatos
        if "walk" in p.name.lower()
        or "caminhada" in p.name.lower()
    ]

    return (preferidos or candidatos)[0]


def nomes_da_aresta(valor):
    if not valor:
        return []

    if isinstance(valor, list):
        return valor

    if isinstance(valor, str):
        try:
            convertido = ast.literal_eval(valor)
            if isinstance(convertido, list):
                return convertido
        except (ValueError, SyntaxError):
            pass

    return [str(valor)]


def extrair_ruas_mapa(grafo):
    nomes = defaultdict(set)

    for _, _, atributos in grafo.edges(data=True):
        for nome in nomes_da_aresta(
            atributos.get("name")
        ):
            nome = str(nome).strip()
            chave = normalizar(nome)

            if chave:
                nomes[chave].add(nome)

    return nomes


def comparar():
    if not ITINERARIOS.exists():
        raise FileNotFoundError(
            "Execute preparar_rede_onibus.py primeiro."
        )

    mapa = localizar_mapa()
    print("Mapa encontrado:", mapa)

    print("Carregando rede viária...")
    grafo = nx.read_graphml(mapa)

    ruas = extrair_ruas_mapa(grafo)

    print("Nomes de ruas encontrados:", len(ruas))

    dados = json.loads(
        ITINERARIOS.read_text(encoding="utf-8")
    )

    resultados = []

    for linha in dados.get("itinerarios", []):
        comparacoes = []

        for trecho in linha.get(
            "trechos_textuais", []
        ):
            chave = normalizar(trecho)

            if not chave:
                continue

            if chave in ruas:
                comparacoes.append({
                    "texto_ept": trecho,
                    "rua_mapa": sorted(ruas[chave])[0],
                    "similaridade": 1.0,
                    "tipo": "exata",
                })
                continue

            melhor = None
            pontuacao = 0.0

            for nome_normalizado in ruas:
                valor = SequenceMatcher(
                    None,
                    chave,
                    nome_normalizado,
                ).ratio()

                if valor > pontuacao:
                    pontuacao = valor
                    melhor = nome_normalizado

            comparacoes.append({
                "texto_ept": trecho,
                "rua_mapa": (
                    sorted(ruas[melhor])[0]
                    if melhor and pontuacao >= 0.80
                    else None
                ),
                "similaridade": round(
                    pontuacao, 3
                ),
                "tipo": (
                    "aproximada"
                    if pontuacao >= 0.80
                    else "nao_encontrada"
                ),
            })

        resultados.append({
            "codigo": linha["codigo"],
            "sentido": linha["sentido"],
            "comparacoes": comparacoes,
        })

    SAIDA.write_text(
        json.dumps(
            {
                "mapa_utilizado": str(mapa),
                "resultados": resultados,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nComparação concluída.")
    print("Arquivo:", SAIDA)


if __name__ == "__main__":
    comparar()
