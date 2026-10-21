
import json
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

ARQUIVO = (
    BASE_DIR
    / "data"
    / "onibus"
    / "itinerarios_ept.json"
)

CODIGOS_REVISAR = {
    "E24",
    "E24A",
    "E26",
    "E34",
    "E35",
    "E36",
    "E30E",
}


def main():
    with ARQUIVO.open(
        "r", encoding="utf-8"
    ) as arquivo:
        dados = json.load(arquivo)

    linhas = dados["linhas"]

    contagem = Counter(
        linha["codigo"] for linha in linhas
    )

    print("=" * 65)
    print("DIAGNOSTICO DOS ITINERARIOS EPT")
    print("=" * 65)

    print("\nCODIGOS DUPLICADOS:")

    for codigo, quantidade in contagem.items():
        if quantidade > 1:
            print(
                f"  {codigo}: {quantidade} registros"
            )

    print("\nLINHAS QUE PRECISAM DE REVISAO:")

    for indice, linha in enumerate(linhas, start=1):
        if linha["codigo"] not in CODIGOS_REVISAR:
            continue

        print("\n" + "-" * 65)
        print("Registro:", indice)
        print("Codigo:", linha["codigo"])
        print("Nome:", linha["nome"])

        itinerarios = linha.get("itinerarios", [])

        print(
            "Itinerarios reconhecidos:",
            len(itinerarios),
        )

        for itinerario in itinerarios:
            print(
                "Sentido:",
                itinerario.get("sentido"),
            )
            print(
                "Percurso:",
                itinerario.get("percurso_textual", ""),
            )

    print("\n" + "=" * 65)
    print("DIAGNOSTICO CONCLUIDO")
    print("=" * 65)


if __name__ == "__main__":
    main()
