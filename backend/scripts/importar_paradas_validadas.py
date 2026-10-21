
import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
PASTA = BASE / "data" / "onibus"

ARQUIVO_CSV = PASTA / "validacao_e01.csv"

ARQUIVO_PONTOS = (
    PASTA / "pontos_onibus_candidatos.geojson"
)

ARQUIVO_SAIDA = (
    PASTA / "paradas_linhas_validadas.json"
)

ARQUIVO_RELATORIO = (
    PASTA / "relatorio_importacao_paradas.json"
)


def normalizar(texto):
    return str(texto or "").strip().lower()


def campo_sim(texto):
    return normalizar(texto) in {
        "sim", "s", "true", "1"
    }


def carregar_pontos():
    if not ARQUIVO_PONTOS.exists():
        raise FileNotFoundError(
            f"GeoJSON não encontrado: {ARQUIVO_PONTOS}"
        )

    dados = json.loads(
        ARQUIVO_PONTOS.read_text(encoding="utf-8")
    )

    pontos = {}

    for feature in dados.get("features", []):
        propriedades = feature.get("properties") or {}
        geometria = feature.get("geometry") or {}

        identificador = propriedades.get("id")
        coordenadas = geometria.get("coordinates") or []

        if identificador is None:
            continue

        if geometria.get("type") != "Point":
            continue

        if len(coordenadas) < 2:
            continue

        pontos[str(identificador)] = {
            "id": str(identificador),
            "nome": propriedades.get("nome") or "",
            "lat": coordenadas[1],
            "lng": coordenadas[0],
        }

    return pontos


def ler_csv():
    if not ARQUIVO_CSV.exists():
        raise FileNotFoundError(
            f"CSV não encontrado: {ARQUIVO_CSV}"
        )

    with ARQUIVO_CSV.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:
        leitor = csv.DictReader(
            arquivo,
            delimiter=";",
        )

        return list(leitor)


def executar():
    pontos = carregar_pontos()
    registros = ler_csv()

    agrupados = defaultdict(list)
    avisos = []
    erros = []

    total_marcados = 0

    for numero_linha, registro in enumerate(
        registros,
        start=2,
    ):
        if not campo_sim(
            registro.get("pertence_e01")
        ):
            continue

        total_marcados += 1

        identificador = str(
            registro.get("id") or ""
        ).strip()

        sentido = normalizar(
            registro.get("sentido")
        )

        ordem_texto = str(
            registro.get("ordem") or ""
        ).strip()

        if identificador not in pontos:
            erros.append(
                f"Linha {numero_linha}: "
                f"ponto {identificador} não existe "
                "no GeoJSON."
            )
            continue

        if sentido not in {"ida", "volta"}:
            erros.append(
                f"Linha {numero_linha}: "
                "sentido deve ser ida ou volta."
            )
            continue

        try:
            ordem = int(ordem_texto)
        except ValueError:
            erros.append(
                f"Linha {numero_linha}: "
                "ordem deve ser um número inteiro."
            )
            continue

        if ordem < 1:
            erros.append(
                f"Linha {numero_linha}: "
                "ordem deve começar em 1."
            )
            continue

        agrupados[sentido].append({
            "ordem": ordem,
            "id": identificador,
        })

    linhas = []

    for sentido in ("ida", "volta"):
        itens = sorted(
            agrupados[sentido],
            key=lambda item: item["ordem"],
        )

        ordens = [
            item["ordem"]
            for item in itens
        ]

        ids = [
            item["id"]
            for item in itens
        ]

        if len(ordens) != len(set(ordens)):
            erros.append(
                f"E01 {sentido}: existem "
                "ordens duplicadas."
            )

        if len(ids) != len(set(ids)):
            avisos.append(
                f"E01 {sentido}: existem "
                "pontos repetidos. "
                "Confira se é um itinerário circular."
            )

        if itens and ordens != list(
            range(1, len(ordens) + 1)
        ):
            erros.append(
                f"E01 {sentido}: a sequência "
                "deve ser 1, 2, 3..."
            )

        if len(itens) == 1:
            erros.append(
                f"E01 {sentido}: pelo menos "
                "dois pontos são necessários."
            )

        if len(itens) >= 2:
            linhas.append({
                "codigo": "E01",
                "sentido": sentido,
                "paradas": ids,
                "validado": True,
                "fonte": "validacao_manual",
            })

    if total_marcados == 0:
        avisos.append(
            "Nenhuma parada foi marcada como "
            "pertencente à E01."
        )

    relatorio = {
        "gerado_em": datetime.now(
            timezone.utc
        ).isoformat(),
        "total_linhas_csv": len(registros),
        "total_pontos_marcados": total_marcados,
        "total_sentidos_preparados": len(linhas),
        "erros": erros,
        "avisos": avisos,
        "importacao_concluida": not erros,
    }

    PASTA.mkdir(
        parents=True,
        exist_ok=True,
    )

    ARQUIVO_RELATORIO.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    if erros:
        print(
            "Importação interrompida. "
            "Corrija os problemas encontrados:"
        )

        for erro in erros:
            print("-", erro)

        print(
            "Relatório:",
            ARQUIVO_RELATORIO,
        )

        raise SystemExit(1)

    # Não sobrescreve o arquivo existente
    # se não houver nenhuma sequência validada.
    if not linhas:
        print(
            "Nenhuma sequência completa "
            "foi validada."
        )
        print(
            "O arquivo de rotas existente "
            "foi preservado."
        )
        return

    # Preserva outras linhas já cadastradas.
    if ARQUIVO_SAIDA.exists():
        dados_anteriores = json.loads(
            ARQUIVO_SAIDA.read_text(
                encoding="utf-8"
            )
        )
    else:
        dados_anteriores = {
            "versao": 1,
            "linhas": [],
        }

    outras_linhas = [
        linha
        for linha in dados_anteriores.get(
            "linhas", []
        )
        if str(
            linha.get("codigo", "")
        ).upper() != "E01"
    ]

    saida = {
        "versao": 1,
        "fonte": "validacao_manual",
        "atualizado_em": datetime.now(
            timezone.utc
        ).isoformat(),
        "linhas": outras_linhas + linhas,
    }

    # Escrita atômica para evitar arquivo
    # incompleto em caso de interrupção.
    temporario = ARQUIVO_SAIDA.with_suffix(
        ".json.tmp"
    )

    temporario.write_text(
        json.dumps(
            saida,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporario.replace(ARQUIVO_SAIDA)

    print("Importação concluída!")
    print(
        "Pontos marcados:",
        total_marcados,
    )
    print(
        "Sentidos importados:",
        len(linhas),
    )
    print(
        "Arquivo:",
        ARQUIVO_SAIDA,
    )

    for aviso in avisos:
        print("AVISO:", aviso)


if __name__ == "__main__":
    executar()
