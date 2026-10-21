
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

ARQUIVO_LINHAS = (
    BASE_DIR / "data" / "onibus" / "linhas.json"
)


def validar_linhas():
    if not ARQUIVO_LINHAS.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {ARQUIVO_LINHAS}"
        )

    with open(ARQUIVO_LINHAS, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    campos_obrigatorios = [
        "sistema",
        "municipio",
        "operadora",
        "tarifa",
        "linhas",
    ]

    for campo in campos_obrigatorios:
        if campo not in dados:
            raise ValueError(
                f"Campo obrigatório ausente: {campo}"
            )

    if not isinstance(dados["linhas"], list):
        raise ValueError(
            "O campo 'linhas' deve ser uma lista."
        )

    codigos = set()

    for linha in dados["linhas"]:
        if not isinstance(linha, dict):
            raise ValueError(
                "Cada linha deve ser um objeto JSON."
            )

        for campo in ["codigo", "nome", "itinerarios"]:
            if campo not in linha:
                raise ValueError(
                    f"Linha com campo ausente: {campo}"
                )

        codigo = linha["codigo"]

        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError(
                "O código da linha deve ser um texto não vazio."
            )

        if codigo in codigos:
            raise ValueError(
                f"Código de linha duplicado: {codigo}"
            )

        codigos.add(codigo)

        if not isinstance(linha["itinerarios"], list):
            raise ValueError(
                f"Os itinerários da linha {codigo} devem ser uma lista."
            )

    print("Arquivo JSON válido!")
    print(f"Linhas cadastradas: {len(dados['linhas'])}")


if __name__ == "__main__":
    validar_linhas()
