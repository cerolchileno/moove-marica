
import json
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DADOS = BASE / "data" / "onibus"

ENTRADA = DADOS / "correspondencias_ruas_ept.json"
SAIDA = DADOS / "revisao_correspondencias_ept.json"


def revisar():
    if not ENTRADA.exists():
        raise FileNotFoundError(
            "Arquivo de correspondências não encontrado. "
            "Execute comparar_ruas_ept.py primeiro."
        )

    dados = json.loads(
        ENTRADA.read_text(encoding="utf-8")
    )

    resumo = Counter()
    revisao = []
    total = 0

    for linha in dados.get("resultados", []):
        codigo = linha.get("codigo", "")
        sentido = linha.get("sentido", "")

        for item in linha.get("comparacoes", []):
            total += 1

            tipo = item.get(
                "tipo", "nao_encontrada"
            )
            resumo[tipo] += 1

            # Correspondência textual não é
            # validação geográfica.
            if tipo != "exata":
                revisao.append({
                    "codigo": codigo,
                    "sentido": sentido,
                    "texto_ept": item.get(
                        "texto_ept", ""
                    ),
                    "rua_sugerida": item.get(
                        "rua_mapa"
                    ),
                    "similaridade": item.get(
                        "similaridade", 0
                    ),
                    "status": "pendente",
                })

    resultado = {
        "mapa": dados.get("mapa_utilizado"),
        "total_comparacoes": total,
        "resumo": dict(resumo),
        "pendencias": revisao,
    }

    SAIDA.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 55)
    print("MOOVE MARICA - REVISAO DE RUAS")
    print("=" * 55)

    print("Mapa:", resultado["mapa"])
    print("Total:", total)
    print("Exatas:", resumo["exata"])
    print("Aproximadas:", resumo["aproximada"])
    print(
        "Nao encontradas:",
        resumo["nao_encontrada"]
    )
    print("Pendencias:", len(revisao))

    print("\nPrimeiras pendencias:")

    for item in revisao[:20]:
        print()
        print(
            item["codigo"],
            "-",
            item["sentido"],
        )
        print("EPT:", item["texto_ept"][:180])
        print("Sugestao:", item["rua_sugerida"])

    print("\nRelatorio salvo em:", SAIDA)


if __name__ == "__main__":
    revisar()
