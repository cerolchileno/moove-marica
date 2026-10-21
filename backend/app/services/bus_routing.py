
import json
from functools import lru_cache
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

ARQUIVO_LINHAS = (
    BASE_DIR / "data" / "onibus" / "linhas.json"
)


@lru_cache(maxsize=1)
def carregar_linhas_onibus():
    """
    Carrega as linhas cadastradas dos Vermelhinhos.
    Não modifica os serviços de caminhada ou bicicleta.
    """

    if not ARQUIVO_LINHAS.exists():
        raise FileNotFoundError(
            f"Arquivo de linhas não encontrado: {ARQUIVO_LINHAS}"
        )

    with open(ARQUIVO_LINHAS, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, dict):
        raise ValueError(
            "O cadastro de ônibus deve ser um objeto JSON."
        )

    linhas = dados.get("linhas")

    if not isinstance(linhas, list):
        raise ValueError(
            "O campo 'linhas' deve ser uma lista."
        )

    return linhas


def listar_linhas_onibus():
    """
    Retorna as linhas cadastradas, sem alterar seus dados.
    """

    return carregar_linhas_onibus()


def buscar_linha_onibus(codigo):
    """
    Busca uma linha pelo código.
    """

    for linha in carregar_linhas_onibus():
        if linha.get("codigo") == codigo:
            return linha

    return None
