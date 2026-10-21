
import json
import re
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DADOS = BASE / "data" / "onibus"

ENTRADA = DADOS / "rede_onibus_preparada.json"
SAIDA = DADOS / "ruas_itinerarios_ept.json"

# Reconhece nomes iniciados por tipos comuns
# de logradouro. Não é um georreferenciador.
PADRAO_RUA = re.compile(
    r"\b(?:"
    r"Rua|Avenida|Av\.?|Estrada|Rodovia|"
    r"Travessa|Alameda|Praça"
    r")\s+"
    r"[^,;→\n]+",
    re.IGNORECASE,
)


def limpar(texto):
    return " ".join(str(texto).split())


def identificar_ruas(texto):
    encontrados = PADRAO_RUA.findall(texto)

    ruas = []

    for encontrado in encontrados:
        nome = limpar(encontrado)

        if nome and nome not in ruas:
            ruas.append(nome)

    return ruas


def processar():
    if not ENTRADA.exists():
        raise FileNotFoundError(
            "Execute preparar_rede_onibus.py primeiro."
        )

    dados = json.loads(
        ENTRADA.read_text(encoding="utf-8")
    )

    resultados = []
    sem_ruas = []

    for itinerario in dados.get("itinerarios", []):
        texto = itinerario.get(
            "percurso_textual", ""
        )

        ruas = identificar_ruas(texto)

        registro = {
            "id": itinerario.get("id"),
            "codigo": itinerario.get("codigo"),
            "sentido": itinerario.get("sentido"),
            "ruas_candidatas": ruas,
            "quantidade_ruas": len(ruas),
            "status": "pendente_validacao",
        }

        resultados.append(registro)

        if not ruas:
            sem_ruas.append({
                "codigo": registro["codigo"],
                "sentido": registro["sentido"],
            })

    resultado = {
        "fonte": "itinerarios_ept",
        "tipo": "extracao_textual_preliminar",
        "itinerarios": resultados,
        "sem_ruas_reconhecidas": sem_ruas,
    }

    SAIDA.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("MOOVE MARICA - IDENTIFICACAO DE RUAS")
    print("Itinerarios:", len(resultados))
    print("Sem ruas reconhecidas:", len(sem_ruas))

    print("\nExemplos:")
    for item in resultados[:5]:
        print(
            item["codigo"],
            item["sentido"],
            item["ruas_candidatas"][:5],
        )

    print("\nArquivo criado:", SAIDA)


if __name__ == "__main__":
    processar()
